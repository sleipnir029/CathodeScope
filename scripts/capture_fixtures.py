"""Fixture capture script for CathodeScope test suite.

Generates test fixtures for offline testing and regression tests.  Two
capture modes are available:

1. **Golden outputs** (default, offline, no API key required)::

       python scripts/capture_fixtures.py

   Runs the LiCoO2 structural_analysis workflow and the Phase-1 benchmark
   using a deterministic mock calculator (zero forces → immediate
   convergence).  Writes three files to
   ``tests/fixtures/expected_outputs/``:

   * ``licoo2_workflow_result.json`` – full WorkflowResult
   * ``licoo2_report.json``           – ReportRecord from step 6
   * ``benchmark_summary.json``       – BenchmarkSummary for Phase 1

2. **MP API responses** (requires ``MP_API_KEY``)::

       MP_API_KEY=<your_key> python scripts/capture_fixtures.py --mp

   Re-fetches the three benchmark MP entries and saves them to
   ``tests/fixtures/mp_responses/``.  **Do NOT run in CI** — fixtures
   are committed to version control.

Add ``--force`` to overwrite existing files (default: skip if already
present, ensuring idempotency).

Golden outputs use a deterministic mock calculator so they can be
regenerated offline at any time and compared reliably by T-29 regression
tests.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from ase.calculators.calculator import Calculator

# Ensure the repo root is on sys.path when executed directly.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

_MP_FIXTURE_DIR = _REPO_ROOT / "tests" / "fixtures" / "mp_responses"
_EXPECTED_OUTPUTS_DIR = _REPO_ROOT / "tests" / "fixtures" / "expected_outputs"
_BENCHMARK_MATERIALS = ["mp-22526", "mp-19017", "mp-18767"]

_FORMULA_TO_MP_ID: dict[str, str] = {
    "LiCoO2": "mp-22526",
    "LiFePO4": "mp-19017",
    "LiMn2O4": "mp-18767",
}

# ---------------------------------------------------------------------------
# Offline MP client (duck-typed — satisfies _MPClientProtocol in input_resolver)
# ---------------------------------------------------------------------------


class _OfflineMPClient:
    """Read fixture JSON files instead of making live MP API calls.

    Satisfies the ``_MPClientProtocol`` duck-type required by
    ``cathodescope.tools.input_resolver``.
    """

    def fetch_by_mp_id(self, mp_id: str) -> Any:
        """Return a success ToolResult backed by the committed fixture file."""
        from cathodescope.models.provenance import create_provenance
        from cathodescope.models.results import ToolResult

        fixture_path = _MP_FIXTURE_DIR / f"{mp_id}.json"
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

    def fetch_by_formula(self, formula: str) -> Any:
        """Resolve formula → mp_id via local look-up table."""
        from cathodescope.models.provenance import create_provenance
        from cathodescope.models.results import ErrorRecord, ToolResult

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
# Deterministic mock calculator (zero forces → immediate convergence)
# ---------------------------------------------------------------------------


class _MockZeroForceCalc(Calculator):
    """Return zero forces on every call → FIRE converges on step 0.

    Energy is fixed at -10.0 eV.  The structure is never moved, so golden
    output lattice parameters are identical to the normalized input.
    """

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self) -> None:
        """Initialise with ASE result caching enabled."""
        super().__init__()  # type: ignore[no-untyped-call]
        self.use_cache = True

    def calculate(
        self,
        atoms: Any = None,
        properties: Any = None,
        system_changes: Any = None,
    ) -> None:
        """Set results: constant energy, zero forces and stress."""
        n = len(atoms)
        self.results = {
            "energy": -10.0,
            "forces": np.zeros((n, 3)),
            "stress": np.zeros(6),
        }


# ---------------------------------------------------------------------------
# Offline config duck-type (no CathodescopeSettings import)
# ---------------------------------------------------------------------------


@dataclass
class _CaptureConfig:
    """Minimal config for golden output capture.

    Provides ``mp_client`` and ``calculator`` so the workflow step helpers
    ``_get_mp_client`` and ``_get_calculator`` use dependency injection
    instead of constructing live instances.
    """

    mp_client: Any = field(default_factory=_OfflineMPClient)
    calculator: Any = field(default_factory=_MockZeroForceCalc)

    def model_dump(self, *, mode: str = "json") -> dict[str, Any]:
        """Return a minimal config snapshot for provenance recording."""
        return {
            "mode": "golden_capture",
            "mp_client": "offline_fixture",
            "calculator": "mock_zero_force",
        }


# ---------------------------------------------------------------------------
# MP response capture (requires MP_API_KEY)
# ---------------------------------------------------------------------------


def _capture_mp_responses(force: bool) -> None:
    """Fetch and save MP API responses for the 3 benchmark materials.

    Requires ``MP_API_KEY`` environment variable.  Skips existing files
    unless ``force`` is True.
    """
    from cathodescope.tools.mp_client import CathodescopeMPClient  # noqa: PLC0415

    api_key = os.environ.get("MP_API_KEY", "").strip()
    if not api_key:
        print(
            "ERROR: MP_API_KEY not set. Skipping MP response capture.",
            file=sys.stderr,
        )
        return

    _MP_FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    cache_dir = _REPO_ROOT / "artifacts" / "cache" / "mp_capture_tmp"
    client = CathodescopeMPClient(api_key=api_key, cache_dir=cache_dir)

    for mp_id in _BENCHMARK_MATERIALS:
        out_path = _MP_FIXTURE_DIR / f"{mp_id}.json"
        if out_path.exists() and not force:
            print(f"  Skipping {mp_id} (exists; use --force to overwrite)")
            continue

        print(f"  Fetching {mp_id}…")
        result = client.fetch_by_mp_id(mp_id)
        if result.status != "success" or result.data is None:
            msg = result.error.message if result.error else "unknown error"
            print(f"  FAILED {mp_id}: {msg}", file=sys.stderr)
            continue

        out_path.write_text(json.dumps(result.data, indent=2), encoding="utf-8")
        print(f"  Saved  → {out_path.relative_to(_REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Golden output helpers
# ---------------------------------------------------------------------------


def _write_golden(path: Path, data: dict[str, Any]) -> None:
    """Write *data* as 2-space-indented JSON to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"  Saved  → {path.relative_to(_REPO_ROOT)}")


def _run_licoo2_workflow() -> Any:
    """Execute the LiCoO2 structural_analysis pipeline with mock calculator.

    Uses :class:`_OfflineMPClient` (no network) and
    :class:`_MockZeroForceCalc` (no MACE dependency).

    Returns
    -------
    WorkflowResult
        Completed result; status is ``"success"`` when all 7 steps pass.
    """
    from cathodescope.workflows.engine import WorkflowEngine  # noqa: PLC0415
    from cathodescope.workflows.structural_analysis import REGISTRY  # noqa: PLC0415

    engine = WorkflowEngine(REGISTRY)
    config = _CaptureConfig()
    return engine.run("structural_analysis", "mp-22526", config)


def _run_phase1_benchmark(tmp_store_dir: Path) -> Any:
    """Execute the Phase-1 benchmark across all 3 materials with mock calculator.

    Uses a temporary :class:`~cathodescope.provenance.store.ArtifactStore`
    to satisfy the runner's write requirements.  Only the returned
    :class:`~cathodescope.models.reports.BenchmarkSummary` is retained.

    Parameters
    ----------
    tmp_store_dir:
        Writable temporary directory for the ArtifactStore.

    Returns
    -------
    BenchmarkSummary
        Aggregated benchmark result for the three Phase-1 materials.
    """
    from cathodescope.benchmark.registry import (
        BenchmarkMaterialRegistry,  # noqa: PLC0415
    )
    from cathodescope.benchmark.runner import BenchmarkRunner  # noqa: PLC0415
    from cathodescope.provenance.store import ArtifactStore  # noqa: PLC0415
    from cathodescope.workflows.engine import WorkflowEngine  # noqa: PLC0415
    from cathodescope.workflows.structural_analysis import REGISTRY  # noqa: PLC0415

    store = ArtifactStore(tmp_store_dir)
    engine = WorkflowEngine(REGISTRY)
    registry = BenchmarkMaterialRegistry()
    runner = BenchmarkRunner(engine, registry, store)
    config = _CaptureConfig()
    return runner.run("phase1_structural_analysis", config)


# ---------------------------------------------------------------------------
# Golden output capture (offline, mock calculator)
# ---------------------------------------------------------------------------


def _capture_golden_outputs(force: bool) -> None:
    """Capture and commit golden WorkflowResult, ReportRecord, and BenchmarkSummary.

    Generates ``tests/fixtures/expected_outputs/``:

    * ``licoo2_workflow_result.json``
    * ``licoo2_report.json``
    * ``benchmark_summary.json``

    Files that already exist are skipped unless *force* is True.
    """
    wf_result_path = _EXPECTED_OUTPUTS_DIR / "licoo2_workflow_result.json"
    report_path = _EXPECTED_OUTPUTS_DIR / "licoo2_report.json"
    benchmark_path = _EXPECTED_OUTPUTS_DIR / "benchmark_summary.json"

    # --- LiCoO2 workflow result + report ------------------------------------
    need_wf = not wf_result_path.exists() or force
    need_report = not report_path.exists() or force

    if need_wf or need_report:
        print("  Running LiCoO2 structural_analysis workflow (mock calculator)…")
        wf_result = _run_licoo2_workflow()

        if wf_result.status != "success":
            print(
                f"  ERROR: LiCoO2 workflow failed (status={wf_result.status!r}). "
                "Cannot generate golden outputs.",
                file=sys.stderr,
            )
            return

        if need_wf:
            _write_golden(wf_result_path, wf_result.model_dump(mode="json"))
        else:
            print(f"  Skipping {wf_result_path.name} (exists)")

        if need_report:
            report_step = wf_result.steps[6]  # generate_report = step 6
            report_data: dict[str, Any] = report_step.tool_result.data or {}
            report_json: dict[str, Any] = report_data.get("report_json", {})
            _write_golden(report_path, report_json)
        else:
            print(f"  Skipping {report_path.name} (exists)")
    else:
        print(
            "  Skipping LiCoO2 workflow outputs (both exist; use --force to overwrite)"
        )

    # --- Phase-1 benchmark summary -----------------------------------------
    if not benchmark_path.exists() or force:
        print("  Running Phase-1 benchmark (3 materials, mock calculator)…")
        with tempfile.TemporaryDirectory() as tmp_dir:
            summary = _run_phase1_benchmark(Path(tmp_dir))
        _write_golden(benchmark_path, summary.model_dump(mode="json"))
    else:
        print(f"  Skipping {benchmark_path.name} (exists)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the capture script."""
    parser = argparse.ArgumentParser(
        prog="capture_fixtures",
        description=(
            "Capture or regenerate CathodeScope test fixtures.\n\n"
            "Default (no flags): generate golden outputs offline.\n"
            "Use --mp to also re-fetch MP API responses (requires MP_API_KEY)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing fixture files.",
    )
    parser.add_argument(
        "--mp",
        action="store_true",
        help="Capture MP API responses (requires MP_API_KEY environment variable).",
    )
    parser.add_argument(
        "--golden",
        action="store_true",
        help=(
            "Capture golden outputs (WorkflowResult, ReportRecord, BenchmarkSummary). "
            "Offline — no API key required. "
            "This is the default when neither --mp nor --golden is specified."
        ),
    )
    return parser


def main() -> None:
    """Parse CLI arguments and run the requested capture steps."""
    args = _build_parser().parse_args()

    # Default: run golden capture if neither mode flag is given.
    run_mp = args.mp
    run_golden = args.golden or (not args.mp and not args.golden)

    if run_mp:
        print("=== Capturing MP API responses ===")
        _capture_mp_responses(force=args.force)

    if run_golden:
        print("=== Capturing golden outputs ===")
        _capture_golden_outputs(force=args.force)

    print("Done.")


if __name__ == "__main__":
    main()
