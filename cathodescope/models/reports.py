"""Report and benchmark pydantic models.

Implements:
- ReportSection: one section of a workflow report.
- ReportRecord: complete report artifact.
- BenchmarkRow: single-material benchmark result with 24 metrics.
- BenchmarkSummary: aggregated benchmark results across materials.

Implemented in T-04.
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cathodescope.models.provenance import ProvenanceRecord

BenchmarkStatus = Literal[
    "success",
    "partial_success",
    "soft_failure",
    "hard_failure",
    "infrastructure_failure",
]

FailureCategory = Literal[
    "retrieval_failure",
    "convergence_failure",
    "validation_failure",
    "artifact_failure",
    "unknown_failure",
]


class ReportSection(BaseModel):
    """One section of a workflow report.

    Contains a heading, human-readable Markdown content, machine-readable
    structured data, and evidence level labels for claims in this section.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "heading": "Lattice Parameters",
                "content_markdown": (
                    "The relaxed structure has lattice parameter a = 2.81 Å."
                ),
                "data": {"a": 2.81, "b": 2.81, "c": 14.05},
                "evidence_labels": ["A-computed", "A-compared"],
            }
        }
    )

    heading: str = Field(description="Section title.")
    content_markdown: str = Field(
        description="Rendered Markdown content for human reading.",
    )
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured machine-readable data behind this section.",
    )
    evidence_labels: list[str] = Field(
        default_factory=list,
        description="Evidence level labels for claims in this section.",
    )


class ReportRecord(BaseModel):
    """Complete report artifact for a single workflow run.

    Generated from WorkflowResult data and always reproducible from the
    underlying structured records. Contains ordered sections with evidence
    labels and a provenance trail back to the source workflow run.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schema_version": "1.0.0",
                "report_id": "12345678-1234-5678-1234-567812345678",
                "material_id": "mat-001",
                "workflow_result_id": "87654321-4321-8765-4321-876543218765",
                "report_type": "structural_analysis",
                "raw_user_input": "LiCoO2",
                "title": "Structural Analysis: LiCoO2",
                "sections": [],
                "evidence_summary": {"A-computed": 3, "A-compared": 2},
                "warnings": [],
                "generated_at": "2026-01-01T00:00:00+00:00",
            }
        }
    )

    schema_version: str = Field(
        default="1.0.0",
        description="Schema version following semver.",
    )
    report_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this report.",
    )
    material_id: str = Field(
        description="References CanonicalMaterial.material_id.",
    )
    workflow_result_id: uuid.UUID = Field(
        description="References WorkflowResult.workflow_run_id.",
    )
    report_type: str = Field(
        description='Report type, e.g. "structural_analysis" or "benchmark_summary".',
    )
    raw_user_input: str = Field(
        description="Original user input that initiated this workflow (e.g. 'LiCoO2').",
    )
    title: str = Field(description="Report title.")
    sections: list[ReportSection] = Field(
        default_factory=list,
        description="Ordered list of report sections.",
    )
    evidence_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregate count of evidence labels across all sections.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Report-level warnings.",
    )
    generated_at: datetime = Field(
        description="ISO 8601 UTC timestamp when this report was generated.",
    )
    provenance: ProvenanceRecord = Field(
        description="Provenance record for this report.",
    )


class BenchmarkRow(BaseModel):
    """Single-material benchmark result within one benchmark run.

    Records all 24 metrics from benchmark_spec.md Section 4 for one
    material processed by one workflow. The metrics dict is open to support
    any workflow type; for structural_analysis all 24 keys must be present.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schema_version": "1.0.0",
                "benchmark_run_id": "12345678-1234-5678-1234-567812345678",
                "material_id": "mat-001",
                "formula": "LiCoO2",
                "family": "layered_oxide",
                "workflow_name": "structural_analysis",
                "workflow_version": "1.0.0",
                "status": "success",
                "metrics": {
                    "input_resolution": True,
                    "structure_retrieval": True,
                    "structure_normalization": True,
                    "space_group_input": "R-3m",
                    "relaxation_convergence": True,
                    "relaxation_steps": 23,
                    "final_fmax": 0.005,
                    "final_energy": -42.156,
                    "lattice_param_deviation_a": 0.53,
                    "lattice_param_deviation_b": 0.53,
                    "lattice_param_deviation_c": 0.22,
                    "volume_deviation": 1.28,
                    "symmetry_preserved": True,
                    "space_group_output": "R-3m",
                    "min_bond_length": 1.92,
                    "max_bond_length": 2.11,
                    "evidence_labeling_complete": True,
                    "report_generated": True,
                    "runtime_seconds": 12.3,
                    "workflow_version": "1.0.0",
                    "angle_deviation_alpha": 0.0,
                    "angle_deviation_beta": 0.0,
                    "angle_deviation_gamma": 0.0,
                    "symprec_used": 0.1,
                },
                "failure_category": None,
                "timestamp": "2026-01-01T00:00:00+00:00",
            }
        }
    )

    schema_version: str = Field(
        default="1.0.0",
        description="Schema version following semver.",
    )
    benchmark_run_id: uuid.UUID = Field(
        description="UUID for the overall benchmark run.",
    )
    material_id: str = Field(
        description="References CanonicalMaterial.material_id.",
    )
    formula: str = Field(
        description="Denormalized formula for readability in tables.",
    )
    family: str = Field(
        description="Denormalized cathode family for readability in tables.",
    )
    workflow_name: str = Field(description="Name of the workflow executed.")
    workflow_version: str = Field(description="Version of the workflow.")
    status: BenchmarkStatus = Field(
        description="Benchmark outcome for this material.",
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Key-value pairs of benchmark metrics from benchmark_spec.md Section 4."
        ),
    )
    failure_category: FailureCategory | None = Field(
        default=None,
        description="Failure taxonomy category; null when status is 'success'.",
    )
    timestamp: datetime = Field(
        description="ISO 8601 UTC timestamp for this benchmark row.",
    )
    provenance: ProvenanceRecord = Field(
        description="Provenance record for this benchmark row.",
    )


class BenchmarkSummary(BaseModel):
    """Aggregated results across all materials in one benchmark run.

    Enforces consistency between materials_count, status_counts, and rows
    via a model validator: all three must agree on the total number of
    materials processed.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "schema_version": "1.0.0",
                "benchmark_run_id": "12345678-1234-5678-1234-567812345678",
                "benchmark_name": "phase1_structural_analysis",
                "materials_count": 3,
                "status_counts": {
                    "success": 2,
                    "partial_success": 1,
                    "soft_failure": 0,
                    "hard_failure": 0,
                    "infrastructure_failure": 0,
                },
                "rows": [
                    "rows/mat-001.json",
                    "rows/mat-002.json",
                    "rows/mat-003.json",
                ],
                "started_at": "2026-01-01T00:00:00+00:00",
                "completed_at": "2026-01-01T00:10:00+00:00",
                "runtime_seconds": 600.0,
            }
        }
    )

    schema_version: str = Field(
        default="1.0.0",
        description="Schema version following semver.",
    )
    benchmark_run_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="UUID for this benchmark run.",
    )
    benchmark_name: str = Field(
        description='Name of the benchmark, e.g. "phase1_structural_analysis".',
    )
    materials_count: int = Field(
        description="Total number of materials in this benchmark run.",
    )
    status_counts: dict[str, int] = Field(
        description="Count of each status value; all five status keys must be present.",
    )
    rows: list[str] = Field(
        description="Relative file paths to individual BenchmarkRow JSON files.",
    )
    started_at: datetime = Field(
        description="ISO 8601 UTC timestamp when the benchmark run started.",
    )
    completed_at: datetime = Field(
        description="ISO 8601 UTC timestamp when the benchmark run completed.",
    )
    runtime_seconds: float = Field(
        description="Total wall-clock time for the entire benchmark run.",
    )
    provenance: ProvenanceRecord = Field(
        description="Provenance record for this benchmark summary.",
    )

    @model_validator(mode="after")
    def check_count_consistency(self) -> "BenchmarkSummary":
        """Enforce materials_count == sum(status_counts.values()) == len(rows)."""
        status_sum = sum(self.status_counts.values())
        rows_len = len(self.rows)
        if not (self.materials_count == status_sum == rows_len):
            raise ValueError(
                f"Inconsistent benchmark summary: "
                f"materials_count={self.materials_count}, "
                f"sum(status_counts)={status_sum}, len(rows)={rows_len}. "
                "All three must be equal."
            )
        return self
