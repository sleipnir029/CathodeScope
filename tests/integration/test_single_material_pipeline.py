"""Integration tests for the single-material structural_analysis pipeline.

LiCoO2 end-to-end test (T-20): 14 tests verifying the full pipeline with
real MACE-MP-0 against cached MP fixtures.

All tests are marked @pytest.mark.integration.  They require MACE-MP-0 to
be installed and are excluded from regular CI via ``-m "not integration"``.

LiFePO4 and LiMn2O4 tests are implemented in T-21.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ErrorRecord, ToolResult, WorkflowResult
from cathodescope.provenance.store import ArtifactStore
from cathodescope.workflows.engine import WorkflowEngine
from cathodescope.workflows.structural_analysis import REGISTRY

# ---------------------------------------------------------------------------
# Offline MP client backed by test fixture files
# ---------------------------------------------------------------------------

_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "mp_responses"

_FORMULA_TO_MP_ID: dict[str, str] = {
    "LiCoO2": "mp-22526",
    "LiFePO4": "mp-19017",
    "LiMn2O4": "mp-18767",
}


class _FixtureMPClient:
    """Offline MP client that reads from local fixture JSON files.

    Satisfies the _MPClientProtocol duck-type required by input_resolver.
    Never makes network calls.
    """

    def fetch_by_mp_id(self, mp_id: str) -> ToolResult:
        """Return fixture data for the given MP ID."""
        fixture_path = _FIXTURES_DIR / f"{mp_id}.json"
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

    def fetch_by_formula(self, formula: str) -> ToolResult:
        """Return fixture data for the given formula."""
        mp_id = _FORMULA_TO_MP_ID.get(formula)
        if mp_id:
            return self.fetch_by_mp_id(mp_id)
        return ToolResult(
            tool_name="mp_client",
            status="failure",
            error=ErrorRecord(
                error_type="InputError",
                message=f"No fixture available for formula {formula!r}",
                source="_FixtureMPClient",
            ),
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="mp_client",
                tool_version="0.1.0",
            ),
        )


# ---------------------------------------------------------------------------
# Minimal integration config (duck-typed — no import of CathodescopeSettings)
# ---------------------------------------------------------------------------


@dataclass
class _IntegrationConfig:
    """Minimal config object for integration tests.

    Provides ``mp_client`` and ``calculator`` attributes so the workflow
    step helpers ``_get_mp_client`` and ``_get_calculator`` pick them up via
    ``hasattr`` checks rather than constructing real instances.
    """

    mp_client: Any = field(default_factory=_FixtureMPClient)
    calculator: Any = None

    def model_dump(self, *, mode: str = "json") -> dict[str, Any]:
        """Return a minimal config snapshot for provenance recording."""
        return {
            "mode": "integration_test",
            "mp_client": "fixture",
            "calculator": "injected",
        }


# ---------------------------------------------------------------------------
# Module helpers
# ---------------------------------------------------------------------------


def _make_engine() -> WorkflowEngine:
    """Return a WorkflowEngine backed by the structural_analysis registry."""
    return WorkflowEngine(REGISTRY)


# ---------------------------------------------------------------------------
# Module-scoped fixtures (MACE model loaded once per test session)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def mace_calculator() -> Any:
    """Load MACE-MP-0 once and share across the entire integration test module."""
    from mace.calculators import mace_mp

    return mace_mp(model="medium", device="cpu", default_dtype="float32")


@pytest.fixture(scope="module")
def licoo2_run(
    tmp_path_factory: pytest.TempPathFactory, mace_calculator: Any
) -> tuple[WorkflowResult, Path]:
    """Run the LiCoO2 structural_analysis pipeline once using real MACE-MP-0.

    Returns (WorkflowResult, artifacts_dir) so individual tests can inspect
    the result and exercise artifact storage without re-running relaxation.
    """
    artifacts_dir: Path = tmp_path_factory.mktemp("licoo2_artifacts")
    config = _IntegrationConfig(
        mp_client=_FixtureMPClient(),
        calculator=mace_calculator,
    )
    engine = _make_engine()
    result: WorkflowResult = engine.run("structural_analysis", "mp-22526", config)
    return result, artifacts_dir


# ---------------------------------------------------------------------------
# T-20: 14 integration tests for the LiCoO2 pipeline
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_licoo2_end_to_end_produces_workflow_result(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """Engine returns a WorkflowResult instance."""
    result, _ = licoo2_run
    assert isinstance(result, WorkflowResult)


@pytest.mark.integration
def test_licoo2_workflow_status_is_success(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """All 7 steps succeed → overall status is 'success'."""
    result, _ = licoo2_run
    step_info = ", ".join(
        f"{s.step_name}={s.tool_result.status}" for s in result.steps
    )
    assert result.status == "success", f"Pipeline failed. Steps: {step_info}"


@pytest.mark.integration
def test_licoo2_all_steps_completed(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """All 7 pipeline steps are present in the result."""
    result, _ = licoo2_run
    assert len(result.steps) == 7
    step_names = [s.step_name for s in result.steps]
    assert step_names == [
        "resolve_input",
        "fetch_structure",
        "normalize",
        "relax",
        "compare_reference",
        "validate",
        "generate_report",
    ]


@pytest.mark.integration
def test_licoo2_lattice_deviation_a_below_2_percent(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """LiCoO2 a-axis lattice deviation is within 2% of the MP reference.

    MP reference: a ~ 2.836 Å (conventional hex cell).
    Threshold per scientific_validity_matrix.md Row 4.
    """
    result, _ = licoo2_run
    compare_data = result.steps[4].tool_result.data  # compare_reference = step 4
    assert compare_data is not None, "compare_reference step returned no data"
    lattice_devs: dict[str, float] = compare_data["lattice_deviations"]
    a_dev = lattice_devs["a"]
    assert a_dev < 2.0, (
        f"LiCoO2 a-axis deviation {a_dev:.3f}% exceeds 2% threshold. "
        "Deviation computed as |relaxed - reference| / reference × 100."
    )


@pytest.mark.integration
def test_licoo2_lattice_deviation_c_below_2_percent(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """LiCoO2 c-axis lattice deviation is within 2% of the MP reference.

    MP reference: c ~ 14.083 Å (conventional hex cell).
    Threshold per scientific_validity_matrix.md Row 4.
    """
    result, _ = licoo2_run
    compare_data = result.steps[4].tool_result.data
    assert compare_data is not None
    lattice_devs: dict[str, float] = compare_data["lattice_deviations"]
    c_dev = lattice_devs["c"]
    assert c_dev < 2.0, (
        f"LiCoO2 c-axis deviation {c_dev:.3f}% exceeds 2% threshold. "
        "Deviation computed as |relaxed - reference| / reference × 100."
    )


@pytest.mark.integration
def test_licoo2_volume_deviation_below_5_percent(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """LiCoO2 unit-cell volume deviation is within 5% of the MP reference.

    Threshold per scientific_validity_matrix.md Row 4 / benchmark_spec.md.
    """
    result, _ = licoo2_run
    compare_data = result.steps[4].tool_result.data
    assert compare_data is not None
    vol_dev: float = compare_data["volume_deviation"]
    assert vol_dev < 5.0, (
        f"LiCoO2 volume deviation {vol_dev:.3f}% exceeds 5% threshold. "
        "Deviation computed as |relaxed - reference| / reference × 100."
    )


@pytest.mark.integration
def test_licoo2_symmetry_preserved(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """Normalization preserves the R-3m space group for LiCoO2.

    Criterion per scientific_validity_matrix.md Row 2 / Gate 1.
    """
    result, _ = licoo2_run
    normalize_data = result.steps[2].tool_result.data  # normalize = step 2
    assert normalize_data is not None
    space_group_info = normalize_data.get("space_group")
    if isinstance(space_group_info, dict):
        symbol: str = space_group_info.get("symbol", "")
    else:
        symbol = str(space_group_info) if space_group_info else ""
    assert symbol == "R-3m", (
        f"Expected space group R-3m for LiCoO2, got {symbol!r}. "
        "Per scientific_validity_matrix.md Row 2: space group must be preserved."
    )


@pytest.mark.integration
def test_licoo2_report_generated(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """Report step produces a non-empty JSON report and Markdown string."""
    result, _ = licoo2_run
    report_step = result.steps[6]  # generate_report = step 6
    assert report_step.tool_result.status == "success"
    report_data = report_step.tool_result.data
    assert report_data is not None
    assert "report_json" in report_data, "Missing 'report_json' key"
    assert "report_markdown" in report_data, "Missing 'report_markdown' key"
    assert isinstance(report_data["report_markdown"], str)
    assert len(report_data["report_markdown"]) > 0


@pytest.mark.integration
def test_licoo2_all_evidence_labels_are_level_a(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """All scientific-step evidence types are Level A for the benchmarked LiCoO2.

    LiCoO2 belongs to the layered_oxide family (benchmarked) so no B/C
    downgrade is expected per scientific_validity_matrix.md Section 3 Part A.
    """
    result, _ = licoo2_run
    _scientific_steps = {
        "fetch_structure",
        "normalize",
        "relax",
        "compare_reference",
        "validate",
    }
    for step in result.steps:
        if step.step_name not in _scientific_steps:
            continue
        et = step.tool_result.evidence_type
        assert et is not None and et.startswith("A"), (
            f"Step {step.step_name!r} has non-Level-A evidence type: {et!r}. "
            "LiCoO2 (layered_oxide, benchmarked) must yield all Level-A labels."
        )


@pytest.mark.integration
def test_licoo2_artifacts_stored_correctly(
    licoo2_run: tuple[WorkflowResult, Path],
    tmp_path: Path,
) -> None:
    """Workflow result can be written to ArtifactStore at the expected path."""
    result, _ = licoo2_run
    store = ArtifactStore(tmp_path / "artifacts")
    run_id = str(result.workflow_run_id)
    store.write_workflow_result(run_id, result.model_dump(mode="json"))
    expected = tmp_path / "artifacts" / "workflows" / run_id / "result.json"
    assert expected.exists(), f"Workflow result not found at expected path: {expected}"


@pytest.mark.integration
def test_licoo2_provenance_complete(
    licoo2_run: tuple[WorkflowResult, Path],
) -> None:
    """WorkflowResult provenance record has all required fields populated."""
    result, _ = licoo2_run
    prov = result.provenance
    assert prov.created_by == "cathodescope"
    assert prov.tool_name is not None and prov.tool_name != ""
    assert prov.tool_version is not None and prov.tool_version != ""
    assert prov.cathodescope_version is not None
    assert prov.workflow_run_id == result.workflow_run_id


@pytest.mark.integration
def test_licoo2_rerun_produces_same_result_category(
    licoo2_run: tuple[WorkflowResult, Path],
    mace_calculator: Any,
) -> None:
    """Running the pipeline twice produces the same overall status category.

    Per SC-06 (Reproducibility Verification): result categories must be
    consistent across runs.
    """
    result1, _ = licoo2_run  # First run from module fixture

    config2 = _IntegrationConfig(
        mp_client=_FixtureMPClient(),
        calculator=mace_calculator,
    )
    engine = _make_engine()
    result2: WorkflowResult = engine.run("structural_analysis", "mp-22526", config2)

    assert result1.status == result2.status, (
        f"Run 1 status={result1.status!r}, Run 2 status={result2.status!r}. "
        "Pipeline must be reproducible: same result category on every run."
    )


@pytest.mark.integration
def test_licoo2_end_to_end_runs_offline(
    mace_calculator: Any,
) -> None:
    """Pipeline completes using fixture data with no live MP API calls.

    Patches cathodescope.tools.mp_client.MPRester to fail if invoked,
    proving the injected _FixtureMPClient bypasses all network access.
    """
    config = _IntegrationConfig(
        mp_client=_FixtureMPClient(),
        calculator=mace_calculator,
    )
    engine = _make_engine()

    with patch(
        "cathodescope.tools.mp_client.MPRester",
        side_effect=RuntimeError(
            "MPRester should not be called in offline test — "
            "pipeline must use injected fixture client only."
        ),
    ):
        result: WorkflowResult = engine.run("structural_analysis", "mp-22526", config)

    assert result.status == "success", (
        f"Offline pipeline failed with status {result.status!r}. "
        "Check that _FixtureMPClient is properly injected via config."
    )


@pytest.mark.integration
def test_licoo2_integrity_check_passes(
    licoo2_run: tuple[WorkflowResult, Path],
    tmp_path: Path,
) -> None:
    """ArtifactStore.verify_integrity returns True after storing the workflow result.

    Per artifact_schema.md Section 7: integrity check verifies that
    workflows/{run_id}/result.json exists.
    """
    result, _ = licoo2_run
    store = ArtifactStore(tmp_path / "artifacts")
    run_id = str(result.workflow_run_id)
    store.write_workflow_result(run_id, result.model_dump(mode="json"))
    assert store.verify_integrity(run_id) is True
