"""Input resolver tool.

Converts raw user input (formula string or mp-id) into a NormalizedQuery.
Step 0 of every workflow.

Implemented in T-08.
"""

import re
from typing import Any, Protocol

from pymatgen.core.composition import Composition

from cathodescope.models.material import NormalizedQuery
from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ErrorRecord, ToolResult

_TOOL_VERSION = "0.1.0"

# Matches exactly 'mp-' followed by one or more digits (e.g. 'mp-22526').
_MP_ID_RE = re.compile(r"^mp-\d+$")


class _MPClientProtocol(Protocol):
    """Duck-type interface for the MP client methods used by the resolver."""

    def fetch_by_mp_id(self, mp_id: str) -> ToolResult:
        """Fetch material data by Materials Project ID."""
        ...

    def fetch_by_formula(self, formula: str) -> ToolResult:
        """Fetch the lowest-energy material matching the given formula."""
        ...


def resolve(raw_input: str, mp_client: _MPClientProtocol) -> ToolResult:
    """Resolve raw user input to a NormalizedQuery ToolResult.

    Detects whether ``raw_input`` is a formula string or an mp-id by checking
    against the pattern ``mp-\\d+``. Validates the input accordingly, calls
    the MP client to fill in missing fields (formula for mp-id inputs, mp_id
    for formula inputs), and returns a :class:`~cathodescope.models.results.ToolResult`
    with the :class:`~cathodescope.models.material.NormalizedQuery` in ``data``.

    Args:
        raw_input: User-provided string, e.g. ``"LiCoO2"`` or ``"mp-22526"``.
        mp_client: MP client instance used for formula/mp-id lookups.

    Returns:
        A :class:`~cathodescope.models.results.ToolResult` with
        ``status="success"`` and the NormalizedQuery dict in ``data``, or
        ``status="failure"`` with an ``InputError`` for invalid inputs.
    """
    raw = raw_input.strip()

    if not raw:
        return _failure("Input must not be empty or whitespace-only.")

    if _MP_ID_RE.match(raw):
        return _resolve_mp_id(raw, raw_input, mp_client)

    if raw.startswith("mp-"):
        return _failure(
            f"'{raw}' looks like an mp-id but has invalid format. "
            "Expected 'mp-<digits>' (e.g. 'mp-22526')."
        )

    return _resolve_formula(raw, raw_input, mp_client)


def _resolve_mp_id(
    mp_id: str,
    raw_input: str,
    mp_client: _MPClientProtocol,
) -> ToolResult:
    """Resolve an mp-id to a NormalizedQuery via the MP client."""
    fetch = mp_client.fetch_by_mp_id(mp_id)
    if fetch.status == "failure":
        err_msg = fetch.error.message if fetch.error else "unknown error"
        return _failure(f"Could not resolve mp-id '{mp_id}': {err_msg}")

    data: dict[str, Any] = fetch.data or {}
    formula_raw = data.get("formula")
    formula = str(formula_raw) if formula_raw is not None else mp_id

    try:
        reduced = Composition(formula).reduced_formula
    except Exception:  # noqa: BLE001
        reduced = formula

    query = NormalizedQuery(
        formula=formula,
        reduced_formula=reduced,
        mp_id=mp_id,
        source_type="mp_id",
        raw_input=raw_input,
    )
    return _success(query)


def _resolve_formula(
    formula: str,
    raw_input: str,
    mp_client: _MPClientProtocol,
) -> ToolResult:
    """Resolve a formula string to a NormalizedQuery via the MP client."""
    try:
        reduced = Composition(formula).reduced_formula
    except Exception:  # noqa: BLE001
        return _failure(f"'{formula}' is not a valid chemical formula.")

    fetch = mp_client.fetch_by_formula(formula)
    mp_id: str | None = None
    if fetch.status == "success" and fetch.data:
        mp_id_raw = fetch.data.get("mp_id")
        mp_id = str(mp_id_raw) if mp_id_raw is not None else None

    query = NormalizedQuery(
        formula=formula,
        reduced_formula=reduced,
        mp_id=mp_id,
        source_type="formula",
        raw_input=raw_input,
    )
    return _success(query)


def _success(query: NormalizedQuery) -> ToolResult:
    """Build a successful ToolResult wrapping a NormalizedQuery."""
    return ToolResult(
        tool_name="input_resolver",
        status="success",
        data=query.model_dump(mode="json"),
        evidence_type="A-retrieved",
        provenance=create_provenance(
            created_by="cathodescope",
            tool_name="input_resolver",
            tool_version=_TOOL_VERSION,
        ),
    )


def _failure(message: str) -> ToolResult:
    """Build a failure ToolResult with an InputError."""
    return ToolResult(
        tool_name="input_resolver",
        status="failure",
        error=ErrorRecord(
            error_type="InputError",
            message=message,
            source="input_resolver",
        ),
        provenance=create_provenance(
            created_by="cathodescope",
            tool_name="input_resolver",
            tool_version=_TOOL_VERSION,
        ),
    )
