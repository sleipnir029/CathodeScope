"""ProvenanceRecord pydantic model and factory function.

Implements:
- ProvenanceRecord: 17-field provenance record embedded in every data record.
- create_provenance(): factory function for fully-populated provenance records.

Implemented in T-01.
"""

import platform as _platform_module
import socket
import sys
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProvenanceRecord(BaseModel):
    """Provenance record embedded in every CathodeScope data artifact.

    Contains 17 fields capturing identity, tool metadata, runtime environment,
    workflow context, content hashes, configuration snapshot, and free-form tags.
    All fields except those with defaults are required at construction time.
    Use create_provenance() for runtime-auto-populated records.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "record_id": "12345678-1234-5678-1234-567812345678",
                "created_at": "2026-01-01T00:00:00+00:00",
                "created_by": "cathodescope",
                "tool_name": "mp_client",
                "tool_version": "0.1.0",
                "cathodescope_version": "0.1.0",
                "python_version": "3.11.0",
                "hostname": "workstation",
                "platform": "linux",
                "workflow_run_id": None,
                "step_name": None,
                "elapsed_seconds": None,
                "input_hash": None,
                "output_hash": None,
                "config_snapshot": {},
                "notes": None,
                "tags": [],
            }
        }
    )

    # --- Identity (fields 1–2) ---
    record_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this provenance record.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when this record was created.",
    )

    # --- Creator (field 3) ---
    created_by: Literal["cathodescope", "user", "agent"] = Field(
        description="Entity that created this record.",
    )

    # --- Tool identity (fields 4–9) ---
    tool_name: str = Field(description="Name of the tool that produced this record.")
    tool_version: str = Field(description="Version of the tool.")
    cathodescope_version: str = Field(description="CathodeScope package version.")
    python_version: str = Field(description="Python interpreter version string.")
    hostname: str = Field(description="Hostname of the machine that ran the tool.")
    platform: str = Field(description="Operating system platform string.")

    # --- Workflow context (fields 10–12) ---
    workflow_run_id: uuid.UUID | None = Field(
        default=None,
        description="UUID of the parent workflow run, if any.",
    )
    step_name: str | None = Field(
        default=None,
        description="Name of the workflow step that created this record.",
    )
    elapsed_seconds: float | None = Field(
        default=None,
        description="Wall-clock time in seconds for the tool execution (must be ≥ 0).",
    )

    # --- Content hashes (fields 13–14) ---
    input_hash: str | None = Field(
        default=None,
        description="SHA-256 hex digest of the serialized tool inputs.",
    )
    output_hash: str | None = Field(
        default=None,
        description="SHA-256 hex digest of the serialized tool outputs.",
    )

    # --- Config and metadata (fields 15–17) ---
    config_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of the CathodescopeSettings used during execution.",
    )
    notes: str | None = Field(
        default=None,
        description="Free-form notes about this record.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for searching and filtering provenance records.",
    )

    @field_validator("elapsed_seconds")
    @classmethod
    def elapsed_must_be_non_negative(cls, v: float | None) -> float | None:
        """Reject negative elapsed_seconds values."""
        if v is not None and v < 0:
            raise ValueError("elapsed_seconds must be non-negative")
        return v


def create_provenance(
    *,
    created_by: Literal["cathodescope", "user", "agent"],
    tool_name: str,
    tool_version: str,
    **kwargs: Any,
) -> ProvenanceRecord:
    """Factory function for creating a fully-populated ProvenanceRecord.

    Auto-populates cathodescope_version, python_version, hostname, and platform
    from the current runtime environment. All other ProvenanceRecord fields can be
    supplied as keyword arguments and are passed through directly.

    Args:
        created_by: Entity creating this record ("cathodescope", "user", or "agent").
        tool_name: Name of the tool producing the record.
        tool_version: Version string of the tool.
        **kwargs: Additional fields forwarded to ProvenanceRecord.

    Returns:
        A fully-populated ProvenanceRecord with runtime environment fields set.
    """
    from cathodescope import __version__ as _cathodescope_version

    vi = sys.version_info
    python_version = f"{vi.major}.{vi.minor}.{vi.micro}"

    return ProvenanceRecord(
        created_by=created_by,
        tool_name=tool_name,
        tool_version=tool_version,
        cathodescope_version=_cathodescope_version,
        python_version=python_version,
        hostname=socket.gethostname(),
        platform=_platform_module.system().lower(),
        **kwargs,
    )
