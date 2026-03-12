"""Benchmark regression comparison tool.

Implements compare_benchmarks(rows_a, rows_b) -> RegressionReport, which
detects status changes, metric deltas, new failures, and new successes
between two benchmark runs.

Implemented in T-24b.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from cathodescope.models.reports import BenchmarkRow, BenchmarkStatus

# Severity ranking: higher value = worse outcome.
_STATUS_SEVERITY: dict[str, int] = {
    "success": 0,
    "partial_success": 1,
    "soft_failure": 2,
    "hard_failure": 3,
    "infrastructure_failure": 4,
}

_PASSING = frozenset({"success", "partial_success"})
_FAILING = frozenset({"soft_failure", "hard_failure", "infrastructure_failure"})


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class StatusChange(BaseModel):
    """Per-material status comparison between two benchmark runs.

    Records the material identity, the status from each run, and whether
    the change represents a regression (status got worse).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "material_id": "mp-22526",
                "formula": "LiCoO2",
                "status_before": "success",
                "status_after": "partial_success",
                "is_regression": True,
            }
        }
    )

    material_id: str = Field(description="Materials Project ID of the material.")
    formula: str = Field(description="Chemical formula of the material.")
    status_before: BenchmarkStatus = Field(
        description="Benchmark status in run A (the baseline)."
    )
    status_after: BenchmarkStatus = Field(
        description="Benchmark status in run B (the candidate)."
    )
    is_regression: bool = Field(
        description=(
            "True when the status severity increased between runs "
            "(i.e. the outcome got worse)."
        )
    )


class RegressionReport(BaseModel):
    """Comparison report between two benchmark runs.

    Identifies per-material status changes, materials that newly started
    failing or passing, numeric metric deltas, and materials absent from
    one of the two runs.

    Produced by :func:`compare_benchmarks`.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_regression": True,
                "status_changes": [],
                "new_failures": ["mp-22526"],
                "new_successes": [],
                "metric_deltas": {"mp-22526": {"lattice_param_deviation_a": 0.5}},
                "missing_in_b": [],
                "missing_in_a": [],
            }
        }
    )

    is_regression: bool = Field(
        description=(
            "True if any material's status became worse between run A and run B."
        )
    )
    status_changes: list[StatusChange] = Field(
        default_factory=list,
        description="All materials whose status differed between the two runs.",
    )
    new_failures: list[str] = Field(
        default_factory=list,
        description=(
            "Material IDs that were passing (success or partial_success) in run A "
            "but failing (soft_failure, hard_failure, or infrastructure_failure) "
            "in run B."
        ),
    )
    new_successes: list[str] = Field(
        default_factory=list,
        description=("Material IDs that were failing in run A but passing in run B."),
    )
    metric_deltas: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "Per-material numeric metric deltas: "
            "{material_id: {metric_key: (b_value − a_value)}}. "
            "Only numeric (int/float) metrics are included."
        ),
    )
    missing_in_b: list[str] = Field(
        default_factory=list,
        description="Material IDs present in run A but absent from run B.",
    )
    missing_in_a: list[str] = Field(
        default_factory=list,
        description="Material IDs present in run B but absent from run A.",
    )


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------


def compare_benchmarks(
    rows_a: list[BenchmarkRow],
    rows_b: list[BenchmarkRow],
) -> RegressionReport:
    """Compare two benchmark runs and produce a :class:`RegressionReport`.

    Matches materials by ``material_id`` across the two runs. For each
    matched pair it records any status change, computes numeric metric
    deltas (B minus A), and classifies new failures and new successes.
    Materials absent from one run are reported in ``missing_in_a`` or
    ``missing_in_b`` without contributing to failure/success counts.

    Parameters
    ----------
    rows_a:
        Benchmark rows from the baseline run (run A).
    rows_b:
        Benchmark rows from the candidate run (run B).

    Returns
    -------
    RegressionReport
        Structured comparison including status changes, metric deltas,
        new failures, new successes, and missing-material lists.
    """
    map_a: dict[str, BenchmarkRow] = {r.material_id: r for r in rows_a}
    map_b: dict[str, BenchmarkRow] = {r.material_id: r for r in rows_b}

    ids_a = set(map_a)
    ids_b = set(map_b)
    common = ids_a & ids_b

    missing_in_b = sorted(ids_a - ids_b)
    missing_in_a = sorted(ids_b - ids_a)

    status_changes: list[StatusChange] = []
    new_failures: list[str] = []
    new_successes: list[str] = []
    metric_deltas: dict[str, dict[str, Any]] = {}

    for mid in sorted(common):
        row_a = map_a[mid]
        row_b = map_b[mid]

        sev_a = _STATUS_SEVERITY[row_a.status]
        sev_b = _STATUS_SEVERITY[row_b.status]

        if row_a.status != row_b.status:
            status_changes.append(
                StatusChange(
                    material_id=mid,
                    formula=row_a.formula,
                    status_before=row_a.status,
                    status_after=row_b.status,
                    is_regression=sev_b > sev_a,
                )
            )
            if row_a.status in _PASSING and row_b.status in _FAILING:
                new_failures.append(mid)
            elif row_a.status in _FAILING and row_b.status in _PASSING:
                new_successes.append(mid)

        deltas = _numeric_deltas(row_a.metrics, row_b.metrics)
        if deltas:
            metric_deltas[mid] = deltas

    is_regression = any(sc.is_regression for sc in status_changes)

    return RegressionReport(
        is_regression=is_regression,
        status_changes=status_changes,
        new_failures=new_failures,
        new_successes=new_successes,
        metric_deltas=metric_deltas,
        missing_in_b=missing_in_b,
        missing_in_a=missing_in_a,
    )


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _numeric_deltas(
    metrics_a: dict[str, Any],
    metrics_b: dict[str, Any],
) -> dict[str, float]:
    """Return B-minus-A deltas for all numeric keys present in both dicts.

    Keys whose value in either dict is not ``int`` or ``float`` are silently
    skipped (booleans are excluded even though they are a subtype of ``int``).
    """
    deltas: dict[str, float] = {}
    all_keys = set(metrics_a) | set(metrics_b)
    for key in all_keys:
        val_a = metrics_a.get(key)
        val_b = metrics_b.get(key)
        # Exclude bool (subtype of int) and non-numeric types.
        if (
            isinstance(val_a, int | float)
            and not isinstance(val_a, bool)
            and isinstance(val_b, int | float)
            and not isinstance(val_b, bool)
        ):
            deltas[key] = float(val_b) - float(val_a)
    return deltas
