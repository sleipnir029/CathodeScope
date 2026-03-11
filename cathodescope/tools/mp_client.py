"""Materials Project API client.

Wraps mp-api MPRester. Implements caching, error handling,
and fixture capture for offline development.

Implemented in T-07.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

from mp_api.client import MPRester  # type: ignore[import-untyped]

from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ErrorRecord, ToolResult

_TOOL_VERSION = "0.1.0"
_FIELDS = [
    "material_id",
    "formula_pretty",
    "symmetry",
    "energy_per_atom",
    "formation_energy_per_atom",
    "band_gap",
    "structure",
]


def _cache_key(identifier: str) -> str:
    """Return a safe filename stem for a given query identifier."""
    digest = hashlib.sha256(identifier.encode()).hexdigest()[:8]
    safe = identifier.replace("/", "_").replace(" ", "_")
    return f"{safe}_{digest}"


def _doc_to_data(doc: Any) -> dict[str, Any]:
    """Extract required metadata fields from an MPRester summary document."""
    return {
        "mp_id": str(doc.material_id),
        "formula": doc.formula_pretty,
        "space_group": doc.symmetry.symbol,
        "space_group_number": doc.symmetry.number,
        "energy_per_atom": doc.energy_per_atom,
        "formation_energy_per_atom": doc.formation_energy_per_atom,
        "band_gap": doc.band_gap,
        "structure": doc.structure.as_dict(),
    }


class CathodescopeMPClient:
    """Thin wrapper around mp-api MPRester with caching and provenance.

    Fetches Materials Project structure data by mp_id or chemical formula.
    Caches responses as JSON in ``cache_dir`` to enable offline development.
    All fetch methods return a :class:`~cathodescope.models.results.ToolResult`.

    Args:
        api_key: Materials Project API key.
        cache_dir: Directory used to store cached API responses.
    """

    def __init__(self, api_key: str, cache_dir: Path | str) -> None:
        self._api_key = api_key
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_by_mp_id(self, mp_id: str) -> ToolResult:
        """Fetch a material by its Materials Project ID (e.g. 'mp-22526').

        Returns a cached response if one exists. Otherwise fetches from the
        MP API, caches the result, and returns it.

        Args:
            mp_id: A valid Materials Project identifier string.

        Returns:
            A :class:`~cathodescope.models.results.ToolResult` with
            ``evidence_type='A-retrieved'``. On failure the ``error`` field
            is populated and ``status`` is ``'failure'``.
        """
        cache_file = self._cache_dir / f"{_cache_key(mp_id)}.json"
        if cache_file.exists():
            return self._load_from_cache(cache_file)

        try:
            with MPRester(self._api_key) as mpr:
                docs = mpr.materials.summary.search(
                    material_ids=[mp_id], fields=_FIELDS
                )
        except TimeoutError as exc:
            return self._failure_result("NetworkError", str(exc))
        except Exception as exc:  # noqa: BLE001
            return self._failure_result("UnknownError", str(exc))

        if not docs:
            return self._failure_result(
                "InputError", f"Material ID '{mp_id}' not found in Materials Project."
            )

        data = _doc_to_data(docs[0])
        self._write_cache(cache_file, data)
        return self._success_result(data)

    def fetch_by_formula(self, formula: str) -> ToolResult:
        """Fetch the lowest-energy structure matching the given chemical formula.

        Queries the MP API for all structures with the given formula and
        returns the first (lowest energy) match. Caches the response.

        Args:
            formula: Chemical formula string, e.g. ``'LiCoO2'``.

        Returns:
            A :class:`~cathodescope.models.results.ToolResult` with
            ``evidence_type='A-retrieved'``. On no match, returns
            ``status='failure'`` with ``error_type='InputError'``.
        """
        cache_file = self._cache_dir / f"{_cache_key(formula)}.json"
        if cache_file.exists():
            return self._load_from_cache(cache_file)

        try:
            with MPRester(self._api_key) as mpr:
                docs = mpr.materials.summary.search(
                    formula=formula, fields=_FIELDS
                )
        except TimeoutError as exc:
            return self._failure_result("NetworkError", str(exc))
        except Exception as exc:  # noqa: BLE001
            return self._failure_result("UnknownError", str(exc))

        if not docs:
            return self._failure_result(
                "InputError",
                f"No materials found in Materials Project for formula '{formula}'.",
            )

        data = _doc_to_data(docs[0])
        self._write_cache(cache_file, data)
        return self._success_result(data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _success_result(self, data: dict[str, Any]) -> ToolResult:
        """Build a successful ToolResult with provenance."""
        return ToolResult(
            tool_name="mp_client",
            status="success",
            data=data,
            evidence_type="A-retrieved",
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="mp_client",
                tool_version=_TOOL_VERSION,
            ),
        )

    def _failure_result(self, error_type: str, message: str) -> ToolResult:
        """Build a failed ToolResult with an ErrorRecord."""
        return ToolResult(
            tool_name="mp_client",
            status="failure",
            error=ErrorRecord(
                error_type=error_type,  # type: ignore[arg-type]
                message=message,
                source="mp_client",
            ),
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="mp_client",
                tool_version=_TOOL_VERSION,
            ),
        )

    def _write_cache(self, path: Path, data: dict[str, Any]) -> None:
        """Serialise ``data`` as JSON to ``path`` (2-space indent)."""
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_from_cache(self, path: Path) -> ToolResult:
        """Load a previously cached response and return a successful ToolResult."""
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return self._success_result(data)
