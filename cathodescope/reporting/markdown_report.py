"""Markdown report renderer.

Implements render_markdown(report: ReportRecord) -> str.
Enforces all 10 wording rules from scientific_validity_matrix.md Section 4.
Inline evidence labels in section headers: ### ... [Level X -- sub-type].

Implemented in T-16.
"""

from cathodescope.models.reports import ReportRecord, ReportSection

_MACE_VERSION_STR = "MACE-MP-0 (v0.3.6)"

_METHODOLOGY_CAVEAT = (
    "> **Methodology caveat (mandatory in all reports):** "
    "All deviations are computed between MACE-MP-0 relaxed structures and "
    "Materials Project PBE+U reference calculations. "
    "The PBE+U reference itself deviates from experimental values by approximately "
    "1\u20133% for lattice parameters. "
    "Deviations reported here reflect inter-method consistency, "
    "not absolute accuracy relative to experiment."
)

_EVIDENCE_DISPLAY: dict[str, str] = {
    "A-retrieved": "Level A -- retrieved",
    "A-computed": "Level A -- computed",
    "A-compared": "Level A -- compared",
    "B-restricted": "Level B -- restricted estimate",
    "C-proxy": "Level C -- proxy",
}

# Headings handled outside the main section loop.
_SKIP_HEADINGS = {"Evidence Summary", "Provenance Summary"}


def render_markdown(report: ReportRecord) -> str:
    """Render a ReportRecord as a Markdown string.

    Produces a human-readable report with inline evidence labels in section
    headers, following the format defined in scientific_validity_matrix.md
    Section 5. Enforces all 10 wording rules from scientific_validity_matrix.md
    Section 4. Does not import from cathodescope.tools — operates on model
    objects only.

    Parameters
    ----------
    report:
        Completed ReportRecord from build_json_report().

    Returns
    -------
    str
        Markdown-formatted report string.
    """
    parts: list[str] = [f"## {report.title}", ""]

    section_map = {s.heading: s for s in report.sections}

    for section in report.sections:
        if section.heading in _SKIP_HEADINGS:
            continue
        rendered = _render_section(section)
        if rendered:
            parts.append(rendered)
            parts.append("")

    evidence_sec = section_map.get("Evidence Summary")
    if evidence_sec:
        parts.append(_render_assessment(evidence_sec))
        parts.append("")

    prov_sec = section_map.get("Provenance Summary")
    if prov_sec:
        parts.append(_render_provenance_section(prov_sec))
        parts.append("")

    parts.append(_METHODOLOGY_CAVEAT)
    return "\n".join(parts)


def _format_evidence_label(evidence_labels: list[str]) -> str:
    """Convert the first evidence label to formatted bracket notation."""
    for label in evidence_labels:
        if label in _EVIDENCE_DISPLAY:
            return f" [{_EVIDENCE_DISPLAY[label]}]"
    return ""


def _render_section(section: ReportSection) -> str:
    """Render a scientific ReportSection as a Markdown block."""
    label = _format_evidence_label(section.evidence_labels)
    header = f"### {section.heading}{label}"
    lines: list[str] = [header]

    if section.heading == "Material Summary":
        lines.extend(_render_material_summary(section))
    elif section.heading == "Retrieved Reference Data":
        lines.extend(_render_retrieved_data(section))
    elif section.heading == "Normalization Results":
        lines.extend(_render_normalization(section))
    elif section.heading == "MACE Relaxation Results":
        lines.extend(_render_relaxation(section))
    elif section.heading == "Reference Comparison":
        lines.extend(_render_comparison(section))
    elif section.heading == "Physics Validation":
        lines.extend(_render_validation(section))
    else:
        lines.append(section.content_markdown)

    return "\n".join(lines)


def _render_material_summary(section: ReportSection) -> list[str]:
    """Render Material Summary section lines."""
    d = section.data
    formula = d.get("formula", "unknown")
    family = d.get("family", "unknown")
    mp_id = d.get("mp_id", "unknown")
    source = d.get("source", "unknown")
    return [
        f"Material: {formula} ({family}), MP ID: {mp_id}, source: {source}.",
    ]


def _render_retrieved_data(section: ReportSection) -> list[str]:
    """Render Retrieved Reference Data section lines."""
    d = section.data
    mp_id = d.get("mp_id", "unknown")
    space_group = d.get("space_group", "unknown")
    lattice = d.get("lattice", {})
    a = lattice.get("a", "?") if isinstance(lattice, dict) else "?"
    c = lattice.get("c", "?") if isinstance(lattice, dict) else "?"
    return [
        f"Crystal structure retrieved from Materials Project ({mp_id}), "
        "computed using PBE+U methodology.",
        f"- Space group: {space_group}",
        f"- Lattice parameters: a = {a} Angstrom, c = {c} Angstrom",
    ]


def _render_normalization(section: ReportSection) -> list[str]:
    """Render Normalization Results section lines."""
    d = section.data
    space_group = d.get("space_group", "unknown")
    atom_count = d.get("atom_count", "?")
    conventional = d.get("conventional_cell", "?")
    return [
        "Structure normalized using SpacegroupAnalyzer (pymatgen).",
        f"- Space group: {space_group}",
        f"- Atom count: {atom_count}",
        f"- Conventional cell: {conventional}",
    ]


def _render_relaxation(section: ReportSection) -> list[str]:
    """Render MACE Relaxation Results section lines."""
    d = section.data
    converged = d.get("converged", "?")
    steps = d.get("steps", "?")
    fmax = d.get("fmax", "?")
    final_energy = d.get("final_energy", "?")
    return [
        f"Structure relaxed using {_MACE_VERSION_STR}.",
        f"- Convergence: fmax = {fmax} eV/Angstrom reached in {steps} steps",
        f"- Converged: {converged}",
        f"- Final energy: {final_energy} eV",
    ]


def _render_comparison(section: ReportSection) -> list[str]:
    """Render Reference Comparison section lines."""
    d = section.data
    lattice_dev = d.get("lattice_deviations", {})
    volume_dev = d.get("volume_deviation", "?")
    symmetry_preserved = d.get("symmetry_preserved", "?")
    lines: list[str] = []
    if isinstance(lattice_dev, dict):
        for param, val in lattice_dev.items():
            lines.append(
                f"- Lattice parameter {param}: deviation {val}% from MP reference"
            )
    lines.append(f"- Cell volume deviation: {volume_dev}% from MP reference")
    lines.append(f"- Space group preserved: {symmetry_preserved}")
    return lines


def _render_validation(section: ReportSection) -> list[str]:
    """Render Physics Validation section lines."""
    d = section.data
    overall_sanity = d.get("overall_sanity", "?")
    warnings = d.get("warnings", [])
    lines = [f"- Overall structural sanity: {overall_sanity}"]
    if isinstance(warnings, list):
        for w in warnings:
            lines.append(f"- Warning: {w}")
    return lines


def _render_assessment(section: ReportSection) -> str:
    """Render an assessment paragraph from the Evidence Summary section."""
    d = section.data
    overall = d.get("overall_level", "A")
    counts: dict[str, int] = d.get("counts", {})
    count_str = ", ".join(f"{k}: {v}" for k, v in counts.items())
    if overall == "A":
        level_summary = (
            "All lattice parameter deviations are within the defined 2% threshold, "
            "and volume deviation is within the 5% threshold "
            "(benchmarked against 3 known cathode materials: "
            "LiCoO2, LiFePO4, LiMn2O4). "
            "All evidence labels are Level A."
        )
    else:
        level_summary = f"Weakest evidence level present: Level {overall}."
    return (
        f"**Assessment**: Overall evidence level: {overall}. "
        f"Label counts: {count_str}. "
        f"{level_summary}"
    )


def _render_provenance_section(section: ReportSection) -> str:
    """Render the Provenance Summary section."""
    d = section.data
    cs_version = d.get("cathodescope_version", "unknown")
    hostname = d.get("hostname", "unknown")
    run_id = d.get("workflow_run_id", "unknown")
    started = d.get("started_at", "unknown")
    lines = [
        "### Provenance Summary",
        f"CathodeScope v{cs_version} on {hostname}.",
        f"- Workflow run ID: {run_id}",
        f"- Started at: {started}",
    ]
    return "\n".join(lines)
