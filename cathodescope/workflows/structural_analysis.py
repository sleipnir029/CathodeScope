"""structural_analysis workflow definition.

7-step workflow: resolve → fetch → normalize → relax → compare → validate → report.
Registered with WorkflowRegistry as 'structural_analysis'.

Step order per architecture.md Section 4.3:
  0. resolve_input    -- input_resolver.resolve()
  1. fetch_structure  -- CathodescopeMPClient.fetch_by_mp_id() / fetch_by_formula()
  2. normalize        -- structure_normalizer.normalize()  [creates CanonicalMaterial]
  3. relax            -- structure_relaxer.relax()
  4. compare_reference -- reference_comparator.compare()
  5. validate         -- physics_validator.validate()
  6. generate_report  -- report_generator.generate()

Each step is a thin wrapper that extracts data from context and delegates to the
corresponding tool function.  No scientific logic lives here.

Implemented in T-19.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ToolResult, WorkflowResult
from cathodescope.workflows.base import (
    StepSpec,
    WorkflowContext,
    WorkflowDefinition,
    WorkflowRegistry,
)

# ---------------------------------------------------------------------------
# Module-level registry
# ---------------------------------------------------------------------------

REGISTRY: WorkflowRegistry = WorkflowRegistry()

# ---------------------------------------------------------------------------
# Runtime-dependency helpers (support config injection for tests)
# ---------------------------------------------------------------------------


def _get_mp_client(context: WorkflowContext) -> Any:
    """Return an mp_client from context.config or instantiate one.

    Checks for a ``mp_client`` attribute on ``context.config`` first.  If
    present, returns it directly (useful for dependency injection in tests).
    Otherwise creates a :class:`~cathodescope.tools.mp_client.CathodescopeMPClient`
    from the API key and cache dir stored in ``context.config``.
    """
    config = context.config
    if hasattr(config, "mp_client"):
        return config.mp_client
    from cathodescope.tools.mp_client import CathodescopeMPClient

    api_key: str = getattr(config, "mp_api_key", "")
    cache_dir: str = "artifacts/cache/mp"
    if hasattr(config, "cache") and hasattr(config.cache, "cache_dir"):
        cache_dir = config.cache.cache_dir
    return CathodescopeMPClient(api_key, cache_dir)


def _get_calculator(context: WorkflowContext) -> Any:
    """Return a calculator from context.config or instantiate MACE-MP-0.

    Checks for a ``calculator`` attribute on ``context.config`` first.  If
    present, returns it directly (useful for dependency injection in tests).
    Otherwise creates a MACE-MP-0 calculator via ``mace.calculators.mace_mp``.
    """
    config = context.config
    if hasattr(config, "calculator"):
        return config.calculator
    from mace.calculators import mace_mp

    return mace_mp(model="medium", device="cpu", default_dtype="float32")


def _make_canonical_material(
    fetch_data: dict[str, Any],
    normalize_data: dict[str, Any],
) -> Any:
    """Create a CanonicalMaterial from fetch + normalize step outputs.

    Called by :func:`_step_normalize` after a successful normalization.

    Args:
        fetch_data: ``tool_result.data`` from the ``fetch_structure`` step.
        normalize_data: ``tool_result.data`` from the ``normalize`` step.

    Returns:
        A fully-populated :class:`~cathodescope.models.material.CanonicalMaterial`.
    """
    from pymatgen.core.composition import Composition

    from cathodescope.models.material import CanonicalMaterial, classify_family

    space_group_info = normalize_data.get("space_group") or {}
    if isinstance(space_group_info, dict):
        space_group = space_group_info.get("symbol", "")
    else:
        space_group = str(space_group_info)

    formula: str = fetch_data.get("formula", "")
    try:
        reduced_formula = Composition(formula).reduced_formula
    except Exception:  # noqa: BLE001
        reduced_formula = formula

    family = classify_family(space_group, formula)

    prov = create_provenance(
        created_by="cathodescope",
        tool_name="structural_analysis",
        tool_version="1.0.0",
    )

    return CanonicalMaterial(
        formula=formula,
        reduced_formula=reduced_formula,
        family=family,
        structure=normalize_data["normalized_structure"],
        source="materials_project",
        mp_id=fetch_data.get("mp_id"),
        provenance=prov,
    )


def _build_partial_workflow_result(context: WorkflowContext) -> WorkflowResult:
    """Build a partial WorkflowResult from accumulated context step results.

    Called by :func:`_step_generate_report` so the report generator receives a
    WorkflowResult-like object with all preceding step results.

    Args:
        context: The current WorkflowContext with steps 0–5 in ``step_results``.

    Returns:
        A :class:`~cathodescope.models.results.WorkflowResult` with
        ``status="partial"`` and all currently-completed steps.
    """
    now = datetime.now(UTC)
    steps = list(context.step_results.values())

    try:
        run_id = uuid.UUID(context.workflow_run_id)
    except (ValueError, AttributeError):
        run_id = uuid.uuid4()

    prov = create_provenance(
        created_by="cathodescope",
        tool_name="structural_analysis",
        tool_version="1.0.0",
        workflow_run_id=run_id,
    )

    return WorkflowResult(
        workflow_run_id=run_id,
        workflow_name="structural_analysis",
        status="partial",
        steps=steps,
        provenance=prov,
        started_at=context.started_at,
        completed_at=now,
    )


# ---------------------------------------------------------------------------
# Step functions (private — one per pipeline step)
# ---------------------------------------------------------------------------


def _step_resolve_input(context: WorkflowContext) -> ToolResult:
    """Step 0: Resolve raw user input (formula or mp-id) to a NormalizedQuery.

    Reads ``context.material`` as the raw string and delegates to
    :func:`~cathodescope.tools.input_resolver.resolve`.
    """
    from cathodescope.tools import input_resolver

    mp_client = _get_mp_client(context)
    return input_resolver.resolve(str(context.material), mp_client)


def _step_fetch_structure(context: WorkflowContext) -> ToolResult:
    """Step 1: Fetch structure and metadata from the Materials Project.

    Reads ``mp_id`` from the ``resolve_input`` step result and calls
    ``fetch_by_mp_id``; falls back to ``fetch_by_formula`` when ``mp_id`` is
    absent.
    """
    mp_client = _get_mp_client(context)
    query_data = context.step_results["resolve_input"].tool_result.data or {}
    mp_id: str | None = query_data.get("mp_id")
    if mp_id:
        result: ToolResult = mp_client.fetch_by_mp_id(mp_id)
        return result
    result = mp_client.fetch_by_formula(query_data["formula"])
    return result


def _step_normalize(context: WorkflowContext) -> ToolResult:
    """Step 2: Normalize the retrieved structure to the conventional standard cell.

    Reads the structure dict, mp_id, and formula from the ``fetch_structure``
    step result and delegates to
    :func:`~cathodescope.tools.structure_normalizer.normalize`.

    On success, creates a
    :class:`~cathodescope.models.material.CanonicalMaterial` from the combined
    fetch + normalize data and updates ``context.material``.
    """
    from cathodescope.tools import structure_normalizer

    fetch_data = context.step_results["fetch_structure"].tool_result.data or {}
    structure_dict: dict[str, Any] = fetch_data["structure"]
    mp_id: str | None = fetch_data.get("mp_id")
    formula: str | None = fetch_data.get("formula")

    result = structure_normalizer.normalize(
        structure_dict, mp_id=mp_id, formula=formula
    )
    if result.status == "success" and result.data:
        context.material = _make_canonical_material(fetch_data, result.data)
    return result


def _step_relax(context: WorkflowContext) -> ToolResult:
    """Step 3: Relax the normalized structure using MACE-MP-0 via ASE.

    Reads ``normalized_structure`` from the ``normalize`` step result.
    Uses the relaxation config from ``context.config`` (or defaults).
    """
    from pymatgen.core.structure import Structure

    from cathodescope.tools import structure_relaxer

    normalize_data = context.step_results["normalize"].tool_result.data or {}
    structure = Structure.from_dict(normalize_data["normalized_structure"])
    calculator = _get_calculator(context)

    from cathodescope.config.settings import RelaxationConfig

    relax_config = getattr(context.config, "relaxation", None)
    if relax_config is None:
        relax_config = RelaxationConfig()

    return structure_relaxer.relax(structure, relax_config, calculator)


def _step_compare_reference(context: WorkflowContext) -> ToolResult:
    """Step 4: Compare the relaxed structure against the MP reference.

    Reads the relaxed structure from the ``relax`` step result and the original
    (reference) structure from the ``fetch_structure`` step result.
    """
    from pymatgen.core.structure import Structure

    from cathodescope.tools import reference_comparator

    relax_data = context.step_results["relax"].tool_result.data or {}
    fetch_data = context.step_results["fetch_structure"].tool_result.data or {}

    relaxed = Structure.from_dict(relax_data["relaxed_structure"])
    reference = Structure.from_dict(fetch_data["structure"])

    comparison_config = getattr(context.config, "comparison", None)
    return reference_comparator.compare(relaxed, reference, comparison_config)


def _step_validate(context: WorkflowContext) -> ToolResult:
    """Step 5: Validate the relaxed structure with physics checks and evidence labels.

    Assembles a context dict from the ``relax`` and ``compare_reference`` step
    results and passes it to
    :func:`~cathodescope.tools.physics_validator.validate`.
    ``context.material`` must be a CanonicalMaterial by this step (set in step 2).
    """
    from cathodescope.tools import physics_validator

    relax_data = context.step_results["relax"].tool_result.data or {}
    compare_data = context.step_results["compare_reference"].tool_result.data

    validation_context: dict[str, Any] = {
        "relaxed_structure": relax_data.get("relaxed_structure"),
        "convergence_info": relax_data.get("convergence_info"),
        "comparison_result": compare_data,
    }
    validation_config = getattr(context.config, "validation", None)
    return physics_validator.validate(
        validation_context, context.material, validation_config
    )


def _step_generate_report(context: WorkflowContext) -> ToolResult:
    """Step 6: Generate JSON and Markdown reports from all preceding step results.

    Builds a partial WorkflowResult from ``context.step_results`` and passes it
    together with ``context.material`` to
    :func:`~cathodescope.tools.report_generator.generate`.
    """
    from cathodescope.tools import report_generator

    partial_result = _build_partial_workflow_result(context)
    return report_generator.generate(partial_result, context.material)


# ---------------------------------------------------------------------------
# Workflow definition and registration
# ---------------------------------------------------------------------------

DEFINITION: WorkflowDefinition = WorkflowDefinition(
    name="structural_analysis",
    version="1.0.0",
    steps=[
        StepSpec(name="resolve_input", step_fn=_step_resolve_input),
        StepSpec(name="fetch_structure", step_fn=_step_fetch_structure),
        StepSpec(name="normalize", step_fn=_step_normalize),
        StepSpec(name="relax", step_fn=_step_relax),
        StepSpec(name="compare_reference", step_fn=_step_compare_reference),
        StepSpec(name="validate", step_fn=_step_validate),
        StepSpec(name="generate_report", step_fn=_step_generate_report),
    ],
)

REGISTRY.register(DEFINITION)
