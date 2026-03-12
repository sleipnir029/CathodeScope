"""Unit tests for cathodescope.benchmark.comparator.

Tests implemented in T-24b. All tests use in-memory BenchmarkRow objects;
no filesystem or real workflows are required.
"""

import uuid
from datetime import UTC, datetime

import pytest

from cathodescope.benchmark.comparator import RegressionReport, compare_benchmarks
from cathodescope.models.provenance import create_provenance
from cathodescope.models.reports import BenchmarkRow

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RUN_A = uuid.uuid4()
_RUN_B = uuid.uuid4()


def _prov() -> object:
    return create_provenance(
        created_by="cathodescope",
        tool_name="test",
        tool_version="0.1.0",
    )


def _row(
    material_id: str,
    formula: str,
    status: str,
    metrics: dict | None = None,
    benchmark_run_id: uuid.UUID | None = None,
) -> BenchmarkRow:
    return BenchmarkRow(
        benchmark_run_id=benchmark_run_id or uuid.uuid4(),
        material_id=material_id,
        formula=formula,
        family="layered_oxide",
        workflow_name="structural_analysis",
        workflow_version="0.1.0",
        status=status,  # type: ignore[arg-type]
        metrics=metrics
        or {
            "lattice_param_deviation_a": 0.5,
            "lattice_param_deviation_b": 0.5,
            "lattice_param_deviation_c": 0.5,
            "volume_deviation": 1.0,
            "final_energy": -42.0,
        },
        timestamp=datetime.now(UTC),
        provenance=_prov(),  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_compare_benchmarks_returns_regression_report() -> None:
    """compare_benchmarks must return a RegressionReport instance."""
    rows_a = [_row("mp-22526", "LiCoO2", "success")]
    rows_b = [_row("mp-22526", "LiCoO2", "success")]
    report = compare_benchmarks(rows_a, rows_b)
    assert isinstance(report, RegressionReport)


def test_compare_benchmarks_detects_status_change() -> None:
    """A material whose status differs between runs must appear in status_changes."""
    rows_a = [_row("mp-22526", "LiCoO2", "success")]
    rows_b = [_row("mp-22526", "LiCoO2", "partial_success")]
    report = compare_benchmarks(rows_a, rows_b)

    assert len(report.status_changes) == 1
    change = report.status_changes[0]
    assert change.material_id == "mp-22526"
    assert change.status_before == "success"
    assert change.status_after == "partial_success"


def test_compare_benchmarks_no_change_empty_status_changes() -> None:
    """Identical status across runs must produce an empty status_changes list."""
    rows_a = [
        _row("mp-22526", "LiCoO2", "success"),
        _row("mp-19017", "LiFePO4", "success"),
    ]
    rows_b = [
        _row("mp-22526", "LiCoO2", "success"),
        _row("mp-19017", "LiFePO4", "success"),
    ]
    report = compare_benchmarks(rows_a, rows_b)
    assert report.status_changes == []
    assert report.is_regression is False


def test_compare_benchmarks_flags_new_failures() -> None:
    """A material that was passing in A but failing in B must be in new_failures."""
    rows_a = [
        _row("mp-22526", "LiCoO2", "success"),
        _row("mp-19017", "LiFePO4", "partial_success"),
    ]
    rows_b = [
        _row("mp-22526", "LiCoO2", "hard_failure"),
        _row("mp-19017", "LiFePO4", "soft_failure"),
    ]
    report = compare_benchmarks(rows_a, rows_b)
    assert "mp-22526" in report.new_failures
    assert "mp-19017" in report.new_failures
    assert report.is_regression is True


def test_compare_benchmarks_flags_new_successes() -> None:
    """A material that was failing in A but passing in B must be in new_successes."""
    rows_a = [
        _row("mp-22526", "LiCoO2", "hard_failure"),
        _row("mp-18767", "LiMn2O4", "infrastructure_failure"),
    ]
    rows_b = [
        _row("mp-22526", "LiCoO2", "success"),
        _row("mp-18767", "LiMn2O4", "partial_success"),
    ]
    report = compare_benchmarks(rows_a, rows_b)
    assert "mp-22526" in report.new_successes
    assert "mp-18767" in report.new_successes
    assert report.new_failures == []


def test_compare_benchmarks_computes_metric_deltas() -> None:
    """Numeric metric deltas (b − a) must be recorded per material."""
    metrics_a = {
        "lattice_param_deviation_a": 1.0,
        "volume_deviation": 2.0,
        "final_energy": -40.0,
    }
    metrics_b = {
        "lattice_param_deviation_a": 1.5,
        "volume_deviation": 1.8,
        "final_energy": -42.0,
    }
    rows_a = [_row("mp-22526", "LiCoO2", "success", metrics=metrics_a)]
    rows_b = [_row("mp-22526", "LiCoO2", "success", metrics=metrics_b)]
    report = compare_benchmarks(rows_a, rows_b)

    deltas = report.metric_deltas.get("mp-22526", {})
    assert deltas["lattice_param_deviation_a"] == pytest.approx(0.5, abs=1e-9)
    assert deltas["volume_deviation"] == pytest.approx(-0.2, abs=1e-9)
    assert deltas["final_energy"] == pytest.approx(-2.0, abs=1e-9)


def test_compare_benchmarks_handles_missing_material() -> None:
    """Materials absent from one run must be reported separately."""
    rows_a = [
        _row("mp-22526", "LiCoO2", "success"),
        _row("mp-19017", "LiFePO4", "success"),
    ]
    # mp-19017 missing in B; mp-18767 new in B
    rows_b = [
        _row("mp-22526", "LiCoO2", "success"),
        _row("mp-18767", "LiMn2O4", "partial_success"),
    ]
    report = compare_benchmarks(rows_a, rows_b)
    assert "mp-19017" in report.missing_in_b
    assert "mp-18767" in report.missing_in_a
    # mp-22526 matched in both — status unchanged, not in missing lists
    assert "mp-22526" not in report.missing_in_b
    assert "mp-22526" not in report.missing_in_a
