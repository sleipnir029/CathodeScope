"""JSON report builder.

Implements build_json_report(workflow_result, material) -> ReportRecord.
Creates one ReportSection per workflow step plus summary and provenance sections.

Implemented in T-15.
"""

from datetime import UTC, datetime
from typing import Any

from cathodescope.models.material import CanonicalMaterial
from cathodescope.models.provenance import create_provenance
from cathodescope.models.reports import ReportRecord, ReportSection
from cathodescope.models.results import WorkflowResult

# Section headings in the order defined by architecture.md Section 4.7.
_SECTION_HEADINGS = [
    "Material Summary",
    "Retrieved Reference Data",
    "Normalization Results",
    "MACE Relaxation Results",
    "Reference Comparison",
    "Physics Validation",
    "Evidence Summary",
    "Provenance Summary",
]

# Maps workflow step name → section heading.
_STEP_TO_HEADING: dict[str, str] = {
    "fetch_structure": "Retrieved Reference Data",
    "normalize": "Normalization Results",
    "relax": "MACE Relaxation Results",
    "compare_reference": "Reference Comparison",
    "validate": "Physics Validation",
}


def build_json_report(
    workflow_result: WorkflowResult,
    material: CanonicalMaterial,
) -> ReportRecord:
    """Build a structured JSON report from a completed workflow result.

    Creates one ReportSection per standard pipeline section plus Evidence Summary
    and Provenance Summary sections. Section order follows architecture.md Section
    4.7. Does not import from cathodescope.tools — operates on model objects only.

    Parameters
    ----------
    workflow_result:
        Completed WorkflowResult from the workflow engine.
    material:
        CanonicalMaterial that was processed by the workflow.

    Returns
    -------
    ReportRecord
        Fully populated report record ready for serialization.
    """
    step_map = {s.step_name: s for s in workflow_result.steps}

    sections: list[ReportSection] = [
        _material_summary_section(material),
        _step_section(
            step_map, "fetch_structure", "Retrieved Reference Data", "A-retrieved"
        ),
        _step_section(step_map, "normalize", "Normalization Results", "A-computed"),
        _step_section(step_map, "relax", "MACE Relaxation Results", "A-computed"),
        _step_section(
            step_map, "compare_reference", "Reference Comparison", "A-compared"
        ),
        _step_section(step_map, "validate", "Physics Validation", "A-compared"),
    ]

    evidence_counts = _count_evidence(workflow_result)
    sections.append(_evidence_summary_section(evidence_counts))
    sections.append(_provenance_section(workflow_result))

    raw_user_input = _extract_raw_input(step_map, material.formula)
    report_provenance = create_provenance(
        created_by="cathodescope",
        tool_name="json_report",
        tool_version="1.0.0",
        workflow_run_id=workflow_result.workflow_run_id,
    )

    return ReportRecord(
        material_id=material.material_id,
        workflow_result_id=workflow_result.workflow_run_id,
        report_type="structural_analysis",
        raw_user_input=raw_user_input,
        title=f"Structural Analysis: {material.formula}",
        sections=sections,
        evidence_summary=dict(evidence_counts),
        generated_at=datetime.now(UTC),
        provenance=report_provenance,
    )


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------


def _material_summary_section(material: CanonicalMaterial) -> ReportSection:
    """Build the Material Summary section from CanonicalMaterial fields."""
    return ReportSection(
        heading="Material Summary",
        content_markdown=(
            f"Material: {material.formula} ({material.family}), "
            f"MP ID: {material.mp_id}, source: {material.source}."
        ),
        data={
            "formula": material.formula,
            "reduced_formula": material.reduced_formula,
            "family": material.family,
            "mp_id": material.mp_id,
            "source": material.source,
            "identifiers": material.identifiers,
        },
        evidence_labels=["A-retrieved"],
    )


def _step_section(
    step_map: dict[str, Any],
    step_name: str,
    heading: str,
    fallback_evidence: str,
) -> ReportSection:
    """Build a ReportSection from a named workflow step result.

    If the step is missing (e.g. workflow failed before reaching it), returns
    an empty section with a note in content_markdown.
    """
    step = step_map.get(step_name)
    if step is None or step.tool_result.data is None:
        return ReportSection(
            heading=heading,
            content_markdown=f"Step '{step_name}' did not produce data.",
            data={},
            evidence_labels=[fallback_evidence],
        )
    evidence = step.tool_result.evidence_type or fallback_evidence
    return ReportSection(
        heading=heading,
        content_markdown=f"Data from workflow step '{step_name}'.",
        data=dict(step.tool_result.data),
        evidence_labels=[evidence],
    )


def _count_evidence(workflow_result: WorkflowResult) -> dict[str, int]:
    """Count evidence_type occurrences across all steps, excluding 'metadata'."""
    counts: dict[str, int] = {}
    for step in workflow_result.steps:
        et = step.tool_result.evidence_type
        if et and et != "metadata":
            counts[et] = counts.get(et, 0) + 1
    return counts


def _evidence_summary_section(counts: dict[str, int]) -> ReportSection:
    """Build the Evidence Summary section from aggregated evidence counts."""
    overall = _overall_level(counts)
    return ReportSection(
        heading="Evidence Summary",
        content_markdown=(
            f"Overall evidence level: {overall}. "
            f"Label counts: {counts}."
        ),
        data={"counts": dict(counts), "overall_level": overall},
        evidence_labels=[],
    )


def _provenance_section(workflow_result: WorkflowResult) -> ReportSection:
    """Build the Provenance Summary section from WorkflowResult provenance."""
    prov = workflow_result.provenance
    completed = (
        workflow_result.completed_at.isoformat()
        if workflow_result.completed_at
        else None
    )
    return ReportSection(
        heading="Provenance Summary",
        content_markdown=(
            f"CathodeScope v{prov.cathodescope_version} on {prov.hostname}."
        ),
        data={
            "tool_name": prov.tool_name,
            "cathodescope_version": prov.cathodescope_version,
            "python_version": prov.python_version,
            "hostname": prov.hostname,
            "workflow_run_id": str(workflow_result.workflow_run_id),
            "started_at": workflow_result.started_at.isoformat(),
            "completed_at": completed,
        },
        evidence_labels=["metadata"],
    )


def _extract_raw_input(step_map: dict[str, Any], fallback: str) -> str:
    """Extract raw_input from resolve_input step data, or fall back to formula."""
    resolve_step = step_map.get("resolve_input")
    if resolve_step and resolve_step.tool_result.data:
        raw = resolve_step.tool_result.data.get("raw_input")
        if raw:
            return str(raw)
    return fallback


def _overall_level(counts: dict[str, int]) -> str:
    """Return weakest evidence level present (C < B < A)."""
    if any(k.startswith("C") for k in counts):
        return "C"
    if any(k.startswith("B") for k in counts):
        return "B"
    return "A"
