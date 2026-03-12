"""Unit tests for cathodescope.reporting.markdown_report.

13 tests implemented in T-16.
"""

import re
from datetime import UTC, datetime
from typing import Any

from cathodescope.models.material import CanonicalMaterial
from cathodescope.models.provenance import ProvenanceRecord, create_provenance
from cathodescope.models.results import StepResult, ToolResult, WorkflowResult
from cathodescope.reporting.json_report import build_json_report
from cathodescope.reporting.markdown_report import render_markdown

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_provenance(tool_name: str = "test") -> ProvenanceRecord:
    """Return a minimal ProvenanceRecord for test use."""
    return create_provenance(
        created_by="cathodescope",
        tool_name=tool_name,
        tool_version="0.0.0",
    )


def _make_tool_result(
    tool_name: str,
    data: dict[str, Any] | None,
    evidence_type: str,
) -> ToolResult:
    return ToolResult(
        tool_name=tool_name,
        status="success",
        data=data,
        provenance=_make_provenance(tool_name),
        evidence_type=evidence_type,
    )


def _make_step(
    name: str,
    index: int,
    data: dict[str, Any] | None,
    evidence_type: str,
) -> StepResult:
    now = datetime.now(UTC)
    return StepResult(
        step_name=name,
        step_index=index,
        tool_result=_make_tool_result(name, data, evidence_type),
        started_at=now,
        completed_at=now,
    )


def _make_workflow_result() -> WorkflowResult:
    """WorkflowResult with 6 steps matching the structural_analysis pipeline."""
    now = datetime.now(UTC)
    steps = [
        _make_step(
            "resolve_input",
            0,
            {
                "formula": "LiCoO2",
                "reduced_formula": "LiCoO2",
                "mp_id": "mp-22526",
                "source_type": "formula",
                "raw_input": "LiCoO2",
            },
            "A-retrieved",
        ),
        _make_step(
            "fetch_structure",
            1,
            {
                "mp_id": "mp-22526",
                "formula": "LiCoO2",
                "lattice": {"a": 2.836, "b": 2.836, "c": 14.083},
                "space_group": "R-3m",
                "formation_energy_per_atom": -2.87,
            },
            "A-retrieved",
        ),
        _make_step(
            "normalize",
            2,
            {
                "space_group": "R-3m",
                "atom_count": 12,
                "conventional_cell": True,
            },
            "A-computed",
        ),
        _make_step(
            "relax",
            3,
            {
                "converged": True,
                "steps": 23,
                "fmax": 0.005,
                "final_energy": -42.156,
                "convergence_info": {"converged": True, "steps": 23, "fmax": 0.005},
            },
            "A-computed",
        ),
        _make_step(
            "compare_reference",
            4,
            {
                "lattice_deviations": {"a": 0.53, "b": 0.53, "c": 0.22},
                "angle_deviations": {"alpha": 0.0, "beta": 0.0, "gamma": 0.0},
                "volume_deviation": 1.28,
                "symmetry_preserved": True,
                "within_lattice_tolerance": True,
                "within_volume_tolerance": True,
            },
            "A-compared",
        ),
        _make_step(
            "validate",
            5,
            {
                "overall_sanity": True,
                "checks": [],
                "evidence_labels": [],
                "warnings": [],
            },
            "A-compared",
        ),
    ]
    return WorkflowResult(
        workflow_name="structural_analysis",
        status="success",
        steps=steps,
        provenance=_make_provenance("workflow_engine"),
        material_id="mp-22526",
        started_at=now,
        completed_at=now,
    )


def _make_material() -> CanonicalMaterial:
    return CanonicalMaterial(
        formula="LiCoO2",
        reduced_formula="LiCoO2",
        family="layered_oxide",
        structure={
            "lattice": {
                "a": 2.836,
                "b": 2.836,
                "c": 14.083,
                "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            },
            "sites": [],
        },
        source="materials_project",
        mp_id="mp-22526",
        provenance=_make_provenance("mp_client"),
    )


def _make_report():
    """Build a ReportRecord for markdown rendering tests."""
    return build_json_report(_make_workflow_result(), _make_material())


# ---------------------------------------------------------------------------
# 13 tests
# ---------------------------------------------------------------------------


def test_render_markdown_returns_string() -> None:
    """render_markdown returns a non-empty string."""
    report = _make_report()
    result = render_markdown(report)
    assert isinstance(result, str)
    assert len(result) > 0


def test_markdown_contains_title() -> None:
    """Output contains a top-level heading with the report title."""
    report = _make_report()
    md = render_markdown(report)
    assert "## Structural Analysis: LiCoO2" in md


def test_markdown_section_headers_include_evidence_level() -> None:
    """All rendered section headers include a [Level X -- sub-type] label."""
    report = _make_report()
    md = render_markdown(report)
    assert re.search(r"###.*\[Level [A-C] --", md) is not None


def test_markdown_retrieved_data_section_has_level_a_retrieved() -> None:
    """Retrieved Reference Data section header has [Level A -- retrieved]."""
    report = _make_report()
    md = render_markdown(report)
    assert "### Retrieved Reference Data [Level A -- retrieved]" in md


def test_markdown_relaxation_section_has_level_a_computed() -> None:
    """MACE Relaxation Results section header has [Level A -- computed]."""
    report = _make_report()
    md = render_markdown(report)
    assert "### MACE Relaxation Results [Level A -- computed]" in md


def test_markdown_comparison_section_has_level_a_compared() -> None:
    """Reference Comparison section header has [Level A -- compared]."""
    report = _make_report()
    md = render_markdown(report)
    assert "### Reference Comparison [Level A -- compared]" in md


def test_markdown_contains_mp_id() -> None:
    """Output contains the Materials Project ID from the fixture."""
    report = _make_report()
    md = render_markdown(report)
    assert "mp-22526" in md


def test_markdown_contains_mace_version() -> None:
    """Output contains the MACE model name."""
    report = _make_report()
    md = render_markdown(report)
    assert "MACE-MP-0" in md


def test_markdown_contains_convergence_details() -> None:
    """Output contains relaxation convergence details (fmax and step count)."""
    report = _make_report()
    md = render_markdown(report)
    assert "fmax" in md
    assert "steps" in md or "23" in md


def test_markdown_contains_lattice_deviations() -> None:
    """Output contains lattice deviation values from the comparison section."""
    report = _make_report()
    md = render_markdown(report)
    # Fixture values: a=0.53%, c=0.22% deviation
    assert "0.53" in md
    assert "0.22" in md


def test_markdown_assessment_paragraph_summarizes_evidence() -> None:
    """Output contains an Assessment paragraph with evidence level summary."""
    report = _make_report()
    md = render_markdown(report)
    assert "**Assessment**" in md
    assert "Level A" in md


def test_markdown_no_disallowed_words() -> None:
    """Output does not contain disallowed wording from scientific_validity_matrix.md."""
    report = _make_report()
    md = render_markdown(report)
    disallowed_patterns = [
        r"validated structure",
        r"discovered",
        r"proved stable",
        r"\baccurate\b(?! lattice parameters within| to| at)",
    ]
    for pattern in disallowed_patterns:
        assert not re.search(pattern, md, re.IGNORECASE), (
            f"Disallowed wording pattern found in output: {pattern!r}"
        )


def test_markdown_matches_validity_matrix_format() -> None:
    """Output structure matches the mock excerpt from validity matrix Section 5."""
    report = _make_report()
    md = render_markdown(report)
    # Top-level ## heading present
    assert re.search(r"^## ", md, re.MULTILINE) is not None
    # Section-level ### headings present
    assert re.search(r"^### ", md, re.MULTILINE) is not None
    # Mandatory methodology caveat present
    assert "Methodology caveat" in md
    # Evidence labels present
    assert "[Level A" in md
