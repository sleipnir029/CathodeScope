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


@pytest.fixture
def frozen_time() -> Iterator[str]:
    """Freeze time to the canonical test timestamp.

    Yields the ISO-8601 string of the frozen time.
    """
    canonical = "2026-01-01T00:00:00Z"
    # Real freezegun integration added in T-01 when datetime is used in models.
    yield canonical


@pytest.fixture
def deterministic_uuid() -> Iterator[uuid.UUID]:
    """Return a deterministic UUID for test reproducibility.

    Yields a fixed UUID and patches uuid.uuid4 to return it.
    """
    fixed = uuid.UUID("12345678-1234-5678-1234-567812345678")
    with patch("uuid.uuid4", return_value=fixed):
        yield fixed
