"""Unit tests for cathodescope.tools.report_generator.

7 tests implemented in T-17.
"""

from datetime import UTC, datetime
from typing import Any

from cathodescope.models.material import CanonicalMaterial
from cathodescope.models.provenance import ProvenanceRecord, create_provenance
from cathodescope.models.results import StepResult, ToolResult, WorkflowResult
from cathodescope.tools.report_generator import generate

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
            {"space_group": "R-3m", "atom_count": 12, "conventional_cell": True},
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
            },
            "A-computed",
        ),
        _make_step(
            "compare_reference",
            4,
            {
                "lattice_deviations": {"a": 0.53, "b": 0.53, "c": 0.22},
                "volume_deviation": 1.28,
                "symmetry_preserved": True,
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
# 7 tests
# ---------------------------------------------------------------------------


def test_report_generator_returns_tool_result() -> None:
    """generate() returns a ToolResult instance."""
    result = generate(_make_workflow_result(), _make_material())
    assert isinstance(result, ToolResult)


def test_report_generator_evidence_type_is_metadata() -> None:
    """generate() sets evidence_type to 'metadata' (excluded from evidence counts)."""
    result = generate(_make_workflow_result(), _make_material())
    assert result.evidence_type == "metadata"


def test_report_generator_data_contains_report_json() -> None:
    """generate() data contains a 'report_json' key with a dict representation."""
    result = generate(_make_workflow_result(), _make_material())
    assert result.data is not None
    assert "report_json" in result.data
    assert isinstance(result.data["report_json"], dict)


def test_report_generator_data_contains_report_markdown() -> None:
    """generate() data contains a 'report_markdown' key with a non-empty string."""
    result = generate(_make_workflow_result(), _make_material())
    assert result.data is not None
    assert "report_markdown" in result.data
    assert isinstance(result.data["report_markdown"], str)
    assert len(result.data["report_markdown"]) > 0


def test_report_generator_data_contains_evidence_summary() -> None:
    """generate() data contains an 'evidence_summary' key with a dict."""
    result = generate(_make_workflow_result(), _make_material())
    assert result.data is not None
    assert "evidence_summary" in result.data
    assert isinstance(result.data["evidence_summary"], dict)


def test_report_generator_handles_missing_step_data() -> None:
    """generate() succeeds when some workflow steps have no data."""
    now = datetime.now(UTC)
    minimal_workflow = WorkflowResult(
        workflow_name="structural_analysis",
        status="partial",
        steps=[
            _make_step("resolve_input", 0, None, "A-retrieved"),
        ],
        provenance=_make_provenance("workflow_engine"),
        started_at=now,
        completed_at=now,
    )
    result = generate(minimal_workflow, _make_material())
    assert isinstance(result, ToolResult)
    assert result.status == "success"


def test_report_generator_provenance_is_populated() -> None:
    """generate() populates the ToolResult provenance field."""
    result = generate(_make_workflow_result(), _make_material())
    assert result.provenance is not None
    assert result.provenance.tool_name == "report_generator"
