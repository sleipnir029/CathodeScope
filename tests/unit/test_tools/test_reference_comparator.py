"""Unit tests for cathodescope.tools.reference_comparator.

12 tests implemented in T-11.
"""

import json
from pathlib import Path

import pytest
from pymatgen.core import Lattice, Structure

from cathodescope.models.results import ToolResult
from cathodescope.tools.reference_comparator import compare

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "mp_responses"


def _licoo2_structure() -> Structure:
    """Load LiCoO2 conventional structure from fixture."""
    data = json.loads((_FIXTURE_DIR / "mp-22526.json").read_text(encoding="utf-8"))
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    s = Structure.from_dict(data["structure"])
    return SpacegroupAnalyzer(s).get_conventional_standard_structure()


def _orthorhombic(a: float = 4.0, b: float = 5.0, c: float = 6.0) -> Structure:
    """Create a single-atom orthorhombic Li structure."""
    return Structure(Lattice.orthorhombic(a, b, c), ["Li"], [[0.0, 0.0, 0.0]])


def _cubic(a: float = 4.0, species: list[str] | None = None) -> Structure:
    """Create a single-atom cubic structure."""
    sp = species if species is not None else ["Li"]
    return Structure(Lattice.cubic(a), sp, [[0.0, 0.0, 0.0]])


# ---------------------------------------------------------------------------
# Test 1: Identical structures → zero deviations
# ---------------------------------------------------------------------------


def test_compare_identical_structures_zero_deviation() -> None:
    """Comparing a structure with itself yields zero deviations everywhere."""
    structure = _licoo2_structure()
    result = compare(structure, structure)

    assert result.status == "success"
    assert result.data is not None
    devs = result.data["lattice_deviations"]
    assert devs["a"] == pytest.approx(0.0, abs=1e-10)
    assert devs["b"] == pytest.approx(0.0, abs=1e-10)
    assert devs["c"] == pytest.approx(0.0, abs=1e-10)
    assert result.data["volume_deviation"] == pytest.approx(0.0, abs=1e-10)


# ---------------------------------------------------------------------------
# Test 2: Lattice deviations a, b, c
# ---------------------------------------------------------------------------


def test_compare_lattice_deviations_a_b_c() -> None:
    """Lattice deviations for a, b, c are computed correctly."""
    reference = _orthorhombic(a=4.0, b=5.0, c=6.0)
    relaxed = _orthorhombic(a=4.0 * 1.02, b=5.0 * 1.01, c=6.0 * 1.03)

    result = compare(relaxed, reference)

    assert result.status == "success"
    assert result.data is not None
    devs = result.data["lattice_deviations"]
    assert devs["a"] == pytest.approx(2.0, abs=0.001)
    assert devs["b"] == pytest.approx(1.0, abs=0.001)
    assert devs["c"] == pytest.approx(3.0, abs=0.001)


# ---------------------------------------------------------------------------
# Test 3: Angle deviations alpha, beta, gamma
# ---------------------------------------------------------------------------


def test_compare_lattice_deviations_angles() -> None:
    """Angle deviations alpha/beta/gamma are present and zero for identical structures.
    """
    structure = _orthorhombic()  # alpha=beta=gamma=90°
    result = compare(structure, structure)

    assert result.status == "success"
    assert result.data is not None
    angle_devs = result.data["angle_deviations"]
    assert set(angle_devs.keys()) >= {"alpha", "beta", "gamma"}
    assert angle_devs["alpha"] == pytest.approx(0.0, abs=1e-10)
    assert angle_devs["beta"] == pytest.approx(0.0, abs=1e-10)
    assert angle_devs["gamma"] == pytest.approx(0.0, abs=1e-10)


# ---------------------------------------------------------------------------
# Test 4: Volume deviation
# ---------------------------------------------------------------------------


def test_compare_volume_deviation() -> None:
    """Volume deviation follows |V_relax - V_ref| / V_ref * 100."""
    reference = _cubic(a=4.0)
    relaxed = _cubic(a=4.0 * 1.01)  # each side +1% → volume ≈ +3.03%

    result = compare(relaxed, reference)

    assert result.status == "success"
    assert result.data is not None
    expected = (1.01**3 - 1.0) * 100  # ≈ 3.0301 %
    assert result.data["volume_deviation"] == pytest.approx(expected, abs=0.001)


# ---------------------------------------------------------------------------
# Test 5: Symmetry preserved when space groups match
# ---------------------------------------------------------------------------


def test_compare_symmetry_preserved_when_same() -> None:
    """symmetry_preserved=True when both structures share the same space group."""
    structure = _licoo2_structure()
    result = compare(structure, structure)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["symmetry_preserved"] is True


# ---------------------------------------------------------------------------
# Test 6: Symmetry broken when space groups differ
# ---------------------------------------------------------------------------


def test_compare_symmetry_broken_when_different() -> None:
    """symmetry_preserved=False when relaxed has a different space group."""
    reference = _licoo2_structure()
    perturbed = reference.copy()
    # Translate site 0 by 15% of lattice vector a (≈0.42 Å), well above symprec=0.1 Å
    perturbed.translate_sites([0], [0.15, 0.0, 0.0], frac_coords=True)

    result = compare(perturbed, reference)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["symmetry_preserved"] is False


# ---------------------------------------------------------------------------
# Test 7: Returns ToolResult
# ---------------------------------------------------------------------------


def test_compare_returns_tool_result() -> None:
    """compare() returns a ToolResult instance."""
    structure = _orthorhombic()
    result = compare(structure, structure)

    assert isinstance(result, ToolResult)


# ---------------------------------------------------------------------------
# Test 8: Evidence type
# ---------------------------------------------------------------------------


def test_compare_evidence_type_is_a_compared() -> None:
    """Successful comparison carries evidence_type='A-compared'."""
    structure = _orthorhombic()
    result = compare(structure, structure)

    assert result.evidence_type == "A-compared"


# ---------------------------------------------------------------------------
# Test 9: Required fields in data
# ---------------------------------------------------------------------------


def test_compare_data_contains_all_required_fields() -> None:
    """data dict contains all required keys."""
    structure = _licoo2_structure()
    result = compare(structure, structure)

    assert result.data is not None
    required_keys = (
        "lattice_deviations",
        "angle_deviations",
        "volume_deviation",
        "symmetry_preserved",
        "reference_space_group",
        "relaxed_space_group",
        "within_lattice_tolerance",
        "within_volume_tolerance",
    )
    for key in required_keys:
        assert key in result.data, f"Missing required key: {key!r}"


# ---------------------------------------------------------------------------
# Test 10: Composition mismatch → failure
# ---------------------------------------------------------------------------


def test_compare_mismatched_compositions_raises_error() -> None:
    """Comparing structures with different reduced compositions returns failure."""
    relaxed = _cubic(a=4.0, species=["Li"])
    reference = _cubic(a=4.0, species=["Na"])

    result = compare(relaxed, reference)

    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "InputError"
    assert result.error.source == "reference_comparator"


# ---------------------------------------------------------------------------
# Test 11: Deviation formula correctness
# ---------------------------------------------------------------------------


def test_compare_deviation_formula_is_correct() -> None:
    """Deviation = |relaxed - reference| / reference * 100, always non-negative."""
    reference = _cubic(a=10.0)

    # relaxed > reference: |10.5 - 10.0| / 10.0 * 100 = 5.0 %
    relaxed_larger = _cubic(a=10.5)
    result_larger = compare(relaxed_larger, reference)
    assert result_larger.status == "success"
    assert result_larger.data is not None
    assert result_larger.data["lattice_deviations"]["a"] == pytest.approx(
        5.0, abs=0.001
    )

    # relaxed < reference: |9.5 - 10.0| / 10.0 * 100 = 5.0 %
    relaxed_smaller = _cubic(a=9.5)
    result_smaller = compare(relaxed_smaller, reference)
    assert result_smaller.status == "success"
    assert result_smaller.data is not None
    assert result_smaller.data["lattice_deviations"]["a"] == pytest.approx(
        5.0, abs=0.001
    )


# ---------------------------------------------------------------------------
# Test 12: Hand-computed known deviation
# ---------------------------------------------------------------------------


def test_compare_known_deviation_hand_computed() -> None:
    """A 1% stretch in a gives exactly 1.000% deviation.

    Reference a=4.000 Å, Relaxed a=4.040 Å.
    Deviation = |4.040 - 4.000| / 4.000 * 100 = 1.000 %.
    """
    reference = _orthorhombic(a=4.000, b=5.000, c=6.000)
    relaxed = _orthorhombic(a=4.040, b=5.000, c=6.000)

    result = compare(relaxed, reference)

    assert result.status == "success"
    assert result.data is not None
    devs = result.data["lattice_deviations"]
    assert devs["a"] == pytest.approx(1.000, abs=0.001)
    assert devs["b"] == pytest.approx(0.0, abs=0.001)
    assert devs["c"] == pytest.approx(0.0, abs=0.001)
