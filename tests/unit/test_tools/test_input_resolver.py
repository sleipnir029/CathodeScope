"""Unit tests for cathodescope.tools.input_resolver.

12 tests covering:
- formula resolution: LiCoO2, LiFePO4 (2)
- mp-id resolution (1)
- invalid inputs: bad formula, empty, invalid mp-id format (3)
- field verification: raw_input, source_type (formula), source_type (mp_id),
  reduced_formula (4)
- MP client usage: called for formula lookup (1)
- return contract: ToolResult wrapper (1)

All tests mock the MP client — no live API calls.
"""

from unittest.mock import MagicMock

from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ToolResult
from cathodescope.tools.input_resolver import resolve

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROV = create_provenance(
    created_by="cathodescope",
    tool_name="mp_client",
    tool_version="0.1.0",
)


def _formula_client(mp_id: str, formula: str) -> MagicMock:
    """Mock MP client whose fetch_by_formula returns a successful ToolResult."""
    client = MagicMock()
    client.fetch_by_formula.return_value = ToolResult(
        tool_name="mp_client",
        status="success",
        data={"mp_id": mp_id, "formula": formula},
        evidence_type="A-retrieved",
        provenance=_PROV,
    )
    return client


def _mp_id_client(mp_id: str, formula: str) -> MagicMock:
    """Mock MP client whose fetch_by_mp_id returns a successful ToolResult."""
    client = MagicMock()
    client.fetch_by_mp_id.return_value = ToolResult(
        tool_name="mp_client",
        status="success",
        data={"mp_id": mp_id, "formula": formula},
        evidence_type="A-retrieved",
        provenance=_PROV,
    )
    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_resolve_formula_licoo2_returns_normalized_query() -> None:
    """LiCoO2 formula input resolves to a NormalizedQuery in a success ToolResult."""
    mp_client = _formula_client("mp-22526", "LiCoO2")
    result = resolve("LiCoO2", mp_client)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["formula"] == "LiCoO2"
    assert result.data["mp_id"] == "mp-22526"
    assert result.data["source_type"] == "formula"


def test_resolve_formula_lifepo4_returns_normalized_query() -> None:
    """LiFePO4 formula input resolves to a NormalizedQuery in a success ToolResult."""
    mp_client = _formula_client("mp-19017", "LiFePO4")
    result = resolve("LiFePO4", mp_client)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["formula"] == "LiFePO4"
    assert result.data["mp_id"] == "mp-19017"


def test_resolve_mp_id_returns_normalized_query() -> None:
    """mp-22526 input resolves to a NormalizedQuery with formula from MP client."""
    mp_client = _mp_id_client("mp-22526", "LiCoO2")
    result = resolve("mp-22526", mp_client)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["mp_id"] == "mp-22526"
    assert result.data["formula"] == "LiCoO2"
    assert result.data["source_type"] == "mp_id"


def test_resolve_invalid_formula_raises_input_error() -> None:
    """Invalid formula '@@@@' returns a failure ToolResult with InputError."""
    mp_client = MagicMock()
    result = resolve("@@@@", mp_client)

    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "InputError"
    assert result.error.source == "input_resolver"


def test_resolve_empty_string_raises_input_error() -> None:
    """Empty string input returns a failure ToolResult with InputError."""
    mp_client = MagicMock()
    result = resolve("", mp_client)

    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "InputError"


def test_resolve_invalid_mp_id_format_raises_input_error() -> None:
    """'mp-abc' (invalid mp-id format) returns a failure ToolResult with InputError."""
    mp_client = MagicMock()
    result = resolve("mp-abc", mp_client)

    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "InputError"
    assert "mp-abc" in result.error.message or "format" in result.error.message.lower()


def test_resolve_preserves_raw_input() -> None:
    """raw_input is preserved verbatim in the NormalizedQuery."""
    mp_client = _formula_client("mp-22526", "LiCoO2")
    raw = "LiCoO2"
    result = resolve(raw, mp_client)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["raw_input"] == raw


def test_resolve_source_type_is_formula_for_formula_input() -> None:
    """source_type is 'formula' when input is a chemical formula string."""
    mp_client = _formula_client("mp-22526", "LiCoO2")
    result = resolve("LiCoO2", mp_client)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["source_type"] == "formula"


def test_resolve_source_type_is_mp_id_for_mp_id_input() -> None:
    """source_type is 'mp_id' when input is an mp-id string."""
    mp_client = _mp_id_client("mp-22526", "LiCoO2")
    result = resolve("mp-22526", mp_client)

    assert result.status == "success"
    assert result.data is not None
    assert result.data["source_type"] == "mp_id"


def test_resolve_populates_reduced_formula() -> None:
    """reduced_formula is populated and non-empty in the NormalizedQuery."""
    mp_client = _formula_client("mp-22526", "LiCoO2")
    result = resolve("LiCoO2", mp_client)

    assert result.status == "success"
    assert result.data is not None
    assert "reduced_formula" in result.data
    assert result.data["reduced_formula"]  # non-empty


def test_resolve_uses_mp_client_for_formula_lookup() -> None:
    """MP client's fetch_by_formula is called exactly once for formula input."""
    mp_client = _formula_client("mp-22526", "LiCoO2")
    resolve("LiCoO2", mp_client)

    mp_client.fetch_by_formula.assert_called_once()


def test_resolve_returns_tool_result_wrapper() -> None:
    """resolve() returns a ToolResult instance with tool_name 'input_resolver'."""
    mp_client = _formula_client("mp-22526", "LiCoO2")
    result = resolve("LiCoO2", mp_client)

    assert isinstance(result, ToolResult)
    assert result.status == "success"
    assert result.tool_name == "input_resolver"
