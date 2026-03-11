"""Unit tests for cathodescope.models.reports.

Tests for ReportSection, ReportRecord, BenchmarkRow, BenchmarkSummary.
18 tests implemented in T-04.
"""

import json
import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cathodescope.models.provenance import ProvenanceRecord
from cathodescope.models.reports import (
    BenchmarkRow,
    BenchmarkSummary,
    ReportRecord,
    ReportSection,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_provenance() -> ProvenanceRecord:
    """Return a minimal ProvenanceRecord for embedding in report models."""
    return ProvenanceRecord(
        created_by="cathodescope",
        tool_name="test_tool",
        tool_version="0.1.0",
        cathodescope_version="0.1.0",
        python_version="3.11.0",
        hostname="testhost",
        platform="linux",
    )


def _minimal_section() -> ReportSection:
    """Return a minimal ReportSection."""
    return ReportSection(
        heading="Test Section",
        content_markdown="Some content.",
        data={"key": "value"},
        evidence_labels=["A-computed"],
    )


def _minimal_report_record() -> ReportRecord:
    """Return a minimal ReportRecord with all required fields."""
    return ReportRecord(
        schema_version="1.0.0",
        report_id=uuid.uuid4(),
        material_id="mat-001",
        workflow_result_id=uuid.uuid4(),
        report_type="structural_analysis",
        raw_user_input="LiCoO2",
        title="Structural Analysis: LiCoO2",
        sections=[_minimal_section()],
        evidence_summary={"A-computed": 1},
        warnings=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        provenance=_minimal_provenance(),
    )


def _minimal_benchmark_row() -> BenchmarkRow:
    """Return a minimal BenchmarkRow."""
    return BenchmarkRow(
        schema_version="1.0.0",
        benchmark_run_id=uuid.uuid4(),
        material_id="mat-001",
        formula="LiCoO2",
        family="layered_oxide",
        workflow_name="structural_analysis",
        workflow_version="1.0.0",
        status="success",
        metrics={
            "input_resolution": True,
            "structure_retrieval": True,
            "structure_normalization": True,
            "space_group_input": "R-3m",
            "relaxation_convergence": True,
            "relaxation_steps": 23,
            "final_fmax": 0.005,
            "final_energy": -42.156,
            "lattice_param_deviation_a": 0.53,
            "lattice_param_deviation_b": 0.53,
            "lattice_param_deviation_c": 0.22,
            "volume_deviation": 1.28,
            "symmetry_preserved": True,
            "space_group_output": "R-3m",
            "min_bond_length": 1.92,
            "max_bond_length": 2.11,
            "evidence_labeling_complete": True,
            "report_generated": True,
            "runtime_seconds": 12.3,
            "workflow_version": "1.0.0",
            "angle_deviation_alpha": 0.0,
            "angle_deviation_beta": 0.0,
            "angle_deviation_gamma": 0.0,
            "symprec_used": 0.1,
        },
        failure_category=None,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        provenance=_minimal_provenance(),
    )


def _minimal_benchmark_summary(rows: list[str] | None = None) -> BenchmarkSummary:
    """Return a minimal BenchmarkSummary."""
    if rows is None:
        rows = ["rows/mat-001.json"]
    return BenchmarkSummary(
        schema_version="1.0.0",
        benchmark_run_id=uuid.uuid4(),
        benchmark_name="phase1_structural_analysis",
        materials_count=len(rows),
        status_counts={
            "success": len(rows),
            "partial_success": 0,
            "soft_failure": 0,
            "hard_failure": 0,
            "infrastructure_failure": 0,
        },
        rows=rows,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        completed_at=datetime(2026, 1, 1, 0, 10, tzinfo=UTC),
        runtime_seconds=10.0,
        provenance=_minimal_provenance(),
    )


# ---------------------------------------------------------------------------
# ReportSection tests (3)
# ---------------------------------------------------------------------------


def test_report_section_creation() -> None:
    """ReportSection can be created with all required fields."""
    section = ReportSection(
        heading="Lattice Parameters",
        content_markdown="The relaxed structure has lattice parameter a = 2.81 Å.",
        data={"a": 2.81, "b": 2.81, "c": 14.05},
        evidence_labels=["A-computed", "A-compared"],
    )
    assert section.heading == "Lattice Parameters"
    expected_md = "The relaxed structure has lattice parameter a = 2.81 Å."
    assert section.content_markdown == expected_md
    assert section.data == {"a": 2.81, "b": 2.81, "c": 14.05}
    assert section.evidence_labels == ["A-computed", "A-compared"]


def test_report_section_evidence_labels_is_list() -> None:
    """ReportSection.evidence_labels must be a list of strings."""
    section = _minimal_section()
    assert isinstance(section.evidence_labels, list)
    for label in section.evidence_labels:
        assert isinstance(label, str)


def test_report_section_data_is_dict() -> None:
    """ReportSection.data must be a dict."""
    section = _minimal_section()
    assert isinstance(section.data, dict)


# ---------------------------------------------------------------------------
# ReportRecord tests (6)
# ---------------------------------------------------------------------------


def test_report_record_creation_with_all_fields() -> None:
    """ReportRecord can be created with all required fields populated."""
    record = _minimal_report_record()
    assert record.schema_version == "1.0.0"
    assert record.material_id == "mat-001"
    assert record.report_type == "structural_analysis"
    assert record.raw_user_input == "LiCoO2"
    assert record.title == "Structural Analysis: LiCoO2"
    assert isinstance(record.provenance, ProvenanceRecord)


def test_report_record_sections_is_ordered_list() -> None:
    """ReportRecord.sections is an ordered list of ReportSection objects."""
    s1 = ReportSection(heading="A", content_markdown="a", data={}, evidence_labels=[])
    s2 = ReportSection(heading="B", content_markdown="b", data={}, evidence_labels=[])
    record = ReportRecord(
        schema_version="1.0.0",
        report_id=uuid.uuid4(),
        material_id="mat-001",
        workflow_result_id=uuid.uuid4(),
        report_type="structural_analysis",
        raw_user_input="LiCoO2",
        title="Test",
        sections=[s1, s2],
        evidence_summary={},
        warnings=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        provenance=_minimal_provenance(),
    )
    assert len(record.sections) == 2
    assert record.sections[0].heading == "A"
    assert record.sections[1].heading == "B"


def test_report_record_evidence_summary_is_dict() -> None:
    """ReportRecord.evidence_summary is a dict."""
    record = _minimal_report_record()
    assert isinstance(record.evidence_summary, dict)


def test_report_record_serializes_to_json() -> None:
    """ReportRecord serializes to JSON without error."""
    record = _minimal_report_record()
    json_str = record.model_dump_json()
    data = json.loads(json_str)
    assert data["schema_version"] == "1.0.0"
    assert data["material_id"] == "mat-001"
    assert data["raw_user_input"] == "LiCoO2"


def test_report_record_deserializes_from_json() -> None:
    """ReportRecord round-trips through JSON serialization."""
    original = _minimal_report_record()
    json_str = original.model_dump_json()
    restored = ReportRecord.model_validate_json(json_str)
    assert restored.schema_version == original.schema_version
    assert restored.material_id == original.material_id
    assert restored.raw_user_input == original.raw_user_input
    assert len(restored.sections) == len(original.sections)


def test_report_record_has_raw_user_input() -> None:
    """ReportRecord has a raw_user_input field storing original user input."""
    record = ReportRecord(
        schema_version="1.0.0",
        report_id=uuid.uuid4(),
        material_id="mat-001",
        workflow_result_id=uuid.uuid4(),
        report_type="structural_analysis",
        raw_user_input="mp-22526",
        title="Test",
        sections=[],
        evidence_summary={},
        warnings=[],
        generated_at=datetime(2026, 1, 1, tzinfo=UTC),
        provenance=_minimal_provenance(),
    )
    assert record.raw_user_input == "mp-22526"


# ---------------------------------------------------------------------------
# BenchmarkRow tests (5)
# ---------------------------------------------------------------------------


def test_benchmark_row_creation() -> None:
    """BenchmarkRow can be created with all required fields."""
    row = _minimal_benchmark_row()
    assert row.formula == "LiCoO2"
    assert row.family == "layered_oxide"
    assert row.workflow_name == "structural_analysis"
    assert row.status == "success"
    assert row.failure_category is None


def test_benchmark_row_metrics_is_dict() -> None:
    """BenchmarkRow.metrics is a dict supporting all 24 benchmark metrics."""
    row = _minimal_benchmark_row()
    assert isinstance(row.metrics, dict)
    # Verify all 24 expected metric keys are present
    expected_keys = {
        "input_resolution",
        "structure_retrieval",
        "structure_normalization",
        "space_group_input",
        "relaxation_convergence",
        "relaxation_steps",
        "final_fmax",
        "final_energy",
        "lattice_param_deviation_a",
        "lattice_param_deviation_b",
        "lattice_param_deviation_c",
        "volume_deviation",
        "symmetry_preserved",
        "space_group_output",
        "min_bond_length",
        "max_bond_length",
        "evidence_labeling_complete",
        "report_generated",
        "runtime_seconds",
        "workflow_version",
        "angle_deviation_alpha",
        "angle_deviation_beta",
        "angle_deviation_gamma",
        "symprec_used",
    }
    assert expected_keys.issubset(row.metrics.keys())


def test_benchmark_row_failure_category_is_optional() -> None:
    """BenchmarkRow.failure_category is None on success and set on failure."""
    row_success = _minimal_benchmark_row()
    assert row_success.failure_category is None

    row_failure = BenchmarkRow(
        schema_version="1.0.0",
        benchmark_run_id=uuid.uuid4(),
        material_id="mat-002",
        formula="LiFePO4",
        family="olivine_polyanion",
        workflow_name="structural_analysis",
        workflow_version="1.0.0",
        status="hard_failure",
        metrics={},
        failure_category="retrieval_failure",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        provenance=_minimal_provenance(),
    )
    assert row_failure.failure_category == "retrieval_failure"


def test_benchmark_row_status_validates_enum() -> None:
    """BenchmarkRow.status must be one of the allowed status values."""
    with pytest.raises(ValidationError):
        BenchmarkRow(
            schema_version="1.0.0",
            benchmark_run_id=uuid.uuid4(),
            material_id="mat-001",
            formula="LiCoO2",
            family="layered_oxide",
            workflow_name="structural_analysis",
            workflow_version="1.0.0",
            status="invalid_status",  # type: ignore[arg-type]
            metrics={},
            failure_category=None,
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            provenance=_minimal_provenance(),
        )


def test_benchmark_row_serializes_to_json() -> None:
    """BenchmarkRow serializes to JSON without error."""
    row = _minimal_benchmark_row()
    json_str = row.model_dump_json()
    data = json.loads(json_str)
    assert data["formula"] == "LiCoO2"
    assert data["status"] == "success"
    assert "metrics" in data


# ---------------------------------------------------------------------------
# BenchmarkSummary tests (4)
# ---------------------------------------------------------------------------


def test_benchmark_summary_creation() -> None:
    """BenchmarkSummary can be created with all required fields."""
    summary = _minimal_benchmark_summary()
    assert summary.benchmark_name == "phase1_structural_analysis"
    assert summary.materials_count == 1
    assert isinstance(summary.provenance, ProvenanceRecord)


def test_benchmark_summary_status_counts_is_dict() -> None:
    """BenchmarkSummary.status_counts is a dict with all status keys."""
    summary = _minimal_benchmark_summary()
    assert isinstance(summary.status_counts, dict)
    expected_keys = {
        "success",
        "partial_success",
        "soft_failure",
        "hard_failure",
        "infrastructure_failure",
    }
    assert expected_keys.issubset(summary.status_counts.keys())


def test_benchmark_summary_materials_count_matches_rows() -> None:
    """BenchmarkSummary rejects inconsistent materials_count / status_counts / rows."""
    with pytest.raises(ValidationError):
        BenchmarkSummary(
            schema_version="1.0.0",
            benchmark_run_id=uuid.uuid4(),
            benchmark_name="phase1",
            materials_count=3,  # wrong: doesn't match rows (1) or status_counts sum (1)
            status_counts={
                "success": 1,
                "partial_success": 0,
                "soft_failure": 0,
                "hard_failure": 0,
                "infrastructure_failure": 0,
            },
            rows=["rows/mat-001.json"],  # 1 row
            started_at=datetime(2026, 1, 1, tzinfo=UTC),
            completed_at=datetime(2026, 1, 1, 0, 10, tzinfo=UTC),
            runtime_seconds=10.0,
            provenance=_minimal_provenance(),
        )


def test_benchmark_summary_serializes_to_json() -> None:
    """BenchmarkSummary serializes to JSON without error."""
    summary = _minimal_benchmark_summary()
    json_str = summary.model_dump_json()
    data = json.loads(json_str)
    assert data["benchmark_name"] == "phase1_structural_analysis"
    assert data["materials_count"] == 1
    assert "rows" in data
