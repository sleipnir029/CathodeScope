"""Workflow base classes.

Implements:
- StepSpec: specification for a single workflow step (name + callable).
- WorkflowDefinition: ordered list of steps with name and version metadata.
- WorkflowContext: typed dataclass for inter-step state accumulation.
- WorkflowRegistry: registry mapping workflow names to WorkflowDefinitions.

Implemented in T-18.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Imported for type annotations only; not available until T-02 is done
    # for StepResult, which IS done.
    from cathodescope.models.results import StepResult, ToolResult


@dataclasses.dataclass
class StepSpec:
    """Specification for a single step in a workflow.

    Attributes:
        name: Unique step name within the workflow (e.g. "fetch_structure").
        step_fn: Callable that accepts a WorkflowContext and returns a ToolResult.
    """

    name: str
    step_fn: Callable[[WorkflowContext], ToolResult]


@dataclasses.dataclass
class WorkflowDefinition:
    """Declarative step sequence for a named workflow.

    Attributes:
        name: Workflow name used as the registry key (e.g. "structural_analysis").
        version: Semantic version string (e.g. "1.0.0").
        steps: Ordered list of StepSpec objects defining the pipeline.
    """

    name: str
    version: str
    steps: list[StepSpec]


@dataclasses.dataclass
class WorkflowContext:
    """Typed dataclass for inter-step state passing.

    The engine creates one WorkflowContext per run and passes it to every
    step function. Steps read prior results from ``step_results`` and may
    read ``material`` and ``config``, but only the engine mutates any field.

    Attributes:
        workflow_run_id: UUID string identifying this specific run.
        started_at: UTC datetime when the workflow started.
        material: The material being processed. Typed as Any until T-03
            implements CanonicalMaterial; will be tightened in T-19.
        config: Workflow configuration snapshot (CathodescopeSettings or dict).
        step_results: Mapping of step_name → StepResult, accumulated as steps
            complete. Populated by the engine before each subsequent step runs.
        normalized_query: Resolved query object populated after the
            resolve_input step completes. None until that step runs.
    """

    workflow_run_id: str
    started_at: datetime
    material: Any  # CanonicalMaterial once T-03 is done
    config: Any
    step_results: dict[str, StepResult] = dataclasses.field(default_factory=dict)
    normalized_query: Any = None  # NormalizedQuery once T-03 is done


class WorkflowRegistry:
    """Registry mapping workflow names to WorkflowDefinitions.

    Simple dict-backed registry for Phase 1. No plugin framework needed yet.

    Example::

        registry = WorkflowRegistry()
        registry.register(my_workflow_definition)
        defn = registry.get("structural_analysis")
    """

    def __init__(self) -> None:
        """Initialise an empty registry."""
        self._workflows: dict[str, WorkflowDefinition] = {}

    def register(self, definition: WorkflowDefinition) -> None:
        """Register a workflow definition.

        If a workflow with the same name already exists it is overwritten.

        Args:
            definition: The WorkflowDefinition to register.
        """
        self._workflows[definition.name] = definition

    def get(self, name: str) -> WorkflowDefinition:
        """Return the WorkflowDefinition registered under *name*.

        Args:
            name: Workflow name as used in ``WorkflowDefinition.name``.

        Returns:
            The matching WorkflowDefinition.

        Raises:
            KeyError: If no workflow with that name is registered.
        """
        if name not in self._workflows:
            raise KeyError(f"Workflow '{name}' is not registered.")
        return self._workflows[name]

    def list(self) -> list[WorkflowDefinition]:
        """Return all registered WorkflowDefinitions in insertion order.

        Returns:
            List of WorkflowDefinition objects.
        """
        return list(self._workflows.values())
