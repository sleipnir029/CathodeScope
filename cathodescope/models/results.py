"""Core result pydantic models.

Implements:
- ErrorRecord: structured failure representation.
- ToolResult: universal return type for all tools.
- StepResult: record for a single workflow step.
- WorkflowResult: complete workflow execution record.

Implemented in T-02.
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from cathodescope.models.provenance import ProvenanceRecord

# ---------------------------------------------------------------------------
# ErrorRecord
# ---------------------------------------------------------------------------

ErrorType = Literal[
    "InputError",
    "NetworkError",
    "ValidationError",
    "ComputationError",
    "StorageError",
    "UnknownError",
]

WorkflowStatus = Literal["success", "failure", "partial"]


class ErrorRecord(BaseModel):
    """Structured failure representation embedded in any failed ToolResult.

    Captures the error category, human-readable message, optional structured
    details, the source tool that raised the error, and an optional traceback.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_type": "ComputationError",
                "message": "MACE relaxation did not converge within 500 steps.",
                "details": {"steps_taken": 500, "final_fmax": 0.05},
                "source": "structure_relaxer",
                "traceback": None,
            }
        }
    )

    error_type: ErrorType = Field(
        description="Category of the error (one of six allowed types).",
    )
    message: str = Field(
        description="Human-readable description of what went wrong.",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured key-value details for programmatic inspection.",
    )
    source: str | None = Field(
        default=None,
        description="Name of the tool or step that raised this error.",
    )
    traceback: str | None = Field(
        default=None,
        description="Python traceback string, if available.",
    )


# ---------------------------------------------------------------------------
# ToolResult
# ---------------------------------------------------------------------------


class ToolResult(BaseModel):
    """Universal return type for every CathodeScope tool.

    All tools return a ToolResult regardless of success or failure. On success,
    ``data`` holds the output payload. On failure, ``error`` holds the structured
    error. ``provenance`` is always populated. ``evidence_type`` carries the
    evidence label from the scientific validity matrix (e.g. "A-retrieved").
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tool_name": "mp_client",
                "status": "success",
                "data": {"mp_id": "mp-22526", "formula": "LiCoO2"},
                "error": None,
                "evidence_type": "A-retrieved",
                "warnings": [],
            }
        }
    )

    tool_name: str = Field(description="Name of the tool that produced this result.")
    status: WorkflowStatus = Field(
        description="Outcome of the tool execution: success, failure, or partial.",
    )
    data: dict[str, Any] | None = Field(
        default=None,
        description="Output payload when status is 'success' or 'partial'.",
    )
    error: ErrorRecord | None = Field(
        default=None,
        description="Structured error record when status is 'failure'.",
    )
    provenance: ProvenanceRecord = Field(
        description="Provenance record for this tool execution.",
    )
    evidence_type: str | None = Field(
        default=None,
        description="Evidence level label from the scientific validity matrix.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings generated during tool execution.",
    )


# ---------------------------------------------------------------------------
# StepResult
# ---------------------------------------------------------------------------


class StepResult(BaseModel):
    """Record for a single step within a workflow execution.

    Captures the step identity, its tool output, and timing information.
    Steps are ordered by ``step_index`` within a WorkflowResult.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "step_name": "fetch",
                "step_index": 0,
                "started_at": "2026-01-01T00:00:00+00:00",
                "completed_at": "2026-01-01T00:00:01+00:00",
            }
        }
    )

    step_name: str = Field(description="Name of this workflow step.")
    step_index: int = Field(description="Zero-based index of this step in the workflow.")  # noqa: E501
    tool_result: ToolResult = Field(description="ToolResult produced by this step.")
    started_at: datetime = Field(description="UTC timestamp when this step started.")
    completed_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when this step completed, or None if still running.",
    )


# ---------------------------------------------------------------------------
# WorkflowResult
# ---------------------------------------------------------------------------


class WorkflowResult(BaseModel):
    """Complete record of a single workflow execution.

    Aggregates all step results, top-level status, provenance, and timing
    for one end-to-end run of a named workflow on a specific material.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_run_id": "12345678-1234-5678-1234-567812345678",
                "workflow_name": "structural_analysis",
                "status": "success",
                "material_id": "mp-22526",
                "started_at": "2026-01-01T00:00:00+00:00",
                "completed_at": "2026-01-01T00:10:00+00:00",
            }
        }
    )

    workflow_run_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this workflow run.",
    )
    workflow_name: str = Field(description="Name of the workflow that was executed.")
    status: WorkflowStatus = Field(
        description="Overall outcome: 'success', 'failure', or 'partial'.",
    )
    steps: list[StepResult] = Field(
        description="Ordered list of step results for this workflow run.",
    )
    provenance: ProvenanceRecord = Field(
        description="Top-level provenance record for the entire workflow run.",
    )
    material_id: str | None = Field(
        default=None,
        description="Materials Project ID of the material processed, if applicable.",
    )
    started_at: datetime = Field(description="UTC timestamp when the workflow started.")
    completed_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the workflow completed, or None if running.",
    )
