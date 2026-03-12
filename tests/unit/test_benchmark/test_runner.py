"""Unit tests for cathodescope.benchmark.runner.

Tests implemented in T-23. All tests use a mock WorkflowEngine so no
real tools or MACE are required.
"""

import json
import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from cathodescope.benchmark.registry import BenchmarkMaterialRegistry
from cathodescope.benchmark.runner import BenchmarkRunner
from cathodescope.models.provenance import create_provenance
from cathodescope.models.reports import BenchmarkSummary
from cathodescope.models.results import StepResult, ToolResult, WorkflowResult
from cathodescope.provenance.store import ArtifactStore

# ---------------------------------------------------------------------------
# All 24 required metric keys from benchmark_spec.md Section 4
# ---------------------------------------------------------------------------

ALL_24_METRIC_KEYS = {
    "input_resolution",
    "structure_retrieval",
    "structure_normalization",
    "space_group_input",
    "relaxation_convergence",
    "relaxation_steps",
    "final_fmax",
    "final_energy",
    "lattice_param_deviation_a",
    "lattice_param_deviation_b",
    "lattice_param_deviation_c",
    "angle_deviation_alpha",
    "angle_deviation_beta",
    "angle_deviation_gamma",
    "volume_deviation",
    "symmetry_preserved",
    "space_group_output",
    "symprec_used",
    "min_bond_length",
    "max_bond_length",
    "evidence_labeling_complete",
    "report_generated",
    "runtime_seconds",
    "workflow_version",
}

# A representative "full success" metrics payload (all 24 keys).
_FULL_SUCCESS_METRICS: dict = {
    "input_resolution": True,
    "structure_retrieval": True,
    "structure_normalization": True,
    "space_group_input": "R-3m",
    "relaxation_convergence": True,
    "relaxation_steps": 23,
    "final_fmax": 0.005,
    "final_energy": -42.156,
    "lattice_param_deviation_a": 0.5,
    "lattice_param_deviation_b": 0.5,
    "lattice_param_deviation_c": 0.5,
    "angle_deviation_alpha": 0.0,
    "angle_deviation_beta": 0.0,
    "angle_deviation_gamma": 0.0,
    "volume_deviation": 1.0,
    "symmetry_preserved": True,
    "space_group_output": "R-3m",
    "symprec_used": 0.1,
    "min_bond_length": 1.92,
    "max_bond_length": 2.11,
    "evidence_labeling_complete": True,
    "report_generated": True,
    # runtime_seconds and workflow_version are overridden by the runner
    "runtime_seconds": 10.0,
    "workflow_version": "0.1.0",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_prov() -> object:
    return create_provenance(
        created_by="cathodescope",
        tool_name="test_tool",
        tool_version="0.1.0",
    )


def _make_workflow_result(
    material_id: str = "mp-22526",
    metrics: dict | None = None,
    status: str = "success",
) -> WorkflowResult:
    """Build a minimal WorkflowResult with metrics in the step data."""
    prov = _make_prov()
    now = datetime.now(UTC)
    step_data = dict(_FULL_SUCCESS_METRICS)
    if metrics is not None:
        step_data.update(metrics)
    tool_result = ToolResult(
        tool_name="test_step",
        status="success",
        data=step_data,
        provenance=prov,
    )
    step = StepResult(
        step_name="metrics_step",
        step_index=0,
        tool_result=tool_result,
        started_at=now,
        completed_at=now,
    )
    return WorkflowResult(
        workflow_run_id=uuid.uuid4(),
        workflow_name="test_workflow",
        status=status,  # type: ignore[arg-type]
        steps=[step],
        provenance=prov,
        material_id=material_id,
        started_at=now,
        completed_at=now,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_store(tmp_path: object) -> ArtifactStore:
    return ArtifactStore(tmp_path / "artifacts")  # type: ignore[operator]


@pytest.fixture
def registry() -> BenchmarkMaterialRegistry:
    return BenchmarkMaterialRegistry()


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = MagicMock()
    engine.run.return_value = _make_workflow_result()
    return engine


@pytest.fixture
def runner(
    mock_engine: MagicMock,
    registry: BenchmarkMaterialRegistry,
    tmp_store: ArtifactStore,
) -> BenchmarkRunner:
    return BenchmarkRunner(
        engine=mock_engine,
        registry=registry,
        store=tmp_store,
        workflow_name="test_workflow",
        workflow_version="0.1.0",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_runner_processes_all_materials(
    runner: BenchmarkRunner, mock_engine: MagicMock
) -> None:
    """The runner must call engine.run() once per benchmark material."""
    runner.run("phase1_structural_analysis", config={})
    assert mock_engine.run.call_count == 3


def test_runner_returns_benchmark_summary(runner: BenchmarkRunner) -> None:
    """run() must return a BenchmarkSummary instance."""
    result = runner.run("phase1_structural_analysis", config={})
    assert isinstance(result, BenchmarkSummary)


def test_runner_summary_has_correct_materials_count(runner: BenchmarkRunner) -> None:
    """materials_count must equal the number of materials in the registry."""
    summary = runner.run("phase1_structural_analysis", config={})
    assert summary.materials_count == 3


def test_runner_summary_has_status_counts(runner: BenchmarkRunner) -> None:
    """status_counts must contain all five status keys summing to materials_count."""
    summary = runner.run("phase1_structural_analysis", config={})
    expected_keys = {
        "success",
        "partial_success",
        "soft_failure",
        "hard_failure",
        "infrastructure_failure",
    }
    assert set(summary.status_counts.keys()) == expected_keys
    assert sum(summary.status_counts.values()) == summary.materials_count


def test_runner_produces_benchmark_row_per_material(runner: BenchmarkRunner) -> None:
    """There must be exactly one row path per material in the summary."""
    summary = runner.run("phase1_structural_analysis", config={})
    assert len(summary.rows) == 3


def test_runner_row_contains_all_metrics(
    runner: BenchmarkRunner, tmp_store: ArtifactStore, tmp_path: object
) -> None:
    """Each stored BenchmarkRow must contain all 24 required metric keys."""
    summary = runner.run("phase1_structural_analysis", config={})
    bench_id = str(summary.benchmark_run_id)
    store_root = tmp_store._root  # type: ignore[attr-defined]

    for mp_id in ("mp-22526", "mp-19017", "mp-18767"):
        row_path = store_root / "benchmarks" / bench_id / "rows" / f"{mp_id}.json"
        assert row_path.exists(), f"Row file missing: {row_path}"
        row_data = json.loads(row_path.read_text(encoding="utf-8"))
        missing = ALL_24_METRIC_KEYS - set(row_data.get("metrics", {}).keys())
        assert not missing, f"Missing metrics for {mp_id}: {missing}"


def test_runner_isolates_material_failures(
    registry: BenchmarkMaterialRegistry, tmp_store: ArtifactStore
) -> None:
    """A failure on one material must not abort processing of other materials."""
    engine = MagicMock()

    def side_effect(
        workflow_name: str, material: dict, config: object
    ) -> WorkflowResult:
        if material.get("mp_id") == "mp-22526":
            raise RuntimeError("simulated infrastructure failure")
        return _make_workflow_result(material_id=material.get("mp_id", "unknown"))

    engine.run.side_effect = side_effect

    runner = BenchmarkRunner(
        engine=engine,
        registry=registry,
        store=tmp_store,
        workflow_name="test_workflow",
    )
    summary = runner.run("phase1_structural_analysis", config={})

    # All 3 materials must be attempted.
    assert engine.run.call_count == 3
    # All 3 must appear in the summary rows.
    assert summary.materials_count == 3
    assert len(summary.rows) == 3


def test_runner_continues_after_single_material_failure(
    registry: BenchmarkMaterialRegistry, tmp_store: ArtifactStore
) -> None:
    """A BenchmarkSummary must be produced even when the first material fails."""
    engine = MagicMock()
    engine.run.side_effect = [
        RuntimeError("fail on first material"),
        _make_workflow_result("mp-19017"),
        _make_workflow_result("mp-18767"),
    ]
    runner = BenchmarkRunner(
        engine=engine,
        registry=registry,
        store=tmp_store,
        workflow_name="test_workflow",
    )
    summary = runner.run("phase1_structural_analysis", config={})
    assert isinstance(summary, BenchmarkSummary)
    assert summary.materials_count == 3
    assert summary.status_counts["infrastructure_failure"] == 1


def test_runner_classifies_failure_categories(
    registry: BenchmarkMaterialRegistry, tmp_store: ArtifactStore
) -> None:
    """Exception during engine.run() must produce infrastructure_failure status."""
    engine = MagicMock()
    engine.run.side_effect = RuntimeError("disk full")
    runner = BenchmarkRunner(
        engine=engine,
        registry=registry,
        store=tmp_store,
        workflow_name="test_workflow",
    )
    summary = runner.run("phase1_structural_analysis", config={})
    assert summary.status_counts["infrastructure_failure"] == 3
    # Non-exception statuses must be zero.
    for status in ("success", "partial_success", "soft_failure", "hard_failure"):
        assert summary.status_counts[status] == 0


def test_runner_stores_artifacts(
    runner: BenchmarkRunner, tmp_store: ArtifactStore
) -> None:
    """Benchmark summary and one row per material must be written to the store."""
    summary = runner.run("phase1_structural_analysis", config={})
    bench_id = str(summary.benchmark_run_id)

    assert tmp_store.exists(f"benchmarks/{bench_id}/summary.json")

    for mp_id in ("mp-22526", "mp-19017", "mp-18767"):
        assert tmp_store.exists(
            f"benchmarks/{bench_id}/rows/{mp_id}.json"
        ), f"Row missing for {mp_id}"


def test_runner_records_timestamps(runner: BenchmarkRunner) -> None:
    """BenchmarkSummary must have started_at <= completed_at."""
    summary = runner.run("phase1_structural_analysis", config={})
    assert summary.started_at is not None
    assert summary.completed_at is not None
    assert summary.completed_at >= summary.started_at


def test_runner_records_runtime(runner: BenchmarkRunner) -> None:
    """runtime_seconds must be a non-negative float."""
    summary = runner.run("phase1_structural_analysis", config={})
    assert isinstance(summary.runtime_seconds, float)
    assert summary.runtime_seconds >= 0.0


def test_runner_provenance_is_populated(runner: BenchmarkRunner) -> None:
    """BenchmarkSummary.provenance must be a fully-populated ProvenanceRecord."""
    summary = runner.run("phase1_structural_analysis", config={})
    assert summary.provenance is not None
    assert summary.provenance.created_by == "cathodescope"
    assert summary.provenance.tool_name == "benchmark_runner"
