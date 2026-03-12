"""Benchmark runner.

Implements BenchmarkRunner: runs a named workflow across all benchmark
materials, collects BenchmarkRows, assembles and stores BenchmarkSummary.

Implemented in T-23.
"""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime
from typing import Any

from cathodescope.benchmark.registry import BenchmarkMaterialRegistry
from cathodescope.models.provenance import create_provenance
from cathodescope.models.reports import (
    BenchmarkRow,
    BenchmarkStatus,
    BenchmarkSummary,
    FailureCategory,
)
from cathodescope.models.results import WorkflowResult
from cathodescope.provenance.store import ArtifactStore
from cathodescope.workflows.engine import WorkflowEngine

_TOOL_NAME = "benchmark_runner"
_TOOL_VERSION = "0.1.0"

# All 24 metric keys required by benchmark_spec.md Section 4.
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

_ALL_STATUSES: tuple[str, ...] = (
    "success",
    "partial_success",
    "soft_failure",
    "hard_failure",
    "infrastructure_failure",
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class BenchmarkRunner:
    """Orchestrate a workflow across all benchmark materials and collect results.

    The runner iterates over the materials in a named benchmark set, calls the
    workflow engine for each material, extracts the 24 metrics defined in
    ``benchmark_spec.md`` Section 4, classifies each run, and assembles a
    :class:`~cathodescope.models.reports.BenchmarkSummary`.

    Individual material failures (exceptions from the engine) are caught,
    classified as ``infrastructure_failure``, and recorded. They never abort
    the benchmark run.

    Parameters
    ----------
    engine:
        The :class:`~cathodescope.workflows.engine.WorkflowEngine` to dispatch
        workflow runs through.
    registry:
        The :class:`~cathodescope.benchmark.registry.BenchmarkMaterialRegistry`
        providing the material list for each benchmark set.
    store:
        The :class:`~cathodescope.provenance.store.ArtifactStore` for writing
        benchmark rows and summaries.
    workflow_name:
        Name of the registered workflow to run for each material.
    workflow_version:
        Version string of the workflow (recorded in every ``BenchmarkRow``).
    """

    def __init__(
        self,
        engine: WorkflowEngine,
        registry: BenchmarkMaterialRegistry,
        store: ArtifactStore,
        workflow_name: str = "structural_analysis",
        workflow_version: str = "0.1.0",
    ) -> None:
        self._engine = engine
        self._registry = registry
        self._store = store
        self._workflow_name = workflow_name
        self._workflow_version = workflow_version

    def run(self, benchmark_name: str, config: Any) -> BenchmarkSummary:
        """Run the benchmark for all materials in *benchmark_name*.

        For each material, the engine is called with the configured workflow.
        If the engine raises, the material is recorded as
        ``infrastructure_failure`` and the next material is processed.

        Parameters
        ----------
        benchmark_name:
            Key into the ``BenchmarkMaterialRegistry``, e.g.
            ``"phase1_structural_analysis"``.
        config:
            Configuration passed to the workflow engine for each run.
            Accepts :class:`~cathodescope.config.settings.CathodescopeSettings`
            or a plain dict.

        Returns
        -------
        BenchmarkSummary
            Aggregated summary with one
            :class:`~cathodescope.models.reports.BenchmarkRow`
            per material stored as a side-effect.
        """
        materials = self._registry.get_materials(benchmark_name)
        benchmark_run_id = uuid.uuid4()
        started_at = datetime.now(UTC)

        rows: list[BenchmarkRow] = []
        row_paths: list[str] = []

        for material_spec in materials:
            row = self._run_one_material(benchmark_run_id, material_spec, config)
            rows.append(row)

            material_id = material_spec["mp_id"]
            self._store.write_benchmark_row(
                str(benchmark_run_id),
                material_id,
                row.model_dump(mode="json"),
            )
            row_paths.append(f"rows/{material_id}.json")

        completed_at = datetime.now(UTC)
        runtime_seconds = (completed_at - started_at).total_seconds()

        status_counts: dict[str, int] = {s: 0 for s in _ALL_STATUSES}
        for row in rows:
            status_counts[row.status] += 1

        provenance = create_provenance(
            created_by="cathodescope",
            tool_name=_TOOL_NAME,
            tool_version=_TOOL_VERSION,
            elapsed_seconds=runtime_seconds,
        )

        summary = BenchmarkSummary(
            benchmark_run_id=benchmark_run_id,
            benchmark_name=benchmark_name,
            materials_count=len(rows),
            status_counts=status_counts,
            rows=row_paths,
            started_at=started_at,
            completed_at=completed_at,
            runtime_seconds=runtime_seconds,
            provenance=provenance,
        )

        self._store.write_benchmark_summary(
            str(benchmark_run_id),
            summary.model_dump(mode="json"),
        )

        return summary

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_one_material(
        self,
        benchmark_run_id: uuid.UUID,
        material_spec: dict[str, Any],
        config: Any,
    ) -> BenchmarkRow:
        """Run the workflow for one material, returning a :class:`BenchmarkRow`.

        Catches all exceptions and converts them to ``infrastructure_failure``
        rows so that a single material failure never aborts the benchmark.
        """
        timestamp = datetime.now(UTC)
        material_id = material_spec["mp_id"]
        formula = material_spec["formula"]
        family = material_spec["family"]

        try:
            wf_result = self._engine.run(self._workflow_name, material_spec, config)
            metrics = self._extract_metrics(wf_result)
            status: BenchmarkStatus = classify_benchmark_status(metrics)
            failure_category: FailureCategory | None = None
        except Exception as exc:  # noqa: BLE001
            metrics = {k: None for k in _REQUIRED_METRICS}
            metrics["runtime_seconds"] = 0.0
            metrics["workflow_version"] = self._workflow_version
            status = "infrastructure_failure"
            failure_category = _classify_exception(exc)

        provenance = create_provenance(
            created_by="cathodescope",
            tool_name=_TOOL_NAME,
            tool_version=_TOOL_VERSION,
        )

        return BenchmarkRow(
            benchmark_run_id=benchmark_run_id,
            material_id=material_id,
            formula=formula,
            family=family,
            workflow_name=self._workflow_name,
            workflow_version=self._workflow_version,
            status=status,
            metrics=metrics,
            failure_category=failure_category,
            timestamp=timestamp,
            provenance=provenance,
        )

    def _extract_metrics(self, wf_result: WorkflowResult) -> dict[str, Any]:
        """Merge metrics from all step ``data`` dicts in *wf_result*.

        The runner merges ``tool_result.data`` from every completed step.
        Later steps override earlier steps for duplicate keys. After merging,
        the runner overwrites ``runtime_seconds`` and ``workflow_version``
        with authoritative values derived from the workflow result and the
        runner's own configuration.
        """
        metrics: dict[str, Any] = {}
        for step in wf_result.steps:
            if step.tool_result.data:
                metrics.update(step.tool_result.data)

        # Runner-authoritative fields (always override step-provided values).
        if wf_result.started_at is not None and wf_result.completed_at is not None:
            metrics["runtime_seconds"] = (
                wf_result.completed_at - wf_result.started_at
            ).total_seconds()
        else:
            metrics.setdefault("runtime_seconds", 0.0)

        metrics["workflow_version"] = self._workflow_version
        return metrics


# ---------------------------------------------------------------------------
# Classification helpers (module-level, reusable by tests)
# ---------------------------------------------------------------------------


def classify_benchmark_status(metrics: dict[str, Any]) -> BenchmarkStatus:
    """Classify a benchmark run from its metric values.

    Applies the formal threshold table from ``benchmark_spec.md`` Section 5.
    Classification is determined by the worst metric outcome. ``None`` values
    (missing metrics) are skipped — they do not trigger failure on their own.

    Parameters
    ----------
    metrics:
        Dict of the 24 benchmark metrics. Keys with ``None`` values are ignored
        during threshold evaluation.

    Returns
    -------
    BenchmarkStatus
        One of ``"success"``, ``"partial_success"``, ``"soft_failure"``,
        ``"hard_failure"``.  Callers are responsible for classifying
        ``"infrastructure_failure"`` before this function is reached.
    """
    # --- Hard failure: NaN/Inf energy ---
    final_energy = metrics.get("final_energy")
    if isinstance(final_energy, float) and (
        math.isnan(final_energy) or math.isinf(final_energy)
    ):
        return "hard_failure"

    # --- Hard failure: bond lengths out of hard bounds ---
    min_bond = metrics.get("min_bond_length")
    max_bond = metrics.get("max_bond_length")
    if isinstance(min_bond, float) and min_bond < 1.0:
        return "hard_failure"
    if isinstance(max_bond, float) and max_bond > 4.0:
        return "hard_failure"

    # --- Lattice parameter deviations ---
    worst_lat = 0.0
    for key in (
        "lattice_param_deviation_a",
        "lattice_param_deviation_b",
        "lattice_param_deviation_c",
    ):
        val = metrics.get(key)
        if isinstance(val, (int, float)):
            if math.isnan(val):
                return "hard_failure"
            worst_lat = max(worst_lat, abs(val))

    if worst_lat >= 10.0:
        return "hard_failure"

    # --- Volume deviation ---
    vol_dev = metrics.get("volume_deviation")
    vol_abs = 0.0
    if isinstance(vol_dev, (int, float)) and not math.isnan(vol_dev):
        vol_abs = abs(vol_dev)
        if vol_abs >= 20.0:
            return "hard_failure"

    # --- Soft failure: symmetry broken ---
    if metrics.get("symmetry_preserved") is False:
        return "soft_failure"

    # --- Soft failure: lattice 5–10% or volume 10–20% ---
    if worst_lat >= 5.0 or vol_abs >= 10.0:
        return "soft_failure"

    # --- Angle deviations ---
    worst_angle = 0.0
    angle_keys = (
        "angle_deviation_alpha",
        "angle_deviation_beta",
        "angle_deviation_gamma",
    )
    for key in angle_keys:
        val = metrics.get(key)
        if isinstance(val, (int, float)):
            worst_angle = max(worst_angle, abs(val))

    if worst_angle >= 3.0:
        return "soft_failure"

    # --- Partial success: lattice 2–5%, volume 5–10%, or angle 1–3° ---
    if worst_lat >= 2.0 or vol_abs >= 5.0 or worst_angle >= 1.0:
        return "partial_success"

    return "success"


def _classify_exception(exc: Exception) -> FailureCategory:
    """Map an exception to the closest :data:`FailureCategory`.

    Uses simple keyword matching against the exception message and type name.
    Falls back to ``"unknown_failure"`` when no pattern matches.
    """
    msg = str(exc).lower()
    exc_type = type(exc).__name__.lower()
    combined = f"{exc_type} {msg}"

    retrieval_kws = ("network", "timeout", "connection", "api", "http", "retriev")
    if any(kw in combined for kw in retrieval_kws):
        return "retrieval_failure"
    if any(kw in combined for kw in ("converg", "fmax", "relax")):
        return "convergence_failure"
    artifact_kws = ("disk", "permission", "storage", "artifact", "write", "io")
    if any(kw in combined for kw in artifact_kws):
        return "artifact_failure"
    if any(kw in combined for kw in ("valid", "physics", "symmetr")):
        return "validation_failure"
    return "unknown_failure"
