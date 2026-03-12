"""CLI interface for CathodeScope.

Commands:
- cathodescope analyze <formula|mp-id>: run structural_analysis workflow.
- cathodescope benchmark: run full benchmark suite.

Implemented in T-25.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _build_parser() -> Any:
    """Build and return the argparse argument parser."""
    import argparse

    from cathodescope import __version__

    parser = argparse.ArgumentParser(
        prog="cathodescope",
        description="CathodeScope: reproducible Li-ion cathode screening",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"cathodescope {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # --- analyze subcommand ---
    analyze = subparsers.add_parser(
        "analyze",
        help="Run the structural_analysis workflow for a material",
    )
    analyze.add_argument(
        "material",
        help="Material formula or mp-id (e.g. LiCoO2 or mp-22526)",
    )
    analyze.add_argument(
        "--output-dir",
        default="artifacts",
        help="Root output directory for artifacts (default: artifacts)",
    )
    analyze.add_argument(
        "--config",
        default=None,
        help="Path to a JSON config override file",
    )

    # --- benchmark subcommand ---
    bench = subparsers.add_parser(
        "benchmark",
        help="Run the benchmark suite",
    )
    bench.add_argument(
        "--name",
        default="phase1_structural_analysis",
        help="Benchmark set name (default: phase1_structural_analysis)",
    )
    bench.add_argument(
        "--output-dir",
        default="artifacts",
        help="Root output directory for artifacts (default: artifacts)",
    )
    bench.add_argument(
        "--config",
        default=None,
        help="Path to a JSON config override file",
    )

    return parser


def _cmd_analyze(args: Any) -> int:
    """Execute the analyze subcommand.

    Runs the structural_analysis workflow for the given material, saves the
    generated report to *args.output_dir*, and prints the report path to stdout.

    Progress messages go to stderr; the report path goes to stdout.

    Returns
    -------
    int
        0 on success, 1 on error.
    """
    from cathodescope.config.settings import CathodescopeSettings
    from cathodescope.workflows.engine import WorkflowEngine
    from cathodescope.workflows.structural_analysis import REGISTRY

    print(f"Analyzing {args.material}...", file=sys.stderr)

    try:
        settings = CathodescopeSettings.load(args.config)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    engine = WorkflowEngine(REGISTRY)
    try:
        result = engine.run("structural_analysis", args.material, settings)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    report_path = _save_report(result, args.output_dir)
    if report_path is None:
        print(
            "Error: workflow completed but no report was generated.", file=sys.stderr
        )
        return 1

    print(str(report_path))
    return 0


def _cmd_benchmark(args: Any) -> int:
    """Execute the benchmark subcommand.

    Instantiates the BenchmarkRunner and runs the named benchmark set.
    Prints a one-line summary to stdout.

    Progress messages go to stderr; the summary line goes to stdout.

    Returns
    -------
    int
        0 on success, 1 on error.
    """
    from cathodescope.benchmark.registry import BenchmarkMaterialRegistry
    from cathodescope.benchmark.runner import BenchmarkRunner
    from cathodescope.config.settings import CathodescopeSettings
    from cathodescope.provenance.store import ArtifactStore
    from cathodescope.workflows.engine import WorkflowEngine
    from cathodescope.workflows.structural_analysis import REGISTRY

    print(f"Running benchmark: {args.name}...", file=sys.stderr)

    try:
        settings = CathodescopeSettings.load(args.config)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    store = ArtifactStore(args.output_dir)
    engine = WorkflowEngine(REGISTRY)
    registry = BenchmarkMaterialRegistry()
    runner = BenchmarkRunner(engine, registry, store)

    try:
        summary = runner.run(args.name, settings)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    counts = summary.status_counts
    print(
        f"Benchmark {args.name} complete: "
        f"{summary.materials_count} materials, "
        f"success={counts.get('success', 0)}, "
        f"partial={counts.get('partial_success', 0)}, "
        f"soft_fail={counts.get('soft_failure', 0)}, "
        f"hard_fail={counts.get('hard_failure', 0)}"
    )
    return 0


def _save_report(result: Any, output_dir: str) -> Path | None:
    """Save the Markdown and JSON reports from a workflow result.

    Searches *result.steps* for the ``generate_report`` step and writes
    ``report.md`` and ``report.json`` to
    ``{output_dir}/reports/{workflow_run_id}/``.

    Parameters
    ----------
    result:
        :class:`~cathodescope.models.results.WorkflowResult` from the engine.
    output_dir:
        Root artifact directory (e.g. ``"artifacts"``).

    Returns
    -------
    Path or None
        Path to the saved ``report.md``, or ``None`` if the
        ``generate_report`` step was absent from *result*.
    """
    for step in result.steps:
        if step.step_name == "generate_report" and step.tool_result.data:
            data = step.tool_result.data
            markdown: str = data.get("report_markdown", "")
            report_json: dict[str, Any] = data.get("report_json", {})

            run_id = str(result.workflow_run_id)
            out = Path(output_dir) / "reports" / run_id
            out.mkdir(parents=True, exist_ok=True)

            md_path = out / "report.md"
            md_path.write_text(markdown, encoding="utf-8")

            json_path = out / "report.json"
            json_path.write_text(json.dumps(report_json, indent=2), encoding="utf-8")

            return md_path
    return None


def main() -> None:
    """Entry point for the cathodescope CLI.

    Parses command-line arguments and dispatches to the appropriate
    subcommand handler (``analyze`` or ``benchmark``).
    Exits with code 0 on success, 1 on error, or prints help and exits with
    1 if no subcommand is provided.
    """
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        sys.exit(_cmd_analyze(args))
    elif args.command == "benchmark":
        sys.exit(_cmd_benchmark(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
