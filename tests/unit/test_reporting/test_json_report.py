"""Unit tests for cathodescope.reporting.json_report.

12 tests implemented in T-15.
"""

import json
from datetime import UTC, datetime
from typing import Any

from cathodescope.models.material import CanonicalMaterial
from cathodescope.models.provenance import ProvenanceRecord, create_provenance
from cathodescope.models.reports import ReportRecord
from cathodescope.models.results import StepResult, ToolResult, WorkflowResult
from cathodescope.reporting.json_report import build_json_report

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
                "lattice": {"a": 2.81, "b": 2.81, "c": 14.05},
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
                "a": 2.81,
                "b": 2.81,
                "c": 14.05,
                "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            },
            "sites": [],
        },
        source="materials_project",
        mp_id="mp-22526",
        provenance=_make_provenance("mp_client"),
    )


# ---------------------------------------------------------------------------
# 12 tests
# ---------------------------------------------------------------------------


def test_build_json_report_returns_report_record() -> None:
    """build_json_report returns a ReportRecord instance."""
    result = build_json_report(_make_workflow_result(), _make_material())
    assert isinstance(result, ReportRecord)


def test_json_report_has_all_required_sections() -> None:
    """Report has all 8 required sections in the correct order."""
    report = build_json_report(_make_workflow_result(), _make_material())
    expected_headings = [
        "Material Summary",
        "Retrieved Reference Data",
        "Normalization Results",
        "MACE Relaxation Results",
        "Reference Comparison",
        "Physics Validation",
        "Evidence Summary",
        "Provenance Summary",
    ]
    actual_headings = [s.heading for s in report.sections]
    assert actual_headings == expected_headings


def test_json_report_material_summary_section() -> None:
    """Material Summary section data contains formula, family, mp_id, source."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[0]
    assert section.heading == "Material Summary"
    data = section.data
    assert data["formula"] == "LiCoO2"
    assert data["family"] == "layered_oxide"
    assert data["mp_id"] == "mp-22526"
    assert data["source"] == "materials_project"


def test_json_report_retrieved_data_section() -> None:
    """Retrieved Reference Data section data mirrors fetch_structure step output."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[1]
    assert section.heading == "Retrieved Reference Data"
    # Data should contain the fields from the fetch_structure step
    assert "mp_id" in section.data
    assert section.data["mp_id"] == "mp-22526"
    assert "lattice" in section.data


def test_json_report_normalization_section() -> None:
    """Normalization Results section data mirrors normalize step output."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[2]
    assert section.heading == "Normalization Results"
    assert "space_group" in section.data
    assert section.data["space_group"] == "R-3m"
    assert "atom_count" in section.data


def test_json_report_relaxation_section() -> None:
    """MACE Relaxation Results section data mirrors relax step output."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[3]
    assert section.heading == "MACE Relaxation Results"
    assert "converged" in section.data
    assert section.data["converged"] is True
    assert "fmax" in section.data


def test_json_report_comparison_section() -> None:
    """Reference Comparison section data mirrors compare_reference step output."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[4]
    assert section.heading == "Reference Comparison"
    assert "lattice_deviations" in section.data
    assert "volume_deviation" in section.data
    assert "symmetry_preserved" in section.data


def test_json_report_validation_section() -> None:
    """Physics Validation section data mirrors validate step output."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[5]
    assert section.heading == "Physics Validation"
    assert "overall_sanity" in section.data
    assert section.data["overall_sanity"] is True


def test_json_report_evidence_summary_section() -> None:
    """Evidence Summary section exists and data contains evidence counts."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[6]
    assert section.heading == "Evidence Summary"
    assert "counts" in section.data
    counts = section.data["counts"]
    assert isinstance(counts, dict)
    assert len(counts) > 0


def test_json_report_provenance_section() -> None:
    """Provenance Summary section exists and data contains workflow_run_id."""
    report = build_json_report(_make_workflow_result(), _make_material())
    section = report.sections[7]
    assert section.heading == "Provenance Summary"
    assert "workflow_run_id" in section.data
    assert "cathodescope_version" in section.data


def test_json_report_evidence_summary_counts() -> None:
    """evidence_summary on ReportRecord aggregates step evidence_types correctly.

    Fixture has: resolve_input(A-retrieved), fetch_structure(A-retrieved),
    normalize(A-computed), relax(A-computed), compare_reference(A-compared),
    validate(A-compared) → 2 of each type.
    """
    report = build_json_report(_make_workflow_result(), _make_material())
    assert report.evidence_summary["A-retrieved"] == 2
    assert report.evidence_summary["A-computed"] == 2
    assert report.evidence_summary["A-compared"] == 2


def test_json_report_serializes_to_valid_json() -> None:
    """model_dump(mode='json') produces a JSON-serializable dict."""
    report = build_json_report(_make_workflow_result(), _make_material())
    dumped = report.model_dump(mode="json")
    # Verify round-trip through json.dumps/loads without errors
    serialized = json.dumps(dumped)
    reloaded = json.loads(serialized)
    assert reloaded["report_type"] == "structural_analysis"
    assert reloaded["title"] == "Structural Analysis: LiCoO2"
    assert len(reloaded["sections"]) == 8
