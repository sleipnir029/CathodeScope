"""Unit tests for cathodescope.models.material.

Tests for NormalizedQuery, CanonicalMaterial, and classify_family().
16 tests (T-03) + 5 tests (T-08b) implemented in T-03 and T-08b.
"""

import json
import uuid

import pytest
from pydantic import ValidationError

from cathodescope.models.provenance import ProvenanceRecord

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_provenance() -> ProvenanceRecord:
    """Return a minimal ProvenanceRecord for embedding in material models."""
    return ProvenanceRecord(
        created_by="cathodescope",
        tool_name="test_tool",
        tool_version="0.1.0",
        cathodescope_version="0.1.0",
        python_version="3.11.0",
        hostname="testhost",
        platform="linux",
    )


def _minimal_structure_dict() -> dict:
    """Return a minimal pymatgen-compatible structure dict."""
    return {
        "@module": "pymatgen.core.structure",
        "@class": "Structure",
        "charge": 0,
        "lattice": {
            "matrix": [[2.8, 0, 0], [0, 2.8, 0], [0, 0, 2.8]],
            "a": 2.8,
            "b": 2.8,
            "c": 2.8,
            "alpha": 90.0,
            "beta": 90.0,
            "gamma": 90.0,
            "volume": 21.952,
        },
        "properties": {},
        "sites": [
            {
                "species": [{"element": "Li", "occu": 1}],
                "abc": [0.0, 0.0, 0.0],
                "xyz": [0.0, 0.0, 0.0],
                "label": "Li",
                "properties": {},
            }
        ],
    }


def _minimal_canonical_material_data() -> dict:
    """Return minimal data dict for constructing a CanonicalMaterial."""
    return {
        "formula": "LiCoO2",
        "reduced_formula": "LiCoO2",
        "family": "layered_oxide",
        "structure": _minimal_structure_dict(),
        "source": "materials_project",
        "provenance": _minimal_provenance(),
    }


# ---------------------------------------------------------------------------
# NormalizedQuery tests (T-03)
# ---------------------------------------------------------------------------


def test_normalized_query_creation_from_formula() -> None:
    """NormalizedQuery creates successfully with source_type='formula'."""
    from cathodescope.models.material import NormalizedQuery

    query = NormalizedQuery(
        formula="LiCoO2",
        reduced_formula="LiCoO2",
        source_type="formula",
        raw_input="LiCoO2",
    )

    assert query.formula == "LiCoO2"
    assert query.reduced_formula == "LiCoO2"
    assert query.source_type == "formula"
    assert query.raw_input == "LiCoO2"
    assert query.mp_id is None


def test_normalized_query_creation_from_mp_id() -> None:
    """NormalizedQuery creates successfully with source_type='mp_id'."""
    from cathodescope.models.material import NormalizedQuery

    query = NormalizedQuery(
        formula="LiCoO2",
        reduced_formula="LiCoO2",
        mp_id="mp-22526",
        source_type="mp_id",
        raw_input="mp-22526",
    )

    assert query.mp_id == "mp-22526"
    assert query.source_type == "mp_id"
    assert query.raw_input == "mp-22526"


def test_normalized_query_rejects_empty_input() -> None:
    """NormalizedQuery raises ValidationError when raw_input is empty."""
    from cathodescope.models.material import NormalizedQuery

    with pytest.raises(ValidationError):
        NormalizedQuery(
            formula="",
            reduced_formula="",
            source_type="formula",
            raw_input="",
        )


def test_normalized_query_source_type_validates_enum() -> None:
    """NormalizedQuery rejects invalid source_type values."""
    from cathodescope.models.material import NormalizedQuery

    with pytest.raises(ValidationError):
        NormalizedQuery(
            formula="LiCoO2",
            reduced_formula="LiCoO2",
            source_type="unknown",  # type: ignore[arg-type]
            raw_input="LiCoO2",
        )


def test_normalized_query_preserves_raw_input() -> None:
    """NormalizedQuery stores raw_input exactly as given."""
    from cathodescope.models.material import NormalizedQuery

    raw = "  LiCoO2  "
    query = NormalizedQuery(
        formula="LiCoO2",
        reduced_formula="LiCoO2",
        source_type="formula",
        raw_input=raw,
    )

    assert query.raw_input == raw


def test_normalized_query_serializes_to_json() -> None:
    """NormalizedQuery serializes to valid JSON and back."""
    from cathodescope.models.material import NormalizedQuery

    query = NormalizedQuery(
        formula="LiCoO2",
        reduced_formula="LiCoO2",
        source_type="formula",
        raw_input="LiCoO2",
    )

    json_str = query.model_dump_json()
    data = json.loads(json_str)

    assert data["formula"] == "LiCoO2"
    assert data["source_type"] == "formula"
    assert "timestamp" in data


# ---------------------------------------------------------------------------
# CanonicalMaterial tests (T-03)
# ---------------------------------------------------------------------------


def test_canonical_material_creation_with_valid_data() -> None:
    """CanonicalMaterial creates successfully with all required fields."""
    from cathodescope.models.material import CanonicalMaterial

    material = CanonicalMaterial(**_minimal_canonical_material_data())

    assert material.formula == "LiCoO2"
    assert material.reduced_formula == "LiCoO2"
    assert material.family == "layered_oxide"
    assert material.source == "materials_project"
    assert material.schema_version == "1.0.0"


def test_canonical_material_rejects_missing_structure() -> None:
    """CanonicalMaterial raises ValidationError when structure is missing."""
    from cathodescope.models.material import CanonicalMaterial

    data = _minimal_canonical_material_data()
    del data["structure"]

    with pytest.raises(ValidationError):
        CanonicalMaterial(**data)


def test_canonical_material_family_validates_enum() -> None:
    """CanonicalMaterial rejects invalid family values."""
    from cathodescope.models.material import CanonicalMaterial

    data = _minimal_canonical_material_data()
    data["family"] = "invalid_family"

    with pytest.raises(ValidationError):
        CanonicalMaterial(**data)


def test_canonical_material_source_validates_enum() -> None:
    """CanonicalMaterial rejects invalid source values."""
    from cathodescope.models.material import CanonicalMaterial

    data = _minimal_canonical_material_data()
    data["source"] = "invalid_source"

    with pytest.raises(ValidationError):
        CanonicalMaterial(**data)


def test_canonical_material_material_id_is_uuid_format() -> None:
    """CanonicalMaterial.material_id is a valid UUID string."""
    from cathodescope.models.material import CanonicalMaterial

    material = CanonicalMaterial(**_minimal_canonical_material_data())

    # Should parse as a UUID without raising
    parsed = uuid.UUID(material.material_id)
    assert str(parsed) == material.material_id


def test_canonical_material_workflow_eligibility_is_dict() -> None:
    """CanonicalMaterial.workflow_eligibility is a dict with default value."""
    from cathodescope.models.material import CanonicalMaterial

    material = CanonicalMaterial(**_minimal_canonical_material_data())

    assert isinstance(material.workflow_eligibility, dict)
    assert material.workflow_eligibility == {"structural_analysis": True}


def test_canonical_material_benchmark_tags_is_list() -> None:
    """CanonicalMaterial.benchmark_tags is a list, empty by default."""
    from cathodescope.models.material import CanonicalMaterial

    material = CanonicalMaterial(**_minimal_canonical_material_data())

    assert isinstance(material.benchmark_tags, list)
    assert material.benchmark_tags == []


def test_canonical_material_serializes_to_json() -> None:
    """CanonicalMaterial serializes to valid JSON."""
    from cathodescope.models.material import CanonicalMaterial

    material = CanonicalMaterial(**_minimal_canonical_material_data())
    json_str = material.model_dump_json()
    data = json.loads(json_str)

    assert data["formula"] == "LiCoO2"
    assert data["family"] == "layered_oxide"
    assert "material_id" in data
    assert "created_at" in data


def test_canonical_material_deserializes_from_json() -> None:
    """CanonicalMaterial round-trips through JSON serialization."""
    from cathodescope.models.material import CanonicalMaterial

    material = CanonicalMaterial(**_minimal_canonical_material_data())
    json_str = material.model_dump_json()

    restored = CanonicalMaterial.model_validate_json(json_str)

    assert restored.material_id == material.material_id
    assert restored.formula == material.formula
    assert restored.family == material.family


def test_canonical_material_structure_field_accepts_pymatgen_dict() -> None:
    """CanonicalMaterial.structure accepts a pymatgen as_dict() output."""
    from cathodescope.models.material import CanonicalMaterial

    structure_dict = _minimal_structure_dict()
    data = _minimal_canonical_material_data()
    data["structure"] = structure_dict

    material = CanonicalMaterial(**data)

    assert "lattice" in material.structure
    assert "sites" in material.structure


# ---------------------------------------------------------------------------
# classify_family tests (T-08b)
# ---------------------------------------------------------------------------


def test_classify_family_layered_oxide_r3m_limio2() -> None:
    """classify_family returns 'layered_oxide' for R-3m + LiCoO2."""
    from cathodescope.models.material import classify_family

    result = classify_family("R-3m", "LiCoO2")

    assert result == "layered_oxide"


def test_classify_family_olivine_pnma_limpo4() -> None:
    """classify_family returns 'olivine_polyanion' for Pnma + LiFePO4."""
    from cathodescope.models.material import classify_family

    result = classify_family("Pnma", "LiFePO4")

    assert result == "olivine_polyanion"


def test_classify_family_spinel_fd3m_lim2o4() -> None:
    """classify_family returns 'spinel' for Fd-3m + LiMn2O4."""
    from cathodescope.models.material import classify_family

    result = classify_family("Fd-3m", "LiMn2O4")

    assert result == "spinel"


def test_classify_family_unknown_returns_other() -> None:
    """classify_family returns 'other' for an unrecognised space group / formula."""
    from cathodescope.models.material import classify_family

    assert classify_family("P1", "LiCoO2") == "other"
    assert classify_family("R-3m", "NaCoO2") == "other"
    assert classify_family("Pnma", "LiCoO2") == "other"


def test_classify_family_case_insensitive() -> None:
    """classify_family treats space-group strings case-insensitively."""
    from cathodescope.models.material import classify_family

    assert classify_family("r-3m", "LiCoO2") == "layered_oxide"
    assert classify_family("R-3M", "LiCoO2") == "layered_oxide"
    assert classify_family("pnma", "LiFePO4") == "olivine_polyanion"
    assert classify_family("PNMA", "LiFePO4") == "olivine_polyanion"
    assert classify_family("fd-3m", "LiMn2O4") == "spinel"
    assert classify_family("FD-3M", "LiMn2O4") == "spinel"
