"""Integration tests for the CathodeScope CLI.

Tests implemented in T-25.
"""

from __future__ import annotations

import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import StepResult, ToolResult, WorkflowResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CLI_MODULE = "cathodescope.app.cli"


def _make_workflow_result() -> WorkflowResult:
    """Return a minimal WorkflowResult with a generate_report step."""
    run_id = uuid.uuid4()
    prov = create_provenance(
        created_by="cathodescope",
        tool_name="test",
        tool_version="0.0.1",
    )
    report_data = {
        "report_json": {"title": "Test Report"},
        "report_markdown": "# Test Report\n",
        "evidence_summary": {},
    }
    step_tr = ToolResult(
        tool_name="report_generator",
        status="success",
        data=report_data,
        evidence_type="metadata",
        provenance=prov,
    )
    step_r = StepResult(
        step_name="generate_report",
        step_index=6,
        tool_result=step_tr,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )
    return WorkflowResult(
        workflow_run_id=run_id,
        workflow_name="structural_analysis",
        status="success",
        steps=[step_r],
        provenance=prov,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
    )


# ---------------------------------------------------------------------------
# Subprocess tests (no mocking; test CLI as a black box)
# ---------------------------------------------------------------------------


def test_cli_help_shows_usage() -> None:
    """--help prints usage with 'analyze' and 'benchmark' subcommands."""
    result = subprocess.run(
        [sys.executable, "-m", _CLI_MODULE, "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "analyze" in result.stdout
    assert "benchmark" in result.stdout


def test_cli_version_shows_version() -> None:
    """--version prints the version string (0.1.0)."""
    result = subprocess.run(
        [sys.executable, "-m", _CLI_MODULE, "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout + result.stderr


def test_cli_analyze_command_exists() -> None:
    """analyze subcommand is recognized and shows 'material' in its --help."""
    result = subprocess.run(
        [sys.executable, "-m", _CLI_MODULE, "analyze", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "material" in result.stdout.lower()


def test_cli_benchmark_command_exists() -> None:
    """benchmark subcommand is recognized and shows its own --help."""
    result = subprocess.run(
        [sys.executable, "-m", _CLI_MODULE, "benchmark", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # --name or benchmark should appear in help
    assert "name" in result.stdout.lower() or "benchmark" in result.stdout.lower()


# ---------------------------------------------------------------------------
# Mock-based tests (test plumbing without real MACE or MP API)
# ---------------------------------------------------------------------------


def test_cli_analyze_licoo2_produces_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """analyze LiCoO2 prints a non-empty report path to stdout."""
    monkeypatch.setenv("MP_API_KEY", "test-key")
    mock_result = _make_workflow_result()

    with patch(
        "cathodescope.workflows.engine.WorkflowEngine.run", return_value=mock_result
    ):
        monkeypatch.setattr(
            sys,
            "argv",
            ["cathodescope", "analyze", "LiCoO2", "--output-dir", str(tmp_path)],
        )
        from cathodescope.app.cli import main  # noqa: PLC0415

        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code in (0, None)
    captured = capsys.readouterr()
    assert captured.out.strip(), "Expected a report path on stdout"


def test_cli_analyze_invalid_formula_shows_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """analyze with a failing workflow exits non-zero and prints an error."""
    monkeypatch.setenv("MP_API_KEY", "test-key")

    with patch(
        "cathodescope.workflows.engine.WorkflowEngine.run",
        side_effect=RuntimeError("cannot resolve input: BADFORMULA"),
    ):
        monkeypatch.setattr(
            sys,
            "argv",
            ["cathodescope", "analyze", "BADFORMULA", "--output-dir", str(tmp_path)],
        )
        from cathodescope.app.cli import main  # noqa: PLC0415

        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code not in (0, None)
    captured = capsys.readouterr()
    assert "error" in (captured.err + captured.out).lower()


def test_cli_benchmark_runs_phase1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """benchmark --name phase1_structural_analysis runs and prints a summary line."""
    monkeypatch.setenv("MP_API_KEY", "test-key")

    mock_summary = MagicMock()
    mock_summary.benchmark_run_id = uuid.uuid4()
    mock_summary.materials_count = 3
    mock_summary.status_counts = {
        "success": 1,
        "partial_success": 1,
        "soft_failure": 1,
        "hard_failure": 0,
        "infrastructure_failure": 0,
    }

    with patch(
        "cathodescope.benchmark.runner.BenchmarkRunner.run", return_value=mock_summary
    ):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "cathodescope",
                "benchmark",
                "--name",
                "phase1_structural_analysis",
                "--output-dir",
                str(tmp_path),
            ],
        )
        from cathodescope.app.cli import main  # noqa: PLC0415

        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code in (0, None)
    captured = capsys.readouterr()
    assert captured.out.strip() or captured.err.strip()
