"""CanonicalMaterial and NormalizedQuery pydantic models.

Implements:
- NormalizedQuery: first object created in any pipeline run from user input.
- CanonicalMaterial: canonical material representation used by all pipeline tools.
- classify_family(): assigns material family from space group and composition.

Implemented in T-03 and T-08b.
"""

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cathodescope.models.provenance import ProvenanceRecord


class NormalizedQuery(BaseModel):
    """First object created in any CathodeScope pipeline run.

    Captures the validated and normalized form of raw user input (a formula
    string or an mp-id). All downstream pipeline steps receive a
    NormalizedQuery rather than raw strings.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "formula": "LiCoO2",
                "reduced_formula": "LiCoO2",
                "mp_id": "mp-22526",
                "source_type": "formula",
                "raw_input": "LiCoO2",
                "timestamp": "2026-01-01T00:00:00+00:00",
            }
        }
    )

    formula: str = Field(description="Chemical formula as entered or resolved.")
    reduced_formula: str = Field(
        description="Reduced / Hill-notation chemical formula.",
    )
    mp_id: str | None = Field(
        default=None,
        description="Materials Project ID (e.g. 'mp-22526'), if known.",
    )
    source_type: Literal["formula", "mp_id"] = Field(
        description="How the material was specified: 'formula' or 'mp_id'.",
    )
    raw_input: str = Field(
        description="Original user-provided string, preserved verbatim.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when this query was created.",
    )

    @field_validator("raw_input", "formula", "reduced_formula")
    @classmethod
    def reject_empty_strings(cls, v: str) -> str:
        """Reject blank strings in formula, reduced_formula, and raw_input."""
        if not v.strip():
            raise ValueError("Field must not be empty or whitespace-only.")
        return v


class CanonicalMaterial(BaseModel):
    """Authoritative representation of a cathode material within CathodeScope.

    Every material that enters the system is resolved to exactly one
    CanonicalMaterial. This record is the primary key for all cross-references
    in the artifact store and is embedded in every downstream result.

    The ``structure`` field stores a pymatgen ``Structure.as_dict()`` output as
    a plain ``dict``. A field validator enforces that the dict contains the
    ``lattice`` and ``sites`` keys required by pymatgen's serialization format.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schema_version": "1.0.0",
                "material_id": "12345678-1234-5678-1234-567812345678",
                "formula": "LiCoO2",
                "reduced_formula": "LiCoO2",
                "family": "layered_oxide",
                "structure": {"lattice": {}, "sites": []},
                "source": "materials_project",
                "mp_id": "mp-22526",
                "identifiers": {},
                "benchmark_tags": [],
                "workflow_eligibility": {"structural_analysis": True},
                "created_at": "2026-01-01T00:00:00+00:00",
                "provenance": {},
            }
        }
    )

    schema_version: str = Field(
        default="1.0.0",
        description="Semantic version of the CanonicalMaterial schema.",
    )
    material_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID string, internal primary key for this material.",
    )
    formula: str = Field(description="Chemical formula (e.g. 'LiCoO2').")
    reduced_formula: str = Field(
        description="Reduced / Hill-notation chemical formula.",
    )
    family: Literal["layered_oxide", "olivine_polyanion", "spinel", "other"] = Field(
        description="Material family classification.",
    )
    structure: dict[str, Any] = Field(
        description="Pymatgen Structure serialized via as_dict().",
    )
    source: Literal["materials_project", "user_upload", "generated"] = Field(
        description="Origin of the structure data.",
    )
    mp_id: str | None = Field(
        default=None,
        description="Materials Project ID (e.g. 'mp-22526'), null if not from MP.",
    )
    identifiers: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional cross-database identifiers (ICSD, DOI, etc.).",
    )
    benchmark_tags: list[str] = Field(
        default_factory=list,
        description="Tags for benchmark grouping (e.g. ['phase1', 'layered_oxide']).",
    )
    workflow_eligibility: dict[str, Any] = Field(
        default_factory=lambda: {"structural_analysis": True},
        description="Map of workflow name to eligibility flag.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when this record was created.",
    )
    provenance: ProvenanceRecord = Field(
        description="Provenance record for this canonical material.",
    )

    @field_validator("structure")
    @classmethod
    def structure_must_have_lattice_and_sites(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Require that the structure dict has 'lattice' and 'sites' keys."""
        if "lattice" not in v or "sites" not in v:
            raise ValueError(
                "structure dict must contain 'lattice' and 'sites' keys "
                "(expected pymatgen Structure.as_dict() format)."
            )
        return v
