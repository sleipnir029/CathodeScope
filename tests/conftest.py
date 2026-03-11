"""Shared pytest fixtures for CathodeScope tests.

Provides:
- frozen_time: canonical test timestamp (2026-01-01T00:00:00Z).
- deterministic_uuid: deterministic UUID factory for test reproducibility.
- sample_provenance: a minimal ProvenanceRecord fixture (populated in T-01).
"""

import uuid
from collections.abc import Iterator
from unittest.mock import patch

import pytest

from cathodescope.models.provenance import ProvenanceRecord


@pytest.fixture
def frozen_time() -> Iterator[str]:
    """Freeze time to the canonical test timestamp.

    Yields the ISO-8601 string of the frozen time.
    """
    canonical = "2026-01-01T00:00:00Z"
    yield canonical


@pytest.fixture
def sample_provenance() -> ProvenanceRecord:
    """Return a minimal ProvenanceRecord suitable for use in unit tests."""
    return ProvenanceRecord(
        created_by="cathodescope",
        tool_name="test_tool",
        tool_version="0.1.0",
        cathodescope_version="0.1.0",
        python_version="3.11.0",
        hostname="testhost",
        platform="linux",
    )


@pytest.fixture
def deterministic_uuid() -> Iterator[uuid.UUID]:
    """Return a deterministic UUID for test reproducibility.

    Yields a fixed UUID and patches uuid.uuid4 to return it.
    """
    fixed = uuid.UUID("12345678-1234-5678-1234-567812345678")
    with patch("uuid.uuid4", return_value=fixed):
        yield fixed
