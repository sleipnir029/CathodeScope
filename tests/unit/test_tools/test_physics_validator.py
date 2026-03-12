"""Unit tests for cathodescope.tools.physics_validator.

12 tests implemented in T-14.
"""

import json
from pathlib import Path
from typing import Any

from pymatgen.core import Lattice, Structure

from cathodescope.models.material import CanonicalMaterial
from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ToolResult
from cathodescope.tools.physics_validator import validate

_FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "mp_responses"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _licoo2_structure_dict() -> dict[str, Any]:
    """Load LiCoO2 structure dict from fixture."""
    data = json.loads((_FIXTURE_DIR / "mp-22526.json").read_text(encoding="utf-8"))
    return data["structure"]  # type: ignore[return-value]


def _normalized_licoo2() -> Structure:
    """Return the conventional standard LiCoO2 structure."""
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    s = Structure.from_dict(_licoo2_structure_dict())
    return SpacegroupAnalyzer(s).get_conventional_standard_structure()


def _make_material(
    structure: Structure | None = None,
    family: str = "layered_oxide",
) -> CanonicalMaterial:
    """Build a minimal CanonicalMaterial for testing."""
    if structure is None:
        structure = _normalized_licoo2()
    prov = create_provenance(
        created_by="cathodescope",
        tool_name="test",
        tool_version="0.0.0",
    )
    return CanonicalMaterial(
        formula="LiCoO2",
        reduced_formula="LiCoO2",
        family=family,
        structure=structure.as_dict(),
        source="materials_project",
        mp_id="mp-22526",
        provenance=prov,
    )


def _good_convergence_info() -> dict[str, Any]:
    """Return a convergence_info dict representing a well-converged relaxation."""
    return {
        "converged": True,
        "steps": 10,
        "energy_history": [-10.0, -10.5, -11.0],
        "fmax_history": [0.5, 0.2, 0.01],
    }


def _good_context(material: CanonicalMaterial | None = None) -> dict[str, Any]:
    """Return a context dict that passes all checks."""
    if material is None:
        material = _make_material()
    return {
        "relaxed_structure": material.structure,
        "convergence_info": _good_convergence_info(),
    }


def _collapsed_structure_dict() -> dict[str, Any]:
    """Return a structure with atoms collapsed below the min_bond threshold."""
    # 2 Å cubic cell; Li at origin and Co at (0.02, 0.02, 0.02) Å ≈ 0.035 Å apart
    s = Structure(
        Lattice.cubic(2.0),
        ["Li", "Co", "O", "O"],
        [[0.0, 0.0, 0.0], [0.01, 0.01, 0.01], [0.5, 0.5, 0.0], [0.0, 0.5, 0.5]],
    )
    return s.as_dict()


# ---------------------------------------------------------------------------
# Test 1: Return type
# ---------------------------------------------------------------------------


def test_validator_returns_tool_result() -> None:
    """validate() returns a ToolResult."""
    material = _make_material()
    result = validate(_good_context(material), material)
    assert isinstance(result, ToolResult)


# ---------------------------------------------------------------------------
# Test 2: Evidence type
# ---------------------------------------------------------------------------


def test_validator_evidence_type_is_a_compared() -> None:
    """Physics validator sets evidence_type='A-compared'."""
    material = _make_material()
    result = validate(_good_context(material), material)
    assert result.evidence_type == "A-compared"


# ---------------------------------------------------------------------------
# Test 3: Data contains checks list
# ---------------------------------------------------------------------------


def test_validator_data_contains_checks_list() -> None:
    """ToolResult.data contains a non-empty 'checks' list."""
    material = _make_material()
    result = validate(_good_context(material), material)
    assert result.data is not None
    assert "checks" in result.data
    assert isinstance(result.data["checks"], list)
    assert len(result.data["checks"]) > 0


# ---------------------------------------------------------------------------
# Test 4: Data contains evidence_labels list
# ---------------------------------------------------------------------------


def test_validator_data_contains_evidence_labels_list() -> None:
    """ToolResult.data contains a non-empty 'evidence_labels' list."""
    material = _make_material()
    result = validate(_good_context(material), material)
    assert result.data is not None
    assert "evidence_labels" in result.data
    assert isinstance(result.data["evidence_labels"], list)
    assert len(result.data["evidence_labels"]) > 0


# ---------------------------------------------------------------------------
# Test 5: Data contains overall_sanity bool
# ---------------------------------------------------------------------------


def test_validator_data_contains_overall_sanity_bool() -> None:
    """ToolResult.data contains an 'overall_sanity' bool."""
    material = _make_material()
    result = validate(_good_context(material), material)
    assert result.data is not None
    assert "overall_sanity" in result.data
    assert isinstance(result.data["overall_sanity"], bool)


# ---------------------------------------------------------------------------
# Test 6: All checks pass for valid data
# ---------------------------------------------------------------------------


def test_validator_all_checks_pass_for_valid_data() -> None:
    """Valid structure and convergence produce overall_sanity=True with no failures."""
    material = _make_material()
    result = validate(_good_context(material), material)
    assert result.data is not None
    assert result.data["overall_sanity"] is True
    failed = [c for c in result.data["checks"] if not c["passed"]]
    assert failed == [], f"Unexpected check failures: {failed}"


# ---------------------------------------------------------------------------
# Test 7: Bond length failure
# ---------------------------------------------------------------------------


def test_validator_detects_bond_length_failure() -> None:
    """A collapsed structure produces a failed bond_lengths check."""
    material = _make_material()
    context: dict[str, Any] = {
        "relaxed_structure": _collapsed_structure_dict(),
        "convergence_info": _good_convergence_info(),
    }
    result = validate(context, material)
    assert result.data is not None
    bond_checks = [
        c for c in result.data["checks"] if c["check_name"] == "bond_lengths"
    ]
    assert bond_checks, "bond_lengths check not present in checks list"
    assert not bond_checks[0]["passed"], "bond_lengths must fail for collapsed"


# ---------------------------------------------------------------------------
# Test 8: Convergence failure
# ---------------------------------------------------------------------------


def test_validator_detects_convergence_failure() -> None:
    """Non-converged relaxation produces a failed fmax check."""
    material = _make_material()
    context: dict[str, Any] = {
        "relaxed_structure": material.structure,
        "convergence_info": {
            "converged": False,
            "steps": 500,
            "energy_history": [-10.0],
            "fmax_history": [1.5],  # 1.5 eV/Å >> 0.05 eV/Å threshold
        },
    }
    result = validate(context, material)
    assert result.data is not None
    fmax_checks = [c for c in result.data["checks"] if c["check_name"] == "fmax"]
    assert fmax_checks, "fmax check not present in checks list"
    assert not fmax_checks[0]["passed"], "fmax must fail for unconverged relaxation"


# ---------------------------------------------------------------------------
# Test 9: Symmetry break
# ---------------------------------------------------------------------------


def test_validator_detects_symmetry_break() -> None:
    """comparison_result with symmetry_preserved=False → failed symmetry check."""
    material = _make_material()
    context: dict[str, Any] = {
        "relaxed_structure": material.structure,
        "convergence_info": _good_convergence_info(),
        "comparison_result": {
            "symmetry_preserved": False,
            "reference_space_group": "R-3m",
            "relaxed_space_group": "P1",
        },
    }
    result = validate(context, material)
    assert result.data is not None
    sym_checks = [
        c for c in result.data["checks"] if c["check_name"] == "symmetry_preserved"
    ]
    assert sym_checks, "symmetry_preserved check not present in checks list"
    assert not sym_checks[0]["passed"], "symmetry check must fail for broken symmetry"


# ---------------------------------------------------------------------------
# Test 10: Warnings for soft failures
# ---------------------------------------------------------------------------


def test_validator_returns_warnings_for_soft_failures() -> None:
    """Non-monotonic energy adds a warning without affecting overall_sanity."""
    material = _make_material()
    context: dict[str, Any] = {
        "relaxed_structure": material.structure,
        "convergence_info": {
            "converged": True,
            "steps": 10,
            # Energy jumps +0.5 eV between steps 0→1 (> 0.1 eV tolerance)
            "energy_history": [-10.0, -9.5, -11.0],
            "fmax_history": [0.5, 0.2, 0.01],  # converged fmax
        },
    }
    result = validate(context, material)
    assert result.data is not None
    assert len(result.warnings) > 0, "Expected at least one warning for soft failure"
    assert result.data["overall_sanity"] is True, "Soft failure must not affect sanity"


# ---------------------------------------------------------------------------
# Test 11: Critical failure → overall_sanity=False
# ---------------------------------------------------------------------------


def test_validator_critical_failure_sets_overall_sanity_false() -> None:
    """A collapsed structure (bond_lengths failure) sets overall_sanity=False."""
    material = _make_material()
    context: dict[str, Any] = {
        "relaxed_structure": _collapsed_structure_dict(),
        "convergence_info": _good_convergence_info(),
    }
    result = validate(context, material)
    assert result.data is not None
    assert result.data["overall_sanity"] is False


# ---------------------------------------------------------------------------
# Test 12: Evidence labels match validity matrix
# ---------------------------------------------------------------------------


def test_validator_evidence_labels_match_validity_matrix() -> None:
    """Evidence label matches scientific_validity_matrix.md Row 8 for validate step."""
    material = _make_material()
    result = validate(_good_context(material), material)
    assert result.data is not None
    labels = result.data["evidence_labels"]
    assert len(labels) >= 1
    label = labels[0]
    assert label["output_name"] == "validated_structure"
    assert label["evidence_type"] == "A-compared"
    assert "Row 8" in label["rationale"]
