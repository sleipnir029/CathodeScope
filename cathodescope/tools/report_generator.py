"""Report generator tool.

Thin wrapper delegating to json_report and markdown_report,
wrapping both outputs in a ToolResult.

Implemented in T-17.
"""

from cathodescope.models.material import CanonicalMaterial
from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ToolResult, WorkflowResult
from cathodescope.reporting.json_report import build_json_report
from cathodescope.reporting.markdown_report import render_markdown

_TOOL_VERSION = "0.1.0"


def generate(
    workflow_result: WorkflowResult,
    material: CanonicalMaterial,
) -> ToolResult:
    """Generate a structured report from a completed workflow result.

    Delegates to :func:`~cathodescope.reporting.json_report.build_json_report`
    and :func:`~cathodescope.reporting.markdown_report.render_markdown`.
    Contains no business logic of its own.  The ``evidence_type`` is
    ``"metadata"`` because report generation does not produce scientific data
    and is excluded from the evidence summary count.

    Parameters
    ----------
    workflow_result:
        Completed :class:`~cathodescope.models.results.WorkflowResult` from the
        workflow engine.
    material:
        :class:`~cathodescope.models.material.CanonicalMaterial` that was
        processed by the workflow.

    Returns
    -------
    ToolResult
        ``status="success"``, ``evidence_type="metadata"``, and ``data``
        containing ``report_json`` (dict), ``report_markdown`` (str), and
        ``evidence_summary`` (dict).
    """
    prov = create_provenance(
        created_by="cathodescope",
        tool_name="report_generator",
        tool_version=_TOOL_VERSION,
        workflow_run_id=workflow_result.workflow_run_id,
    )

    report = build_json_report(workflow_result, material)
    markdown = render_markdown(report)

    return ToolResult(
        tool_name="report_generator",
        status="success",
        data={
            "report_json": report.model_dump(mode="json"),
            "report_markdown": markdown,
            "evidence_summary": report.evidence_summary,
        },
        evidence_type="metadata",
        provenance=prov,
    )
