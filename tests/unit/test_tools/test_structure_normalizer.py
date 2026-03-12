"""Unit tests for cathodescope.tools.structure_normalizer.

14 tests implemented in T-09.
"""

import json
from pathlib import Path

from pymatgen.core.structure import Structure

from cathodescope.models.results import ToolResult
from cathodescope.tools.structure_normalizer import normalize

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "mp_responses"


def _load_structure_dict(filename: str) -> dict[str, object]:
    """Load the structure sub-dict from an MP response fixture."""
    data: dict[str, object] = json.loads(
        (_FIXTURE_DIR / filename).read_text(encoding="utf-8")
    )
    return data["structure"]  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Space group preservation (3 materials)
# ---------------------------------------------------------------------------


def test_normalize_licoo2_space_group_preserved() -> None:
    """LiCoO2 R-3m space group symbol is preserved after conventionalization."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict, mp_id="mp-22526", formula="LiCoO2")
    assert result.status == "success"
    assert result.data is not None
    assert result.data["space_group"] == "R-3m"


def test_normalize_lifepo4_space_group_preserved() -> None:
    """LiFePO4 Pnma space group symbol is preserved after conventionalization."""
    structure_dict = _load_structure_dict("mp-19017.json")
    result = normalize(structure_dict, mp_id="mp-19017", formula="LiFePO4")
    assert result.status == "success"
    assert result.data is not None
    assert result.data["space_group"] == "Pnma"


def test_normalize_limn2o4_space_group_preserved() -> None:
    """LiMn2O4 Fd-3m space group symbol is preserved after conventionalization."""
    structure_dict = _load_structure_dict("mp-18767.json")
    result = normalize(structure_dict, mp_id="mp-18767", formula="LiMn2O4")
    assert result.status == "success"
    assert result.data is not None
    assert result.data["space_group"] == "Fd-3m"


# ---------------------------------------------------------------------------
# Conventional cell atom counts (3 materials)
# ---------------------------------------------------------------------------


def test_normalize_licoo2_atom_count() -> None:
    """LiCoO2 conventional cell has exactly 12 atoms."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict, mp_id="mp-22526", formula="LiCoO2")
    assert result.data is not None
    assert result.data["n_atoms"] == 12


def test_normalize_lifepo4_atom_count() -> None:
    """LiFePO4 conventional cell has exactly 28 atoms."""
    structure_dict = _load_structure_dict("mp-19017.json")
    result = normalize(structure_dict, mp_id="mp-19017", formula="LiFePO4")
    assert result.data is not None
    assert result.data["n_atoms"] == 28


def test_normalize_limn2o4_atom_count() -> None:
    """LiMn2O4 conventional cell has exactly 56 atoms."""
    structure_dict = _load_structure_dict("mp-18767.json")
    result = normalize(structure_dict, mp_id="mp-18767", formula="LiMn2O4")
    assert result.data is not None
    assert result.data["n_atoms"] == 56


# ---------------------------------------------------------------------------
# ToolResult format
# ---------------------------------------------------------------------------


def test_normalize_returns_tool_result() -> None:
    """normalize() returns a ToolResult instance."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict)
    assert isinstance(result, ToolResult)


def test_normalize_evidence_type() -> None:
    """Successful ToolResult carries evidence_type='A-computed'."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict)
    assert result.evidence_type == "A-computed"


def test_normalize_status_success() -> None:
    """normalize() returns status='success' for a valid structure dict."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict)
    assert result.status == "success"


def test_normalize_data_has_required_fields() -> None:
    """data dict contains all six required keys."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict, mp_id="mp-22526", formula="LiCoO2")
    assert result.data is not None
    required_keys = (
        "mp_id",
        "formula",
        "space_group",
        "space_group_number",
        "n_atoms",
        "structure",
    )
    for key in required_keys:
        assert key in result.data, f"Missing required key: {key!r}"


def test_normalize_structure_is_dict_with_lattice_and_sites() -> None:
    """Output structure value is a dict containing 'lattice' and 'sites' keys."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict)
    assert result.data is not None
    s = result.data["structure"]
    assert isinstance(s, dict)
    assert "lattice" in s
    assert "sites" in s


def test_normalize_provenance_populated() -> None:
    """ToolResult.provenance carries correct tool metadata."""
    structure_dict = _load_structure_dict("mp-22526.json")
    result = normalize(structure_dict)
    prov = result.provenance
    assert prov.tool_name == "structure_normalizer"
    assert prov.created_by == "cathodescope"


# ---------------------------------------------------------------------------
# Degenerate structure handling
# ---------------------------------------------------------------------------


def test_normalize_degenerate_structure_returns_failure() -> None:
    """An invalid/degenerate structure dict returns a failure ToolResult."""
    bad_dict: dict[str, object] = {"not_a_structure": True}
    result = normalize(bad_dict)
    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "ComputationError"
    assert result.error.source == "structure_normalizer"


# ---------------------------------------------------------------------------
# Conventional cell is at least as large as primitive cell
# ---------------------------------------------------------------------------


def test_normalize_conventional_cell_is_larger_than_primitive() -> None:
    """The conventional cell has at least as many atoms as the primitive input."""
    structure_dict = _load_structure_dict("mp-22526.json")
    primitive = Structure.from_dict(structure_dict)
    result = normalize(structure_dict)
    assert result.data is not None
    assert result.data["n_atoms"] >= len(primitive.sites)
