"""Unit tests for T-18: Workflow Base Classes and Engine.

17 tests:
  Registry (3): register/get, list, unknown raises
  Context (2): accumulates step results, read by step name
  Engine (12): step order, context passing, return type, timestamps,
               runtime, config snapshot, failure handling, partial results,
               success classification, hard-failure classification,
               error non-swallowing, provenance
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from cathodescope.models.provenance import ProvenanceRecord
from cathodescope.models.results import (
    ErrorRecord,
    StepResult,
    ToolResult,
    WorkflowResult,
)
from cathodescope.workflows.base import (
    StepSpec,
    WorkflowContext,
    WorkflowDefinition,
    WorkflowRegistry,
)
from cathodescope.workflows.engine import WorkflowEngine

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _make_provenance() -> ProvenanceRecord:
    return ProvenanceRecord(
        created_by="cathodescope",
        tool_name="test_tool",
        tool_version="0.1.0",
        cathodescope_version="0.1.0",
        python_version="3.11.0",
        hostname="testhost",
        platform="linux",
    )


def _success_result(tool_name: str = "mock_tool") -> ToolResult:
    return ToolResult(
        tool_name=tool_name,
        status="success",
        data={"result": "ok"},
        provenance=_make_provenance(),
    )


def _failure_result() -> ToolResult:
    return ToolResult(
        tool_name="mock_tool",
        status="failure",
        error=ErrorRecord(
            error_type="ComputationError",
            message="Step failed.",
        ),
        provenance=_make_provenance(),
    )


def _partial_result() -> ToolResult:
    return ToolResult(
        tool_name="mock_tool",
        status="partial",
        data={"result": "partial"},
        warnings=["borderline convergence"],
        provenance=_make_provenance(),
    )


def _spec(name: str, fn: Callable[[WorkflowContext], ToolResult]) -> StepSpec:
    return StepSpec(name=name, step_fn=fn)


def _defn(name: str, steps: list[StepSpec]) -> WorkflowDefinition:
    return WorkflowDefinition(name=name, version="1.0.0", steps=steps)


def _engine_and_registry() -> tuple[WorkflowEngine, WorkflowRegistry]:
    registry = WorkflowRegistry()
    engine = WorkflowEngine(registry)
    return engine, registry


# ---------------------------------------------------------------------------
# Registry tests (3)
# ---------------------------------------------------------------------------


def test_workflow_registry_register_and_get() -> None:
    """Registered workflow definition is retrievable by name."""
    registry = WorkflowRegistry()
    defn = _defn("my_workflow", [])
    registry.register(defn)
    assert registry.get("my_workflow") is defn


def test_workflow_registry_list_workflows() -> None:
    """list() returns all registered workflow definitions."""
    registry = WorkflowRegistry()
    a = _defn("workflow_a", [])
    b = _defn("workflow_b", [])
    registry.register(a)
    registry.register(b)
    listed = registry.list()
    assert len(listed) == 2
    assert {d.name for d in listed} == {"workflow_a", "workflow_b"}


def test_workflow_registry_unknown_workflow_raises_error() -> None:
    """get() raises KeyError for an unregistered workflow name."""
    registry = WorkflowRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent")


# ---------------------------------------------------------------------------
# Context tests (2)
# ---------------------------------------------------------------------------


def test_workflow_context_accumulates_step_results() -> None:
    """WorkflowContext stores StepResults keyed by step name."""
    ctx = WorkflowContext(
        workflow_run_id="run-id-1",
        started_at=datetime.now(UTC),
        material={"id": "mp-22526"},
        config={},
    )
    step = StepResult(
        step_name="fetch",
        step_index=0,
        tool_result=_success_result(),
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )
    ctx.step_results["fetch"] = step
    assert "fetch" in ctx.step_results
    assert ctx.step_results["fetch"].step_name == "fetch"


def test_workflow_context_read_by_step_name() -> None:
    """StepResult stored in context is retrievable by step name."""
    ctx = WorkflowContext(
        workflow_run_id="run-id-2",
        started_at=datetime.now(UTC),
        material={},
        config={},
    )
    step = StepResult(
        step_name="normalize",
        step_index=1,
        tool_result=_success_result(),
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )
    ctx.step_results["normalize"] = step
    retrieved = ctx.step_results["normalize"]
    assert retrieved.step_name == "normalize"
    assert retrieved.step_index == 1


# ---------------------------------------------------------------------------
# Engine tests (12)
# ---------------------------------------------------------------------------


def test_engine_executes_steps_in_order() -> None:
    """Engine calls step functions in the order defined by WorkflowDefinition."""
    call_order: list[str] = []

    def step_a(ctx: WorkflowContext) -> ToolResult:
        call_order.append("a")
        return _success_result("tool_a")

    def step_b(ctx: WorkflowContext) -> ToolResult:
        call_order.append("b")
        return _success_result("tool_b")

    engine, registry = _engine_and_registry()
    registry.register(_defn("ordered_wf", [_spec("a", step_a), _spec("b", step_b)]))
    engine.run("ordered_wf", {}, {})
    assert call_order == ["a", "b"]


def test_engine_passes_context_between_steps() -> None:
    """Later steps see earlier steps' results in WorkflowContext."""
    snapshots: list[set[str]] = []

    def first(ctx: WorkflowContext) -> ToolResult:
        snapshots.append(set(ctx.step_results.keys()))
        return _success_result("first")

    def second(ctx: WorkflowContext) -> ToolResult:
        snapshots.append(set(ctx.step_results.keys()))
        return _success_result("second")

    engine, registry = _engine_and_registry()
    registry.register(_defn("ctx_wf", [_spec("first", first), _spec("second", second)]))
    engine.run("ctx_wf", {}, {})
    assert snapshots[0] == set()          # first step: empty context
    assert "first" in snapshots[1]        # second step: sees 'first' result


def test_engine_returns_workflow_result() -> None:
    """Engine.run() returns a WorkflowResult with correct workflow_name."""
    engine, registry = _engine_and_registry()
    registry.register(_defn("simple_wf", [_spec("s", lambda ctx: _success_result())]))
    result = engine.run("simple_wf", {}, {})
    assert isinstance(result, WorkflowResult)
    assert result.workflow_name == "simple_wf"


def test_engine_records_timestamps() -> None:
    """WorkflowResult has started_at and completed_at; completed >= started."""
    engine, registry = _engine_and_registry()
    registry.register(_defn("ts_wf", [_spec("s", lambda ctx: _success_result())]))
    result = engine.run("ts_wf", {}, {})
    assert result.started_at is not None
    assert result.completed_at is not None
    assert result.completed_at >= result.started_at


def test_engine_records_runtime_seconds() -> None:
    """WorkflowResult.provenance.elapsed_seconds is non-negative."""
    engine, registry = _engine_and_registry()
    registry.register(_defn("rt_wf", [_spec("s", lambda ctx: _success_result())]))
    result = engine.run("rt_wf", {}, {})
    assert result.provenance.elapsed_seconds is not None
    assert result.provenance.elapsed_seconds >= 0.0


def test_engine_captures_config_snapshot() -> None:
    """WorkflowResult.provenance.config_snapshot contains the provided config."""
    engine, registry = _engine_and_registry()
    registry.register(_defn("cfg_wf", [_spec("s", lambda ctx: _success_result())]))
    config = {"fmax": 0.01, "max_steps": 500}
    result = engine.run("cfg_wf", {}, config)
    assert isinstance(result.provenance.config_snapshot, dict)
    assert result.provenance.config_snapshot.get("fmax") == 0.01


def test_engine_handles_step_failure_gracefully() -> None:
    """Engine returns WorkflowResult without raising when a step fails."""
    engine, registry = _engine_and_registry()
    registry.register(_defn("fail_wf", [_spec("bad", lambda ctx: _failure_result())]))
    result = engine.run("fail_wf", {}, {})
    assert isinstance(result, WorkflowResult)
    assert result.status == "failure"


def test_engine_stores_partial_results_on_failure() -> None:
    """Steps completed before a failure are preserved in WorkflowResult.steps."""
    engine, registry = _engine_and_registry()
    registry.register(
        _defn(
            "partial_wf",
            [
                _spec("step_ok", lambda ctx: _success_result("ok_tool")),
                _spec("step_fail", lambda ctx: _failure_result()),
            ],
        )
    )
    result = engine.run("partial_wf", {}, {})
    step_names = [s.step_name for s in result.steps]
    assert "step_ok" in step_names
    assert "step_fail" in step_names


def test_engine_classifies_success() -> None:
    """All-success steps produce WorkflowResult.status == 'success'."""
    engine, registry = _engine_and_registry()
    registry.register(
        _defn(
            "ok_wf",
            [
                _spec("a", lambda ctx: _success_result()),
                _spec("b", lambda ctx: _success_result()),
            ],
        )
    )
    result = engine.run("ok_wf", {}, {})
    assert result.status == "success"


def test_engine_classifies_hard_failure() -> None:
    """A step returning status='failure' produces WorkflowResult.status == 'failure'."""
    engine, registry = _engine_and_registry()
    registry.register(_defn("hard_wf", [_spec("fail", lambda ctx: _failure_result())]))
    result = engine.run("hard_wf", {}, {})
    assert result.status == "failure"


def test_engine_never_swallows_errors() -> None:
    """Unexpected exceptions raised by step functions propagate from engine.run()."""

    def crashing_step(ctx: WorkflowContext) -> ToolResult:
        raise RuntimeError("Unexpected crash inside step")

    engine, registry = _engine_and_registry()
    registry.register(_defn("crash_wf", [_spec("crash", crashing_step)]))
    with pytest.raises(RuntimeError, match="Unexpected crash inside step"):
        engine.run("crash_wf", {}, {})


def test_engine_provenance_is_populated() -> None:
    """Provenance in WorkflowResult is populated with tool_name 'workflow_engine'."""
    engine, registry = _engine_and_registry()
    registry.register(_defn("prov_wf", [_spec("s", lambda ctx: _success_result())]))
    result = engine.run("prov_wf", {}, {})
    assert isinstance(result.provenance, ProvenanceRecord)
    assert result.provenance.tool_name == "workflow_engine"
