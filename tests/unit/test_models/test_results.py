"""Unit tests for cathodescope.models.results.

Tests for ErrorRecord, ToolResult, StepResult, WorkflowResult.
23 tests implemented in T-02.
"""

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cathodescope.models.provenance import ProvenanceRecord
from cathodescope.models.results import (
    ErrorRecord,
    StepResult,
    ToolResult,
    WorkflowResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_provenance() -> ProvenanceRecord:
    """Return a minimal ProvenanceRecord for embedding in result models."""
    return ProvenanceRecord(
        created_by="cathodescope",
        tool_name="test_tool",
        tool_version="0.1.0",
        cathodescope_version="0.1.0",
        python_version="3.11.0",
        hostname="testhost",
        platform="linux",
    )


def _minimal_tool_result(status: str = "success") -> ToolResult:
    """Return a minimal ToolResult for embedding in step/workflow results."""
    return ToolResult(
        tool_name="test_tool",
        status=status,  # type: ignore[arg-type]
        provenance=_minimal_provenance(),
    )


def _minimal_step_result(index: int = 0) -> StepResult:
    """Return a minimal StepResult for embedding in WorkflowResult."""
    return StepResult(
        step_name="test_step",
        step_index=index,
        tool_result=_minimal_tool_result(),
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


# ---------------------------------------------------------------------------
# ErrorRecord tests (5)
# ---------------------------------------------------------------------------


def test_error_record_creation_with_required_fields() -> None:
    """ErrorRecord can be created with only the required fields."""
    err = ErrorRecord(
        error_type="InputError",
        message="bad input provided",
    )
    assert err.error_type == "InputError"
    assert err.message == "bad input provided"


def test_error_record_invalid_error_type_rejected() -> None:
    """ErrorRecord rejects an error_type value not in the allowed Literal set."""
    with pytest.raises(ValidationError):
        ErrorRecord(error_type="BogusError", message="x")  # type: ignore[arg-type]


def test_error_record_details_defaults_to_empty_dict() -> None:
    """ErrorRecord.details, source, and traceback default to empty/None."""
    err = ErrorRecord(error_type="UnknownError", message="unexpected")
    assert err.details == {}
    assert err.source is None
    assert err.traceback is None


def test_error_record_all_error_types_accepted() -> None:
    """All six valid error_type literals are accepted."""
    valid_types = (
        "InputError",
        "NetworkError",
        "ValidationError",
        "ComputationError",
        "StorageError",
        "UnknownError",
    )
    for et in valid_types:
        err = ErrorRecord(error_type=et, message="test")  # type: ignore[arg-type]
        assert err.error_type == et


def test_error_record_json_round_trip() -> None:
    """ErrorRecord survives a model_dump_json → model_validate_json round trip."""
    err = ErrorRecord(
        error_type="ComputationError",
        message="convergence failed",
        details={"steps": 500, "fmax": 0.05},
        source="structure_relaxer",
    )
    restored = ErrorRecord.model_validate_json(err.model_dump_json())
    assert restored == err


# ---------------------------------------------------------------------------
# ToolResult tests (9)
# ---------------------------------------------------------------------------


def test_tool_result_success_creation() -> None:
    """ToolResult can be created with status='success' and output data."""
    result = ToolResult(
        tool_name="mp_client",
        status="success",
        data={"mp_id": "mp-22526", "formula": "LiCoO2"},
        provenance=_minimal_provenance(),
    )
    assert result.status == "success"
    assert result.data == {"mp_id": "mp-22526", "formula": "LiCoO2"}


def test_tool_result_failure_creation() -> None:
    """ToolResult can be created with status='failure' and an ErrorRecord."""
    err = ErrorRecord(error_type="NetworkError", message="timeout")
    result = ToolResult(
        tool_name="mp_client",
        status="failure",
        error=err,
        provenance=_minimal_provenance(),
    )
    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "NetworkError"


def test_tool_result_invalid_status_rejected() -> None:
    """ToolResult rejects a status value outside the allowed Literal set."""
    with pytest.raises(ValidationError):
        ToolResult(
            tool_name="mp_client",
            status="pending",  # type: ignore[arg-type]
            provenance=_minimal_provenance(),
        )


def test_tool_result_warnings_default_empty_list() -> None:
    """ToolResult.warnings defaults to an empty list."""
    result = ToolResult(
        tool_name="mp_client",
        status="success",
        provenance=_minimal_provenance(),
    )
    assert result.warnings == []


def test_tool_result_evidence_type_defaults_to_none() -> None:
    """ToolResult.evidence_type defaults to None."""
    result = ToolResult(
        tool_name="mp_client",
        status="success",
        provenance=_minimal_provenance(),
    )
    assert result.evidence_type is None


def test_tool_result_data_and_error_both_optional() -> None:
    """ToolResult.data and .error both default to None."""
    result = ToolResult(
        tool_name="test_tool",
        status="success",
        provenance=_minimal_provenance(),
    )
    assert result.data is None
    assert result.error is None


def test_tool_result_json_round_trip() -> None:
    """ToolResult survives a model_dump_json → model_validate_json round trip."""
    result = ToolResult(
        tool_name="mp_client",
        status="success",
        data={"key": "value"},
        evidence_type="A-retrieved",
        warnings=["low band gap"],
        provenance=_minimal_provenance(),
    )
    restored = ToolResult.model_validate_json(result.model_dump_json())
    assert restored == result


def test_tool_result_embeds_provenance_record() -> None:
    """ToolResult.provenance field holds a ProvenanceRecord instance."""
    prov = _minimal_provenance()
    result = ToolResult(
        tool_name="test_tool",
        status="success",
        provenance=prov,
    )
    assert isinstance(result.provenance, ProvenanceRecord)
    assert result.provenance.tool_name == "test_tool"


def test_tool_result_partial_status_accepted() -> None:
    """ToolResult accepts status='partial' for partial-success outcomes."""
    result = ToolResult(
        tool_name="structure_relaxer",
        status="partial",
        provenance=_minimal_provenance(),
    )
    assert result.status == "partial"


# ---------------------------------------------------------------------------
# StepResult tests (4)
# ---------------------------------------------------------------------------


def test_step_result_creation_with_required_fields() -> None:
    """StepResult can be created with all required fields."""
    ts = datetime(2026, 1, 1, tzinfo=UTC)
    step = StepResult(
        step_name="fetch",
        step_index=0,
        tool_result=_minimal_tool_result(),
        started_at=ts,
    )
    assert step.step_name == "fetch"
    assert step.step_index == 0
    assert step.started_at == ts


def test_step_result_completed_at_defaults_to_none() -> None:
    """StepResult.completed_at defaults to None."""
    step = StepResult(
        step_name="normalize",
        step_index=1,
        tool_result=_minimal_tool_result(),
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert step.completed_at is None


def test_step_result_json_round_trip() -> None:
    """StepResult survives a model_dump_json → model_validate_json round trip."""
    step = StepResult(
        step_name="relax",
        step_index=2,
        tool_result=_minimal_tool_result("partial"),
        started_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
        completed_at=datetime(2026, 1, 1, 0, 5, 0, tzinfo=UTC),
    )
    restored = StepResult.model_validate_json(step.model_dump_json())
    assert restored == step


def test_step_result_embeds_tool_result() -> None:
    """StepResult.tool_result holds a ToolResult instance."""
    tr = _minimal_tool_result()
    step = StepResult(
        step_name="fetch",
        step_index=0,
        tool_result=tr,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert isinstance(step.tool_result, ToolResult)
    assert step.tool_result.tool_name == "test_tool"


# ---------------------------------------------------------------------------
# WorkflowResult tests (5)
# ---------------------------------------------------------------------------


def test_workflow_result_creation_with_required_fields() -> None:
    """WorkflowResult can be created with all required fields."""
    wf = WorkflowResult(
        workflow_name="structural_analysis",
        status="success",
        steps=[_minimal_step_result()],
        provenance=_minimal_provenance(),
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert wf.workflow_name == "structural_analysis"
    assert wf.status == "success"
    assert len(wf.steps) == 1


def test_workflow_result_run_id_defaults_to_uuid() -> None:
    """WorkflowResult.workflow_run_id defaults to a new UUID4."""
    wf = WorkflowResult(
        workflow_name="structural_analysis",
        status="success",
        steps=[],
        provenance=_minimal_provenance(),
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert isinstance(wf.workflow_run_id, uuid.UUID)


def test_workflow_result_invalid_status_rejected() -> None:
    """WorkflowResult rejects a status value not in the allowed Literal set."""
    with pytest.raises(ValidationError):
        WorkflowResult(
            workflow_name="structural_analysis",
            status="running",  # type: ignore[arg-type]
            steps=[],
            provenance=_minimal_provenance(),
            started_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_workflow_result_steps_is_list_of_step_result() -> None:
    """WorkflowResult.steps holds a list of StepResult instances."""
    steps = [_minimal_step_result(i) for i in range(3)]
    wf = WorkflowResult(
        workflow_name="structural_analysis",
        status="success",
        steps=steps,
        provenance=_minimal_provenance(),
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert len(wf.steps) == 3
    for i, step in enumerate(wf.steps):
        assert isinstance(step, StepResult)
        assert step.step_index == i


def test_workflow_result_json_round_trip() -> None:
    """WorkflowResult survives a model_dump_json → model_validate_json round trip."""
    wf = WorkflowResult(
        workflow_name="structural_analysis",
        status="partial",
        steps=[_minimal_step_result(0), _minimal_step_result(1)],
        provenance=_minimal_provenance(),
        material_id="mp-22526",
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        completed_at=datetime(2026, 1, 1, 0, 10, 0, tzinfo=UTC),
    )
    restored = WorkflowResult.model_validate_json(wf.model_dump_json())
    assert restored == wf
