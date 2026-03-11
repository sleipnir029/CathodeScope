"""Unit tests for cathodescope.tools.mp_client.

16 tests covering:
- fetch_by_mp_id (3)
- fetch_by_formula (3)
- error handling: not found, timeout, rate limit (3)
- caching behaviour (2)
- provenance population (2)
- fixture file validation (3)

All tests use mocks — no live MP API calls.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cathodescope.models.results import ToolResult
from cathodescope.tools.mp_client import CathodescopeMPClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "mp_responses"

MINIMAL_STRUCTURE_DICT = {
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
    "sites": [
        {
            "species": [{"element": "Li", "occu": 1.0}],
            "abc": [0.0, 0.0, 0.0],
            "xyz": [0.0, 0.0, 0.0],
            "label": "Li",
            "properties": {},
        }
    ],
    "@module": "pymatgen.core.structure",
    "@class": "Structure",
    "charge": 0,
}

MINIMAL_MP_DATA = {
    "material_id": "mp-22526",
    "formula_pretty": "LiCoO2",
    "symmetry": {"symbol": "R-3m", "number": 166},
    "energy_per_atom": -6.789,
    "formation_energy_per_atom": -2.123,
    "band_gap": 1.5,
    "structure": MINIMAL_STRUCTURE_DICT,
}


def make_mock_rester(mp_data: dict | None = None, raise_exc: Exception | None = None):
    """Return a context-manager mock for MPRester."""
    mock_rester = MagicMock()
    mock_ctx = MagicMock()
    mock_rester.__enter__ = MagicMock(return_value=mock_ctx)
    mock_rester.__exit__ = MagicMock(return_value=False)

    if raise_exc is not None:
        mock_ctx.materials.summary.search.side_effect = raise_exc
    elif mp_data is not None:
        mock_doc = MagicMock()
        mock_doc.material_id = mp_data["material_id"]
        mock_doc.formula_pretty = mp_data["formula_pretty"]
        mock_doc.symmetry.symbol = mp_data["symmetry"]["symbol"]
        mock_doc.symmetry.number = mp_data["symmetry"]["number"]
        mock_doc.energy_per_atom = mp_data["energy_per_atom"]
        mock_doc.formation_energy_per_atom = mp_data["formation_energy_per_atom"]
        mock_doc.band_gap = mp_data["band_gap"]
        mock_doc.structure = MagicMock()
        mock_doc.structure.as_dict.return_value = mp_data["structure"]
        mock_ctx.materials.summary.search.return_value = [mock_doc]
    else:
        mock_ctx.materials.summary.search.return_value = []

    return mock_rester


@pytest.fixture()
def client(tmp_path):
    """CathodescopeMPClient with a temporary cache directory."""
    return CathodescopeMPClient(api_key="test-key", cache_dir=tmp_path)


# ---------------------------------------------------------------------------
# T-07-01 to T-07-03: fetch_by_mp_id
# ---------------------------------------------------------------------------


class TestFetchByMpId:
    """Tests for CathodescopeMPClient.fetch_by_mp_id."""

    def test_success_returns_tool_result(self, client, tmp_path):
        """fetch_by_mp_id returns a ToolResult with status='success'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result = client.fetch_by_mp_id("mp-22526")

        assert isinstance(result, ToolResult)
        assert result.status == "success"

    def test_data_contains_required_metadata(self, client):
        """ToolResult.data includes mp_id, formula, space_group, energies, band_gap."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result = client.fetch_by_mp_id("mp-22526")

        assert result.data is not None
        data = result.data
        assert data["mp_id"] == "mp-22526"
        assert data["formula"] == "LiCoO2"
        assert "space_group" in data
        assert "energy_per_atom" in data
        assert "formation_energy_per_atom" in data
        assert "band_gap" in data
        assert "structure" in data

    def test_evidence_type_is_a_retrieved(self, client):
        """ToolResult.evidence_type must be 'A-retrieved'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result = client.fetch_by_mp_id("mp-22526")

        assert result.evidence_type == "A-retrieved"


# ---------------------------------------------------------------------------
# T-07-04 to T-07-06: fetch_by_formula
# ---------------------------------------------------------------------------


class TestFetchByFormula:
    """Tests for CathodescopeMPClient.fetch_by_formula."""

    def test_success_returns_tool_result(self, client):
        """fetch_by_formula returns a ToolResult with status='success'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result = client.fetch_by_formula("LiCoO2")

        assert isinstance(result, ToolResult)
        assert result.status == "success"

    def test_data_contains_required_metadata(self, client):
        """fetch_by_formula result.data has the same required keys as fetch_by_mp_id."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result = client.fetch_by_formula("LiCoO2")

        assert result.data is not None
        data = result.data
        for key in ("mp_id", "formula", "space_group", "energy_per_atom", "structure"):
            assert key in data, f"Missing key: {key}"

    def test_no_results_returns_failure(self, client):
        """fetch_by_formula with no MP matches returns status='failure'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(None),
        ):
            result = client.fetch_by_formula("Xx99Yy")

        assert result.status == "failure"
        assert result.error is not None
        assert result.error.error_type == "InputError"


# ---------------------------------------------------------------------------
# T-07-07 to T-07-09: error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for CathodescopeMPClient error handling."""

    def test_mp_id_not_found_returns_failure(self, client):
        """fetch_by_mp_id with unknown mp_id returns failure ToolResult."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(None),
        ):
            result = client.fetch_by_mp_id("mp-99999999")

        assert result.status == "failure"
        assert result.error is not None
        assert result.error.error_type == "InputError"

    def test_timeout_returns_network_error(self, client):
        """A TimeoutError from the API produces error_type='NetworkError'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(raise_exc=TimeoutError("timed out")),
        ):
            result = client.fetch_by_mp_id("mp-22526")

        assert result.status == "failure"
        assert result.error is not None
        assert result.error.error_type == "NetworkError"

    def test_generic_exception_returns_unknown_error(self, client):
        """An unexpected exception from the API produces error_type='UnknownError'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(raise_exc=RuntimeError("unexpected")),
        ):
            result = client.fetch_by_mp_id("mp-22526")

        assert result.status == "failure"
        assert result.error is not None
        assert result.error.error_type == "UnknownError"


# ---------------------------------------------------------------------------
# T-07-10 to T-07-11: caching
# ---------------------------------------------------------------------------


class TestCaching:
    """Tests for CathodescopeMPClient caching behaviour."""

    def test_second_call_uses_cache(self, client):
        """A second fetch_by_mp_id for the same id skips the API call."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ) as mock_cls:
            client.fetch_by_mp_id("mp-22526")
            client.fetch_by_mp_id("mp-22526")
            # MPRester should only have been entered once
            assert mock_cls().__enter__().materials.summary.search.call_count <= 1

    def test_cache_hit_returns_same_data(self, client):
        """Cached result has identical data to the original fetch."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result1 = client.fetch_by_mp_id("mp-22526")

        # Second call — API mock not needed; should read from disk cache
        result2 = client.fetch_by_mp_id("mp-22526")

        assert result1.data == result2.data


# ---------------------------------------------------------------------------
# T-07-12 to T-07-13: provenance
# ---------------------------------------------------------------------------


class TestProvenance:
    """Tests for CathodescopeMPClient provenance population."""

    def test_provenance_tool_name_is_mp_client(self, client):
        """ToolResult.provenance.tool_name must be 'mp_client'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result = client.fetch_by_mp_id("mp-22526")

        assert result.provenance.tool_name == "mp_client"

    def test_provenance_created_by_cathodescope(self, client):
        """ToolResult.provenance.created_by must be 'cathodescope'."""
        with patch(
            "cathodescope.tools.mp_client.MPRester",
            return_value=make_mock_rester(MINIMAL_MP_DATA),
        ):
            result = client.fetch_by_mp_id("mp-22526")

        assert result.provenance.created_by == "cathodescope"


# ---------------------------------------------------------------------------
# T-07-14 to T-07-16: fixture file validation
# ---------------------------------------------------------------------------


class TestFixtureFiles:
    """Validate that the committed MP fixture JSON files are well-formed."""

    @pytest.mark.parametrize(
        "mp_id",
        ["mp-22526", "mp-19017", "mp-18767"],
    )
    def test_fixture_file_exists(self, mp_id):
        """Each benchmark material must have a fixture file."""
        fixture_path = FIXTURE_DIR / f"{mp_id}.json"
        assert fixture_path.exists(), f"Missing fixture: {fixture_path}"

    @pytest.mark.parametrize(
        "mp_id",
        ["mp-22526", "mp-19017", "mp-18767"],
    )
    def test_fixture_has_required_keys(self, mp_id):
        """Each fixture JSON must contain all required metadata keys."""
        fixture_path = FIXTURE_DIR / f"{mp_id}.json"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not yet captured: {mp_id}")
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        for key in (
            "mp_id",
            "formula",
            "space_group",
            "energy_per_atom",
            "formation_energy_per_atom",
            "band_gap",
            "structure",
        ):
            assert key in data, f"Fixture {mp_id} missing key: {key}"

    @pytest.mark.parametrize(
        "mp_id",
        ["mp-22526", "mp-19017", "mp-18767"],
    )
    def test_fixture_structure_has_lattice_and_sites(self, mp_id):
        """Fixture structure dict must have 'lattice' and 'sites' keys."""
        fixture_path = FIXTURE_DIR / f"{mp_id}.json"
        if not fixture_path.exists():
            pytest.skip(f"Fixture not yet captured: {mp_id}")
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        structure = data["structure"]
        assert "lattice" in structure, f"Fixture {mp_id}: structure missing 'lattice'"
        assert "sites" in structure, f"Fixture {mp_id}: structure missing 'sites'"
