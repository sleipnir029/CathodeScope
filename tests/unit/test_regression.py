"""Regression tests for T-29.

Compares current pipeline output against golden outputs captured by
``scripts/capture_fixtures.py`` to catch unintended behavioral changes
across refactors.

Golden files in ``tests/fixtures/expected_outputs/``:

* ``licoo2_workflow_result.json`` — full WorkflowResult
* ``licoo2_report.json``          — ReportRecord from step 6
* ``benchmark_summary.json``      — BenchmarkSummary (status counts)

All tests use ``_MockZeroForceCalc`` (zero forces → immediate FIRE
convergence) so they run entirely offline without MACE and produce
deterministic output identical to the committed golden captures.

Non-deterministic fields (UUIDs, timestamps, hostnames) are excluded from
comparison.  Numerical fields use ``pytest.approx(abs=0.01)``.  String
fields (section headings, evidence labels, metric keys) are compared exactly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from ase.calculators.calculator import Calculator

from cathodescope.benchmark.registry import BenchmarkMaterialRegistry
from cathodescope.benchmark.runner import BenchmarkRunner
from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ErrorRecord, ToolResult
from cathodescope.provenance.store import ArtifactStore
from cathodescope.workflows.engine import WorkflowEngine
from cathodescope.workflows.structural_analysis import REGISTRY

_GOLDEN_DIR = Path(__file__).parent.parent / "fixtures" / "expected_outputs"
_MP_FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "mp_responses"

_FORMULA_TO_MP_ID: dict[str, str] = {
    "LiCoO2": "mp-22526",
    "LiFePO4": "mp-19017",
    "LiMn2O4": "mp-18767",
}


# ---------------------------------------------------------------------------
# Deterministic mock calculator (zero forces → FIRE converges on step 0)
# ---------------------------------------------------------------------------


class _MockZeroForceCalc(Calculator):
    """Return zero forces on every call → FIRE converges immediately.

    Energy is fixed at -10.0 eV.  The structure is never moved, so lattice
    parameters after relaxation are identical to the normalised input and all
    deviations relative to the MP reference are 0.0.
    """

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self) -> None:
        """Initialise ASE calculator with result caching enabled."""
        super().__init__()  # type: ignore[no-untyped-call]
        self.use_cache = True

    def calculate(
        self,
        atoms: Any = None,
        properties: Any = None,
        system_changes: Any = None,
    ) -> None:
        """Set constant energy −10 eV, zero forces, and zero stress."""
        n = len(atoms)
        self.results = {
            "energy": -10.0,
            "forces": np.zeros((n, 3)),
            "stress": np.zeros(6),
        }


# ---------------------------------------------------------------------------
# Offline MP client (reads local fixture JSON files)
# ---------------------------------------------------------------------------


class _OfflineMPClient:
    """Offline MP client backed by committed fixture JSON files.

    Satisfies the ``_MPClientProtocol`` duck-type expected by
    ``cathodescope.tools.input_resolver``.
    """

    def fetch_by_mp_id(self, mp_id: str) -> ToolResult:
        """Return a success ToolResult loaded from the fixture file."""
        fixture_path = _MP_FIXTURE_DIR / f"{mp_id}.json"
        data: dict[str, Any] = json.loads(
            fixture_path.read_text(encoding="utf-8")
        )
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
        """Resolve formula → mp_id via the local look-up table."""
        mp_id = _FORMULA_TO_MP_ID.get(formula)
        if mp_id:
            return self.fetch_by_mp_id(mp_id)
        return ToolResult(
            tool_name="mp_client",
            status="failure",
            error=ErrorRecord(
                error_type="InputError",
                message=f"No offline fixture for formula {formula!r}",
                source="_OfflineMPClient",
            ),
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="mp_client",
                tool_version="0.1.0",
            ),
        )


# ---------------------------------------------------------------------------
# Minimal config duck-type (no CathodescopeSettings dependency)
# ---------------------------------------------------------------------------


@dataclass
class _MockConfig:
    """Minimal config for regression tests.

    Injects ``_OfflineMPClient`` and ``_MockZeroForceCalc`` so the workflow
    steps use dependency injection instead of constructing live instances.
    """

    mp_client: Any = field(default_factory=_OfflineMPClient)
    calculator: Any = field(default_factory=_MockZeroForceCalc)

    def model_dump(self, *, mode: str = "json") -> dict[str, Any]:
        """Return a minimal config snapshot for provenance recording."""
        return {
            "mode": "regression_test",
            "mp_client": "offline_fixture",
            "calculator": "mock_zero_force",
        }


# ---------------------------------------------------------------------------
# Module-scoped fixtures (pipeline runs once per module)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def licoo2_workflow_result() -> Any:
    """Run the LiCoO2 structural_analysis workflow once with mock calculator."""
    engine = WorkflowEngine(REGISTRY)
    config = _MockConfig()
    return engine.run("structural_analysis", "mp-22526", config)


@pytest.fixture(scope="module")
def golden_workflow_result() -> dict[str, Any]:
    """Load the committed golden WorkflowResult fixture."""
    data: dict[str, Any] = json.loads(
        (_GOLDEN_DIR / "licoo2_workflow_result.json").read_text(encoding="utf-8")
    )
    return data


@pytest.fixture(scope="module")
def golden_report() -> dict[str, Any]:
    """Load the committed golden ReportRecord fixture."""
    data: dict[str, Any] = json.loads(
        (_GOLDEN_DIR / "licoo2_report.json").read_text(encoding="utf-8")
    )
    return data


@pytest.fixture(scope="module")
def golden_benchmark_summary() -> dict[str, Any]:
    """Load the committed golden BenchmarkSummary fixture."""
    data: dict[str, Any] = json.loads(
        (_GOLDEN_DIR / "benchmark_summary.json").read_text(encoding="utf-8")
    )
    return data


# ---------------------------------------------------------------------------
# Helper: find a step by name
# ---------------------------------------------------------------------------


def _get_step(wf_result: Any, step_name: str) -> Any:
    """Return the StepResult whose step_name matches *step_name*."""
    for step in wf_result.steps:
        if step.step_name == step_name:
            return step
    raise KeyError(f"Step {step_name!r} not found in workflow result")


# ---------------------------------------------------------------------------
# T-29 regression tests
# ---------------------------------------------------------------------------


def test_licoo2_workflow_result_matches_golden(
    licoo2_workflow_result: Any,
    golden_workflow_result: dict[str, Any],
) -> None:
    """WorkflowResult pipeline output matches golden for LiCoO2.

    Compares workflow_name, status, step count, step names, step statuses,
    final energy, relaxation convergence, and lattice/volume deviations.
    UUIDs and timestamps are excluded from comparison.  Numerical values use
    ``pytest.approx(abs=0.01)``.
    """
    actual = licoo2_workflow_result
    golden = golden_workflow_result

    # Workflow-level scalar fields
    assert actual.workflow_name == golden["workflow_name"]
    assert actual.status == golden["status"]
    assert len(actual.steps) == len(golden["steps"])

    # Step names and statuses must match in order
    for act_step, gld_step in zip(actual.steps, golden["steps"]):
        assert act_step.step_name == gld_step["step_name"], (
            f"Step name mismatch: actual={act_step.step_name!r}, "
            f"golden={gld_step['step_name']!r}"
        )
        assert act_step.tool_result.status == gld_step["tool_result"]["status"], (
            f"Step {act_step.step_name!r} status mismatch: "
            f"actual={act_step.tool_result.status!r}, "
            f"golden={gld_step['tool_result']['status']!r}"
        )

    # Relax step: final_energy and convergence
    relax_step = _get_step(actual, "relax")
    gld_relax_step = next(
        s for s in golden["steps"] if s["step_name"] == "relax"
    )
    rel_data = relax_step.tool_result.data or {}
    gld_rel_data = gld_relax_step["tool_result"]["data"]

    assert rel_data.get("final_energy") == pytest.approx(
        gld_rel_data["final_energy"], abs=0.01
    ), (
        f"final_energy mismatch: "
        f"{rel_data.get('final_energy')} vs {gld_rel_data['final_energy']}"
    )

    conv = rel_data.get("convergence_info", {})
    gld_conv = gld_rel_data["convergence_info"]
    assert conv.get("converged") == gld_conv["converged"]
    assert conv.get("steps") == gld_conv["steps"]

    # Compare-reference step: lattice deviations, volume deviation, symmetry
    cmp_step = _get_step(actual, "compare_reference")
    gld_cmp_step = next(
        s for s in golden["steps"] if s["step_name"] == "compare_reference"
    )
    cmp_data = cmp_step.tool_result.data or {}
    gld_cmp_data = gld_cmp_step["tool_result"]["data"]

    lat = cmp_data.get("lattice_deviations", {})
    gld_lat = gld_cmp_data["lattice_deviations"]
    for axis in ("a", "b", "c"):
        assert lat.get(axis) == pytest.approx(gld_lat[axis], abs=0.01), (
            f"lattice_deviations[{axis!r}] mismatch: {lat.get(axis)} vs {gld_lat[axis]}"
        )

    assert cmp_data.get("volume_deviation") == pytest.approx(
        gld_cmp_data["volume_deviation"], abs=0.01
    )
    assert cmp_data.get("symmetry_preserved") == gld_cmp_data["symmetry_preserved"]
    assert (
        cmp_data.get("reference_space_group") == gld_cmp_data["reference_space_group"]
    )
    assert cmp_data.get("relaxed_space_group") == gld_cmp_data["relaxed_space_group"]


def test_licoo2_report_sections_match_golden(
    licoo2_workflow_result: Any,
    golden_report: dict[str, Any],
) -> None:
    """Report sections from pipeline match golden for LiCoO2.

    Compares report-level scalar fields (title, report_type, raw_user_input,
    schema_version) and, for each section, the heading and evidence_labels.
    Section data contents are NOT compared deeply — only structural fields
    that would break if a section were added, removed, or renamed.
    """
    report_step = _get_step(licoo2_workflow_result, "generate_report")
    report_data = report_step.tool_result.data or {}
    actual_report = report_data["report_json"]
    golden = golden_report

    # Scalar report-level fields (no UUIDs or timestamps)
    assert actual_report["title"] == golden["title"]
    assert actual_report["report_type"] == golden["report_type"]
    assert actual_report["raw_user_input"] == golden["raw_user_input"]
    assert actual_report["schema_version"] == golden["schema_version"]

    # Section count and structure
    actual_sections = actual_report.get("sections", [])
    golden_sections = golden.get("sections", [])
    assert len(actual_sections) == len(golden_sections), (
        f"Section count mismatch: actual={len(actual_sections)}, "
        f"golden={len(golden_sections)}"
    )

    for i, (act_sec, gld_sec) in enumerate(
        zip(actual_sections, golden_sections)
    ):
        assert act_sec["heading"] == gld_sec["heading"], (
            f"Section {i} heading mismatch: "
            f"actual={act_sec['heading']!r}, golden={gld_sec['heading']!r}"
        )
        assert sorted(act_sec["evidence_labels"]) == sorted(
            gld_sec["evidence_labels"]
        ), (
            f"Section {i} ({act_sec['heading']!r}) evidence_labels mismatch: "
            f"actual={sorted(act_sec['evidence_labels'])}, "
            f"golden={sorted(gld_sec['evidence_labels'])}"
        )


def test_licoo2_evidence_summary_matches_golden(
    licoo2_workflow_result: Any,
    golden_report: dict[str, Any],
) -> None:
    """Evidence summary counts from pipeline match golden for LiCoO2.

    Compares the per-label counts in ``evidence_summary`` exactly.  This
    detects regressions where a step silently drops or duplicates an evidence
    label assignment.
    """
    report_step = _get_step(licoo2_workflow_result, "generate_report")
    report_data = report_step.tool_result.data or {}
    actual_summary: dict[str, Any] = report_data.get("evidence_summary", {})
    golden_summary: dict[str, Any] = golden_report["evidence_summary"]

    # Same label keys
    assert set(actual_summary.keys()) == set(golden_summary.keys()), (
        f"Evidence summary keys differ: "
        f"actual={sorted(actual_summary.keys())}, "
        f"golden={sorted(golden_summary.keys())}"
    )

    # Same count for each label
    for label, expected_count in golden_summary.items():
        assert actual_summary[label] == expected_count, (
            f"Evidence label {label!r}: expected count {expected_count}, "
            f"got {actual_summary[label]}"
        )


def test_benchmark_row_metrics_match_golden(
    tmp_path: Path,
    golden_benchmark_summary: dict[str, Any],
) -> None:
    """LiCoO2 benchmark row metrics match golden and summary counts match golden.

    Runs the Phase 1 benchmark with the mock zero-force calculator, reads the
    stored LiCoO2 row, and asserts key numerical metrics.  With a zero-force
    calculator the relaxation leaves all lattice parameters unchanged, so all
    deviation metrics must be 0.0.

    Also asserts that the ``BenchmarkSummary`` status counts and benchmark_name
    match the committed golden summary exactly.
    """
    store = ArtifactStore(tmp_path)
    engine = WorkflowEngine(REGISTRY)
    registry = BenchmarkMaterialRegistry()
    runner = BenchmarkRunner(engine, registry, store)
    config = _MockConfig()

    summary = runner.run("phase1_structural_analysis", config)

    # Benchmark summary scalar fields match golden (UUIDs/timestamps excluded)
    assert summary.benchmark_name == golden_benchmark_summary["benchmark_name"]
    assert summary.materials_count == golden_benchmark_summary["materials_count"]
    assert summary.status_counts == golden_benchmark_summary["status_counts"]

    # Read LiCoO2 row from the ArtifactStore
    bench_id = str(summary.benchmark_run_id)
    store_root: Path = store._root  # noqa: SLF001
    row_path = store_root / "benchmarks" / bench_id / "rows" / "mp-22526.json"
    row_data: dict[str, Any] = json.loads(row_path.read_text(encoding="utf-8"))
    metrics: dict[str, Any] = row_data.get("metrics", {})

    # Zero-force mock: all lattice deviations must be 0.0
    assert metrics.get("lattice_param_deviation_a") == pytest.approx(0.0, abs=0.01)
    assert metrics.get("lattice_param_deviation_b") == pytest.approx(0.0, abs=0.01)
    assert metrics.get("lattice_param_deviation_c") == pytest.approx(0.0, abs=0.01)
    assert metrics.get("volume_deviation") == pytest.approx(0.0, abs=0.01)
    assert metrics.get("angle_deviation_alpha") == pytest.approx(0.0, abs=0.01)
    assert metrics.get("angle_deviation_beta") == pytest.approx(0.0, abs=0.01)
    assert metrics.get("angle_deviation_gamma") == pytest.approx(0.0, abs=0.01)

    # Zero-force mock: relaxation converges on step 0, energy = -10.0
    assert metrics.get("final_energy") == pytest.approx(-10.0, abs=0.01)
    assert metrics.get("final_fmax") == pytest.approx(0.0, abs=1e-6)
    assert metrics.get("relaxation_convergence") is True
    assert metrics.get("relaxation_steps") == 0

    # LiCoO2 structural properties
    assert metrics.get("symmetry_preserved") is True
    assert metrics.get("space_group_output") == "R-3m"
    assert metrics.get("space_group_input") == "R-3m"

    # Pipeline completeness flags
    assert metrics.get("evidence_labeling_complete") is True
    assert metrics.get("report_generated") is True
    assert metrics.get("input_resolution") is True
    assert metrics.get("structure_retrieval") is True
    assert metrics.get("structure_normalization") is True
