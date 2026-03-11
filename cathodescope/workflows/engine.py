"""Workflow engine.

Implements WorkflowEngine.run(): tool-agnostic step sequencer with
error handling, partial result preservation, and provenance recording.

The engine sequences step callables from a WorkflowDefinition. It:
- Creates a WorkflowContext before step 0.
- Calls each step_fn(context) in order, capturing timing.
- Wraps each ToolResult in a StepResult and updates context.step_results.
- Stops early on status='failure'; marks overall status='partial' on any
  status='partial' step; marks overall status='success' if all steps succeed.
- Never catches unexpected exceptions from step functions (non-swallowing).

Implemented in T-18.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import StepResult, WorkflowResult
from cathodescope.workflows.base import WorkflowContext, WorkflowRegistry

_TOOL_NAME = "workflow_engine"
_TOOL_VERSION = "0.1.0"


class WorkflowEngine:
    """Tool-agnostic step sequencer for CathodeScope workflows.

    The engine has no knowledge of individual tools. It receives a
    WorkflowRegistry at construction time and dispatches to registered step
    callables at runtime. Scientific logic lives exclusively in the tools, not
    here.

    Example::

        registry = WorkflowRegistry()
        registry.register(structural_analysis_workflow)
        engine = WorkflowEngine(registry)
        result = engine.run("structural_analysis", material, settings)
    """

    def __init__(self, registry: WorkflowRegistry) -> None:
        """Initialise the engine with a workflow registry.

        Args:
            registry: Registry containing all available workflow definitions.
        """
        self._registry = registry

    def run(
        self,
        workflow_name: str,
        material: Any,
        config: Any,
    ) -> WorkflowResult:
        """Run a named workflow on a material and return the full result.

        Executes each step in order. A step returning status='failure' stops
        execution immediately (partial results are preserved). A step returning
        status='partial' marks the overall result as 'partial'. All steps
        returning status='success' yields overall status='success'.

        Unexpected exceptions from step callables are NOT caught — they
        propagate to the caller unchanged.

        Args:
            workflow_name: Name of the registered workflow to run.
            material: Material to process. Will be CanonicalMaterial once T-03
                is done; currently accepts any value.
            config: Configuration for the run. Accepts CathodescopeSettings or
                a plain dict.

        Returns:
            WorkflowResult with all step results, overall status, timing,
            and a fully-populated provenance record.

        Raises:
            KeyError: If *workflow_name* is not registered.
            Any exception raised by a step function (not swallowed).
        """
        definition = self._registry.get(workflow_name)
        run_id = uuid.uuid4()
        started_at = datetime.now(UTC)

        context = WorkflowContext(
            workflow_run_id=str(run_id),
            started_at=started_at,
            material=material,
            config=config,
        )

        completed_steps: list[StepResult] = []
        overall_status: str = "success"

        for idx, step_spec in enumerate(definition.steps):
            step_started = datetime.now(UTC)
            # Unexpected exceptions propagate; only ToolResult failures are handled.
            tool_result = step_spec.step_fn(context)
            step_completed = datetime.now(UTC)

            step_result = StepResult(
                step_name=step_spec.name,
                step_index=idx,
                tool_result=tool_result,
                started_at=step_started,
                completed_at=step_completed,
            )
            context.step_results[step_spec.name] = step_result
            completed_steps.append(step_result)

            if tool_result.status == "failure":
                overall_status = "failure"
                break
            elif tool_result.status == "partial" and overall_status == "success":
                overall_status = "partial"

        completed_at = datetime.now(UTC)
        elapsed = (completed_at - started_at).total_seconds()

        # Extract material_id for the WorkflowResult record.
        material_id: str | None = None
        if hasattr(material, "material_id"):
            material_id = str(material.material_id)
        elif isinstance(material, str):
            material_id = material

        # Build config snapshot: accept pydantic models or plain dicts.
        config_snapshot: dict[str, Any] = {}
        if hasattr(config, "model_dump"):
            config_snapshot = config.model_dump(mode="json")
        elif isinstance(config, dict):
            config_snapshot = dict(config)

        provenance = create_provenance(
            created_by="cathodescope",
            tool_name=_TOOL_NAME,
            tool_version=_TOOL_VERSION,
            workflow_run_id=run_id,
            step_name=workflow_name,
            elapsed_seconds=elapsed,
            config_snapshot=config_snapshot,
        )

        # overall_status is Literal["success","failure","partial"] — matches WorkflowStatus  # noqa: E501
        return WorkflowResult(
            workflow_run_id=run_id,
            workflow_name=workflow_name,
            status=overall_status,  # type: ignore[arg-type]
            steps=completed_steps,
            provenance=provenance,
            material_id=material_id,
            started_at=started_at,
            completed_at=completed_at,
        )
