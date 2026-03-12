"""Unit tests for cathodescope.workflows.structural_analysis.

7 tests:
  1. test_structural_analysis_is_registered_in_registry
  2. test_structural_analysis_has_correct_step_count
  3. test_structural_analysis_step_order_is_correct
  4. test_structural_analysis_step_names_match_spec
  5. test_structural_analysis_version_is_1_0_0
  6. test_structural_analysis_uses_correct_tool_for_each_step
  7. test_structural_analysis_passes_context_correctly
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from cathodescope.models.provenance import ProvenanceRecord
from cathodescope.models.results import StepResult, ToolResult
from cathodescope.workflows import structural_analysis
from cathodescope.workflows.base import WorkflowContext, WorkflowDefinition

# ---------------------------------------------------------------------------
# Constants — canonical step names per architecture.md Section 4.3
# ---------------------------------------------------------------------------

_EXPECTED_STEP_NAMES = [
    "resolve_input",
    "fetch_structure",
    "normalize",
    "relax",
    "compare_reference",
    "validate",
    "generate_report",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_provenance() -> ProvenanceRecord:
    return ProvenanceRecord(
        created_by="cathodescope",
        tool_name="test",
        tool_version="0.1.0",
        cathodescope_version="0.1.0",
        python_version="3.11.0",
        hostname="testhost",
        platform="linux",
    )


def _success_result(tool_name: str = "mock", data: dict | None = None) -> ToolResult:
    return ToolResult(
        tool_name=tool_name,
        status="success",
        data=data if data is not None else {"key": "value"},
        provenance=_make_provenance(),
    )


def _make_step_result(step_name: str, data: dict | None = None) -> StepResult:
    return StepResult(
        step_name=step_name,
        step_index=0,
        tool_result=_success_result(data=data),
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )


def _make_ctx(**kwargs: object) -> WorkflowContext:
    defaults: dict = {
        "workflow_run_id": str(uuid.uuid4()),
        "started_at": datetime.now(UTC),
        "material": "LiCoO2",
        "config": MagicMock(),
    }
    defaults.update(kwargs)
    return WorkflowContext(**defaults)


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def definition() -> WorkflowDefinition:
    return structural_analysis.REGISTRY.get("structural_analysis")


# ---------------------------------------------------------------------------
# Tests 1–5: Structural verification (no tool invocations)
# ---------------------------------------------------------------------------


def test_structural_analysis_is_registered_in_registry() -> None:
    """The module registers 'structural_analysis' in a REGISTRY at import time."""
    definition = structural_analysis.REGISTRY.get("structural_analysis")
    assert definition.name == "structural_analysis"


def test_structural_analysis_has_correct_step_count(
    definition: WorkflowDefinition,
) -> None:
    """The workflow has exactly 7 steps."""
    assert len(definition.steps) == 7


def test_structural_analysis_step_order_is_correct(
    definition: WorkflowDefinition,
) -> None:
    """Steps appear in the canonical pipeline order."""
    actual = [s.name for s in definition.steps]
    assert actual == _EXPECTED_STEP_NAMES


def test_structural_analysis_step_names_match_spec(
    definition: WorkflowDefinition,
) -> None:
    """All 7 step names match architecture.md Section 4.3 exactly."""
    names = {s.name for s in definition.steps}
    assert names == set(_EXPECTED_STEP_NAMES)


def test_structural_analysis_version_is_1_0_0(
    definition: WorkflowDefinition,
) -> None:
    """Workflow version string is '1.0.0'."""
    assert definition.version == "1.0.0"


# ---------------------------------------------------------------------------
# Test 6: Tool binding — each step calls its designated tool
# ---------------------------------------------------------------------------


def test_structural_analysis_uses_correct_tool_for_each_step(
    definition: WorkflowDefinition,
) -> None:
    """Each step function delegates to its designated tool module function."""
    # --- resolve_input → input_resolver.resolve ---
    step_fn_resolve = definition.steps[0].step_fn
    config = MagicMock()
    config.mp_client = MagicMock()
    config.mp_client.fetch_by_formula.return_value = _success_result()
    config.mp_client.fetch_by_mp_id.return_value = _success_result()
    ctx = _make_ctx(material="LiCoO2", config=config)
    with patch(
        "cathodescope.tools.input_resolver.resolve",
        return_value=_success_result("input_resolver"),
    ) as mock_resolve:
        step_fn_resolve(ctx)
    mock_resolve.assert_called_once()

    # --- validate → physics_validator.validate ---
    step_fn_validate = next(s.step_fn for s in definition.steps if s.name == "validate")
    relax_data = {
        "relaxed_structure": {
            "lattice": {"a": 2.8, "b": 2.8, "c": 14.0},
            "sites": [],
        },
        "convergence_info": {
            "converged": True,
            "steps": 10,
            "fmax_history": [0.1, 0.01],
        },
    }
    compare_data = {"symmetry_preserved": True}
    ctx_validate = _make_ctx(
        material=MagicMock(),
        step_results={
            "relax": _make_step_result("relax", relax_data),
            "compare_reference": _make_step_result("compare_reference", compare_data),
        },
    )
    with patch(
        "cathodescope.tools.physics_validator.validate",
        return_value=_success_result("physics_validator"),
    ) as mock_validate:
        step_fn_validate(ctx_validate)
    mock_validate.assert_called_once()

    # --- generate_report → report_generator.generate ---
    step_fn_report = next(
        s.step_fn for s in definition.steps if s.name == "generate_report"
    )
    ctx_report = _make_ctx(
        material=MagicMock(),
        step_results={
            "resolve_input": _make_step_result(
                "resolve_input", {"raw_input": "LiCoO2"}
            ),
            "fetch_structure": _make_step_result(
                "fetch_structure", {"formula": "LiCoO2"}
            ),
        },
    )
    with patch(
        "cathodescope.tools.report_generator.generate",
        return_value=_success_result("report_generator"),
    ) as mock_generate:
        step_fn_report(ctx_report)
    mock_generate.assert_called_once()


# ---------------------------------------------------------------------------
# Test 7: Context passing — steps read the right keys from step_results
# ---------------------------------------------------------------------------


def test_structural_analysis_passes_context_correctly(
    definition: WorkflowDefinition,
) -> None:
    """Step functions extract the correct data from context.step_results."""
    # --- fetch_structure reads mp_id from resolve_input step result ---
    step_fn_fetch = next(
        s.step_fn for s in definition.steps if s.name == "fetch_structure"
    )
    mp_id = "mp-22526"
    mock_mp_client = MagicMock()
    mock_mp_client.fetch_by_mp_id.return_value = _success_result("mp_client")
    config = MagicMock()
    config.mp_client = mock_mp_client

    ctx_fetch = _make_ctx(
        config=config,
        step_results={
            "resolve_input": _make_step_result(
                "resolve_input", {"mp_id": mp_id, "formula": "LiCoO2"}
            ),
        },
    )
    step_fn_fetch(ctx_fetch)
    mock_mp_client.fetch_by_mp_id.assert_called_once_with(mp_id)

    # --- normalize reads structure dict + mp_id + formula from fetch_structure ---
    step_fn_normalize = next(
        s.step_fn for s in definition.steps if s.name == "normalize"
    )
    structure_dict = {"lattice": {"a": 2.8, "b": 2.8, "c": 14.0}, "sites": []}
    fetch_data = {
        "structure": structure_dict,
        "mp_id": "mp-22526",
        "formula": "LiCoO2",
    }
    ctx_normalize = _make_ctx(
        step_results={
            "fetch_structure": _make_step_result("fetch_structure", fetch_data),
        },
    )
    # Return data=None so _make_canonical_material is not attempted.
    with patch(
        "cathodescope.tools.structure_normalizer.normalize",
        return_value=ToolResult(
            tool_name="structure_normalizer",
            status="success",
            data=None,
            provenance=_make_provenance(),
        ),
    ) as mock_norm:
        step_fn_normalize(ctx_normalize)
    mock_norm.assert_called_once_with(
        structure_dict, mp_id="mp-22526", formula="LiCoO2"
    )
