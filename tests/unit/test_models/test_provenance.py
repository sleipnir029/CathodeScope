"""Unit tests for cathodescope.models.provenance.

Tests for ProvenanceRecord model and create_provenance() factory function.
15 tests implemented in T-01.
"""

import json
import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cathodescope.models.provenance import ProvenanceRecord, create_provenance

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_kwargs() -> dict:
    """Return the minimum required keyword arguments for ProvenanceRecord."""
    return {
        "created_by": "cathodescope",
        "tool_name": "mp_client",
        "tool_version": "0.1.0",
        "cathodescope_version": "0.1.0",
        "python_version": "3.11.0",
        "hostname": "testhost",
        "platform": "linux",
    }


# ---------------------------------------------------------------------------
# Creation tests (4)
# ---------------------------------------------------------------------------


def test_creation_with_required_fields() -> None:
    """ProvenanceRecord can be created with only required fields."""
    record = ProvenanceRecord(**_minimal_kwargs())
    assert record.created_by == "cathodescope"
    assert record.tool_name == "mp_client"
    assert record.tool_version == "0.1.0"


def test_creation_with_all_fields() -> None:
    """ProvenanceRecord can be created with all 17 fields populated."""
    wf_id = uuid.uuid4()
    rec_id = uuid.uuid4()
    ts = datetime(2026, 1, 1, tzinfo=UTC)
    record = ProvenanceRecord(
        record_id=rec_id,
        created_at=ts,
        created_by="agent",
        tool_name="structure_relaxer",
        tool_version="0.1.0",
        cathodescope_version="0.1.0",
        python_version="3.11.0",
        hostname="testhost",
        platform="linux",
        workflow_run_id=wf_id,
        step_name="relax",
        elapsed_seconds=5.2,
        input_hash="abc123",
        output_hash="def456",
        config_snapshot={"fmax": 0.01},
        notes="test run",
        tags=["benchmark", "lco"],
    )
    assert record.record_id == rec_id
    assert record.created_at == ts
    assert record.workflow_run_id == wf_id
    assert record.elapsed_seconds == 5.2
    assert record.tags == ["benchmark", "lco"]
    assert record.config_snapshot == {"fmax": 0.01}


def test_record_id_defaults_to_uuid4() -> None:
    """ProvenanceRecord.record_id defaults to a new UUID4 when not provided."""
    record = ProvenanceRecord(**_minimal_kwargs())
    assert isinstance(record.record_id, uuid.UUID)


def test_created_at_defaults_to_utc_now() -> None:
    """ProvenanceRecord.created_at defaults to the current UTC datetime."""
    before = datetime.now(UTC)
    record = ProvenanceRecord(**_minimal_kwargs())
    after = datetime.now(UTC)
    assert before <= record.created_at <= after
    assert record.created_at.tzinfo is not None


# ---------------------------------------------------------------------------
# Validation tests (4)
# ---------------------------------------------------------------------------


def test_invalid_created_by_rejected() -> None:
    """ProvenanceRecord rejects invalid created_by values."""
    with pytest.raises(ValidationError):
        ProvenanceRecord(**{**_minimal_kwargs(), "created_by": "alien"})  # type: ignore[arg-type]


def test_negative_elapsed_seconds_rejected() -> None:
    """ProvenanceRecord rejects negative elapsed_seconds."""
    with pytest.raises(ValidationError):
        ProvenanceRecord(**{**_minimal_kwargs(), "elapsed_seconds": -1.0})


def test_all_created_by_literals_accepted() -> None:
    """All three valid created_by literals are accepted."""
    for value in ("cathodescope", "user", "agent"):
        record = ProvenanceRecord(**{**_minimal_kwargs(), "created_by": value})  # type: ignore[arg-type]
        assert record.created_by == value


def test_optional_fields_default_to_none_or_empty() -> None:
    """Optional fields default to None or empty collections when not provided."""
    record = ProvenanceRecord(**_minimal_kwargs())
    assert record.workflow_run_id is None
    assert record.step_name is None
    assert record.elapsed_seconds is None
    assert record.input_hash is None
    assert record.output_hash is None
    assert record.notes is None
    assert record.config_snapshot == {}
    assert record.tags == []


# ---------------------------------------------------------------------------
# Serialization tests (3)
# ---------------------------------------------------------------------------


def test_model_dump_json_mode_produces_serializable_output() -> None:
    """model_dump(mode='json') output can be serialized with json.dumps."""
    record = ProvenanceRecord(**_minimal_kwargs())
    data = record.model_dump(mode="json")
    # Must not raise
    json_str = json.dumps(data)
    assert isinstance(json_str, str)


def test_model_dump_contains_all_17_fields() -> None:
    """model_dump() output contains exactly the 17 expected fields."""
    record = ProvenanceRecord(**_minimal_kwargs())
    data = record.model_dump()
    expected_fields = {
        "record_id",
        "created_at",
        "created_by",
        "tool_name",
        "tool_version",
        "cathodescope_version",
        "python_version",
        "hostname",
        "platform",
        "workflow_run_id",
        "step_name",
        "elapsed_seconds",
        "input_hash",
        "output_hash",
        "config_snapshot",
        "notes",
        "tags",
    }
    assert set(data.keys()) == expected_fields


def test_json_round_trip_via_model_dump_json() -> None:
    """model_dump_json() → model_validate_json() round trip preserves all values."""
    record = ProvenanceRecord(**_minimal_kwargs())
    restored = ProvenanceRecord.model_validate_json(record.model_dump_json())
    assert restored == record


# ---------------------------------------------------------------------------
# Deserialization tests (1)
# ---------------------------------------------------------------------------


def test_round_trip_via_model_dump_dict() -> None:
    """model_dump(mode='json') → model_validate() round trip preserves all values."""
    record = ProvenanceRecord(**_minimal_kwargs())
    data = record.model_dump(mode="json")
    restored = ProvenanceRecord.model_validate(data)
    assert restored == record


# ---------------------------------------------------------------------------
# Factory function tests (3)
# ---------------------------------------------------------------------------


def test_create_provenance_returns_provenance_record() -> None:
    """create_provenance() returns a ProvenanceRecord instance."""
    record = create_provenance(
        created_by="cathodescope",
        tool_name="mp_client",
        tool_version="0.1.0",
    )
    assert isinstance(record, ProvenanceRecord)


def test_create_provenance_auto_populates_system_fields() -> None:
    """create_provenance() auto-populates system fields from the runtime environment.

    Checks cathodescope_version, python_version, hostname, and platform.
    """
    record = create_provenance(
        created_by="cathodescope",
        tool_name="mp_client",
        tool_version="0.1.0",
    )
    assert record.cathodescope_version == "0.1.0"
    assert record.python_version != ""
    assert record.hostname != ""
    assert record.platform != ""


def test_create_provenance_passes_optional_kwargs_through() -> None:
    """create_provenance() correctly passes optional keyword arguments to the model."""
    wf_id = uuid.uuid4()
    record = create_provenance(
        created_by="cathodescope",
        tool_name="mp_client",
        tool_version="0.1.0",
        workflow_run_id=wf_id,
        step_name="fetch",
        elapsed_seconds=1.5,
        tags=["test"],
    )
    assert record.workflow_run_id == wf_id
    assert record.step_name == "fetch"
    assert record.elapsed_seconds == 1.5
    assert record.tags == ["test"]
