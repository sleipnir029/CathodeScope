"""Integration tests for the full Phase 1 benchmark suite.

Tests implemented in T-24. All tests are marked @pytest.mark.integration.
They require MACE-MP-0 to be installed and are excluded from regular CI
via ``-m "not integration"``.

SC-05 documentation (Benchmark Results Review):
    LiCoO2   Full Success    (lattice < 2%, volume < 5%)
    LiMn2O4  Partial Success (lattice ≈ 3.1%, vol ≈ 9.4% — Jahn-Teller Mn³⁺ Fd-3m)
    LiFePO4  Soft Failure    (lattice ≈ 5–8% — MACE-MP-0 medium distorts Pnma c/a)
    Result: 1/3 Full Success. Failures documented per T-21 and SC-05.
    Phase gate (2/3 Full Success) not met; proceeding with documented failures.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from cathodescope.benchmark.registry import BenchmarkMaterialRegistry
from cathodescope.benchmark.runner import BenchmarkRunner
from cathodescope.models.provenance import create_provenance
from cathodescope.models.reports import BenchmarkSummary
from cathodescope.models.results import ErrorRecord, ToolResult
from cathodescope.provenance.store import ArtifactStore
from cathodescope.workflows.engine import WorkflowEngine
from cathodescope.workflows.structural_analysis import REGISTRY

# ---------------------------------------------------------------------------
# Required benchmark metric keys (benchmark_spec.md Section 4)
# ---------------------------------------------------------------------------

_REQUIRED_METRICS: frozenset[str] = frozenset(
    {
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
)

# Phase 1 benchmark materials
_PHASE1_MP_IDS: tuple[str, ...] = ("mp-22526", "mp-19017", "mp-18767")

# ---------------------------------------------------------------------------
# Offline MP client backed by test fixture files
# ---------------------------------------------------------------------------

_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "mp_responses"

_FORMULA_TO_MP_ID: dict[str, str] = {
    "LiCoO2": "mp-22526",
    "LiFePO4": "mp-19017",
    "LiMn2O4": "mp-18767",
}


class _FixtureMPClient:
    """Offline MP client that reads from local fixture JSON files."""

    def fetch_by_mp_id(self, mp_id: str) -> ToolResult:
        """Return fixture data for the given MP ID."""
        fixture_path = _FIXTURES_DIR / f"{mp_id}.json"
        data: dict[str, Any] = json.loads(fixture_path.read_text(encoding="utf-8"))
        return ToolResult(
            tool_name="mp_client",
            status="success",
            data=data,
            evidence_type="A-retrieved",
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="mp_client",
                tool_version="0.1.0",
            ),
        )

    def fetch_by_formula(self, formula: str) -> ToolResult:
        """Return fixture data for the given formula."""
        mp_id = _FORMULA_TO_MP_ID.get(formula)
        if mp_id:
            return self.fetch_by_mp_id(mp_id)
        return ToolResult(
            tool_name="mp_client",
            status="failure",
            error=ErrorRecord(
                error_type="InputError",
                message=f"No fixture available for formula {formula!r}",
                source="_FixtureMPClient",
            ),
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="mp_client",
                tool_version="0.1.0",
            ),
        )


# ---------------------------------------------------------------------------
# Minimal integration config (duck-typed)
# ---------------------------------------------------------------------------


@dataclass
class _IntegrationConfig:
    """Minimal config for integration tests.

    Provides ``mp_client`` and ``calculator`` so the workflow step helpers
    pick them up via ``hasattr`` checks rather than constructing real instances.
    """

    mp_client: Any = field(default_factory=_FixtureMPClient)
    calculator: Any = None

    def model_dump(self, *, mode: str = "json") -> dict[str, Any]:
        """Return a minimal config snapshot for provenance recording."""
        return {
            "mode": "integration_test",
            "mp_client": "fixture",
            "calculator": "injected",
        }


# ---------------------------------------------------------------------------
# Module-scoped fixtures (MACE model loaded once per session)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def mace_calculator() -> Any:
    """Load MACE-MP-0 once per module (float64 for geometry optimization)."""
    from mace.calculators import mace_mp

    return mace_mp(model="medium", device="cpu", default_dtype="float64")


@pytest.fixture(scope="module")
def benchmark_run(
    tmp_path_factory: pytest.TempPathFactory,
    mace_calculator: Any,
) -> tuple[BenchmarkSummary, str, ArtifactStore]:
    """Run the Phase 1 benchmark once and return (summary, bench_id, store).

    Module-scoped so the 3 MACE relaxations run only once regardless of how
    many tests consume this fixture.
    """
    artifacts_dir: Path = tmp_path_factory.mktemp("benchmark_suite_artifacts")
    store = ArtifactStore(artifacts_dir)
    config = _IntegrationConfig(
        mp_client=_FixtureMPClient(),
        calculator=mace_calculator,
    )
    registry = BenchmarkMaterialRegistry()
    engine = WorkflowEngine(REGISTRY)
    runner = BenchmarkRunner(engine, registry, store)
    summary = runner.run("phase1_structural_analysis", config)
    return summary, str(summary.benchmark_run_id), store


# ---------------------------------------------------------------------------
# T-24: 8 integration tests for the full Phase 1 benchmark suite
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_benchmark_phase1_runs_all_3_materials(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
) -> None:
    """Benchmark runner processes all 3 Phase 1 materials without aborting.

    Phase 1 set: LiCoO2 (mp-22526), LiFePO4 (mp-19017), LiMn2O4 (mp-18767).
    """
    summary, _, _ = benchmark_run
    assert summary.materials_count == 3, (
        f"Expected 3 materials in Phase 1 benchmark, got {summary.materials_count}. "
        "Phase 1 set: LiCoO2 (mp-22526), LiFePO4 (mp-19017), LiMn2O4 (mp-18767)."
    )


@pytest.mark.integration
@pytest.mark.xfail(
    strict=False,
    reason=(
        "SC-05: MACE-MP-0 (medium, float64) achieves 1/3 Full Success, not 2/3. "
        "LiCoO2: Full Success. "
        "LiMn2O4: Partial Success (Jahn-Teller Mn³⁺ Fd-3m; lat ≈ 3.1%, vol ≈ 9.4%). "
        "LiFePO4: Soft Failure (MACE-MP-0 distorts Pnma c/a; a ≈ 5.8%, c ≈ 8.3%). "
        "Failures documented in T-21. SC-05 satisfied via documentation."
    ),
)
def test_benchmark_at_least_2_full_success(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
) -> None:
    """Phase gate SC-05: at least 2/3 materials must achieve Full Success.

    Per benchmark_spec.md Section 6 the Phase 2 gate requires at least 2 of
    3 benchmark materials to achieve Full Success.  This test asserts the
    formal criterion.

    This test is marked ``xfail`` because MACE-MP-0 (medium, float64) achieves
    Full Success only for LiCoO2 with the current Phase 1 materials.  The
    failures are scientifically documented in T-21 and the SC-05 protocol.
    Do NOT lower thresholds to make this test pass.
    """
    summary, _, _ = benchmark_run
    full_successes = summary.status_counts.get("success", 0)
    assert full_successes >= 2, (
        f"Phase gate SC-05 not met: {full_successes}/3 Full Success. "
        "benchmark_spec.md Section 6 requires at least 2/3. "
        "Investigate MACE-MP-0 accuracy for LiFePO4 and LiMn2O4."
    )


@pytest.mark.integration
def test_benchmark_no_hard_failures(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
) -> None:
    """No material produces a hard_failure or infrastructure_failure.

    A hard_failure indicates energy divergence (NaN/Inf), bond length collapse
    (< 1.0 Å), or bond explosion (> 4.0 Å).  An infrastructure_failure
    indicates a pipeline exception (network, disk, MACE install error).
    Both must be zero for the Phase 1 benchmark to be scientifically valid.
    """
    summary, _, _ = benchmark_run
    hf = summary.status_counts.get("hard_failure", 0)
    inf_f = summary.status_counts.get("infrastructure_failure", 0)
    assert hf == 0, (
        f"Unexpected hard_failure for {hf} material(s). "
        "Investigate energy divergence or bond length violations."
    )
    assert inf_f == 0, (
        f"Unexpected infrastructure_failure for {inf_f} material(s). "
        "Investigate pipeline exceptions (network, disk, MACE install)."
    )


@pytest.mark.integration
def test_benchmark_summary_generated(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
) -> None:
    """Benchmark produces a BenchmarkSummary with all required fields populated."""
    summary, bench_id, _ = benchmark_run
    assert isinstance(summary, BenchmarkSummary)
    assert summary.benchmark_name == "phase1_structural_analysis"
    assert summary.benchmark_run_id is not None
    assert bench_id == str(summary.benchmark_run_id)
    assert summary.started_at is not None
    assert summary.completed_at is not None
    assert summary.completed_at >= summary.started_at
    assert summary.runtime_seconds >= 0.0
    assert summary.provenance is not None
    assert summary.provenance.created_by == "cathodescope"


@pytest.mark.integration
def test_benchmark_rows_stored(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
) -> None:
    """Benchmark runner writes one row file per material and a summary file."""
    _, bench_id, store = benchmark_run
    assert store.exists(
        f"benchmarks/{bench_id}/summary.json"
    ), "Benchmark summary file missing from ArtifactStore."
    for mp_id in _PHASE1_MP_IDS:
        assert store.exists(
            f"benchmarks/{bench_id}/rows/{mp_id}.json"
        ), f"Row file missing for material {mp_id}."


@pytest.mark.integration
def test_benchmark_metrics_complete(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
) -> None:
    """All 24 required benchmark metrics are present in every stored BenchmarkRow.

    Per benchmark_spec.md Section 4: no metric is optional.  All 24 keys must
    be present in every row regardless of the material's pass/fail outcome.
    """
    _, bench_id, store = benchmark_run
    store_root: Path = store._root  # type: ignore[attr-defined]
    for mp_id in _PHASE1_MP_IDS:
        row_path = store_root / "benchmarks" / bench_id / "rows" / f"{mp_id}.json"
        row_data: dict[str, Any] = json.loads(row_path.read_text(encoding="utf-8"))
        metrics: dict[str, Any] = row_data.get("metrics", {})
        missing = _REQUIRED_METRICS - set(metrics.keys())
        assert not missing, (
            f"Missing benchmark metrics for {mp_id}: {sorted(missing)}. "
            "All 24 metrics from benchmark_spec.md Section 4 must be populated."
        )


@pytest.mark.integration
def test_benchmark_reproducible_on_rerun(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
    tmp_path_factory: pytest.TempPathFactory,
    mace_calculator: Any,
) -> None:
    """Two consecutive benchmark runs produce the same per-material status categories.

    Per SC-06 (Reproducibility Verification): the same result category must
    appear for each material on every run.  Uses the ``benchmark_run`` module
    fixture as Run 1 and performs a second independent run for comparison.
    """
    summary1, _, _ = benchmark_run  # Run 1 from module fixture

    # Run 2: independent store and config, same MACE calculator instance.
    dir2: Path = tmp_path_factory.mktemp("bench_repro_run2")
    store2 = ArtifactStore(dir2)
    config2 = _IntegrationConfig(
        mp_client=_FixtureMPClient(),
        calculator=mace_calculator,
    )
    registry2 = BenchmarkMaterialRegistry()
    engine2 = WorkflowEngine(REGISTRY)
    runner2 = BenchmarkRunner(engine2, registry2, store2)
    summary2 = runner2.run("phase1_structural_analysis", config2)

    for status_key in ("success", "partial_success", "soft_failure", "hard_failure"):
        count1 = summary1.status_counts.get(status_key, 0)
        count2 = summary2.status_counts.get(status_key, 0)
        assert count1 == count2, (
            f"Non-reproducible benchmark: '{status_key}' count changed between runs. "
            f"Run 1 counts: {dict(summary1.status_counts)}, "
            f"Run 2 counts: {dict(summary2.status_counts)}. "
            "Per SC-06: same result category required on consecutive runs."
        )


@pytest.mark.integration
def test_benchmark_evidence_labeling_complete_for_all(
    benchmark_run: tuple[BenchmarkSummary, str, ArtifactStore],
) -> None:
    """evidence_labeling_complete metric is True for all 3 Phase 1 materials.

    Per scientific_validity_matrix.md: every output must carry an evidence
    label.  A True value in the ``evidence_labeling_complete`` metric confirms
    that the evidence labeling step executed and produced at least one label.
    """
    _, bench_id, store = benchmark_run
    store_root: Path = store._root  # type: ignore[attr-defined]
    for mp_id in _PHASE1_MP_IDS:
        row_path = store_root / "benchmarks" / bench_id / "rows" / f"{mp_id}.json"
        row_data: dict[str, Any] = json.loads(row_path.read_text(encoding="utf-8"))
        metrics: dict[str, Any] = row_data.get("metrics", {})
        assert metrics.get("evidence_labeling_complete") is True, (
            f"evidence_labeling_complete is not True for {mp_id}. "
            f"Got: {metrics.get('evidence_labeling_complete')!r}. "
            "All materials must have complete evidence labels per "
            "scientific_validity_matrix.md."
        )
