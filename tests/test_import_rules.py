"""Import rule enforcement tests for CathodeScope.

T-00: Preserves the original scaffold sanity tests (package importable,
      all subpackages importable).
T-27: Implements 10 AST-based tests that verify each package only imports
      from allowed packages per dependency_graph.md Section 6.

Uses ast.parse() for static analysis — never runtime import checks.
"""

from __future__ import annotations

import ast
import pathlib
from collections.abc import Iterator

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CATHODESCOPE_ROOT = pathlib.Path(__file__).parent.parent / "cathodescope"


def _iter_py_files(package_dir: pathlib.Path) -> Iterator[pathlib.Path]:
    """Yield every .py file under *package_dir*, sorted for determinism."""
    yield from sorted(package_dir.rglob("*.py"))


def _get_cathodescope_imports(filepath: pathlib.Path) -> set[str]:
    """Return the set of cathodescope sub-module names imported in *filepath*.

    Handles both ``import cathodescope.foo.bar`` and
    ``from cathodescope.foo.bar import baz`` forms.
    Returns fully-qualified module names, e.g. ``"cathodescope.tools.mp_client"``.
    """
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("cathodescope."):
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("cathodescope."):
                imports.add(node.module)
    return imports


def _violations(
    package_name: str, forbidden_prefix: str
) -> list[tuple[pathlib.Path, str]]:
    """Return (file, import) pairs where a file in *package_name* imports
    from *forbidden_prefix*.
    """
    result: list[tuple[pathlib.Path, str]] = []
    package_dir = CATHODESCOPE_ROOT / package_name
    if not package_dir.exists():
        return result
    for filepath in _iter_py_files(package_dir):
        for imp in _get_cathodescope_imports(filepath):
            if imp.startswith(forbidden_prefix):
                result.append((filepath, imp))
    return result


# ---------------------------------------------------------------------------
# T-00 scaffold tests (preserved)
# ---------------------------------------------------------------------------


def test_package_importable() -> None:
    """cathodescope imports successfully and exposes __version__."""
    import cathodescope

    assert hasattr(cathodescope, "__version__")
    assert cathodescope.__version__ == "0.1.0"


def test_all_subpackages_importable() -> None:
    """Every cathodescope subpackage imports without error."""
    import cathodescope.app  # noqa: F401
    import cathodescope.benchmark  # noqa: F401
    import cathodescope.config  # noqa: F401
    import cathodescope.models  # noqa: F401
    import cathodescope.provenance  # noqa: F401
    import cathodescope.reporting  # noqa: F401
    import cathodescope.tools  # noqa: F401
    import cathodescope.validation  # noqa: F401
    import cathodescope.workflows  # noqa: F401


# ---------------------------------------------------------------------------
# T-27 import rule enforcement tests (10 tests)
# ---------------------------------------------------------------------------


def test_models_do_not_import_from_cathodescope_tools() -> None:
    """models/* must not import from cathodescope.tools.

    Per dependency_graph.md Section 6: models/* may only import from the
    standard library, pydantic, and pymatgen — never from other cathodescope
    packages outside models/.
    """
    violations = _violations("models", "cathodescope.tools")
    assert not violations, (
        "models/* illegally imports from cathodescope.tools — "
        f"violations: {violations}"
    )


def test_models_do_not_import_from_cathodescope_config() -> None:
    """models/* must not import from cathodescope.config.

    Per dependency_graph.md Section 6: config/* depends on models/*, not the
    reverse. A models → config import would create a circular dependency.
    """
    violations = _violations("models", "cathodescope.config")
    assert not violations, (
        "models/* illegally imports from cathodescope.config — "
        f"violations: {violations}"
    )


def test_tools_do_not_import_from_each_other() -> None:
    """tools/* must not import from other cathodescope.tools modules.

    Per dependency_graph.md Section 6: each tool is standalone. A tool
    importing from another tool creates hidden coupling and is a code-review
    rejection.
    """
    tools_dir = CATHODESCOPE_ROOT / "tools"
    cross_tool_violations: list[tuple[pathlib.Path, str]] = []
    for filepath in _iter_py_files(tools_dir):
        for imp in _get_cathodescope_imports(filepath):
            if imp.startswith("cathodescope.tools"):
                cross_tool_violations.append((filepath, imp))
    assert not cross_tool_violations, (
        "tools/* illegally imports from other cathodescope.tools modules — "
        f"violations: {cross_tool_violations}"
    )


def test_validation_does_not_import_from_tools() -> None:
    """validation/* must not import from cathodescope.tools.

    Per dependency_graph.md Section 6: validation modules are pure functions
    that depend only on models/* (and pymatgen/numpy). They must not reach
    into the tool layer.
    """
    violations = _violations("validation", "cathodescope.tools")
    assert not violations, (
        "validation/* illegally imports from cathodescope.tools — "
        f"violations: {violations}"
    )


def test_validation_does_not_import_from_workflows() -> None:
    """validation/* must not import from cathodescope.workflows.

    Per dependency_graph.md Section 6: validation is below workflows in the
    layer stack. A validation → workflow import would be a layer inversion.
    """
    violations = _violations("validation", "cathodescope.workflows")
    assert not violations, (
        "validation/* illegally imports from cathodescope.workflows — "
        f"violations: {violations}"
    )


def test_reporting_does_not_import_from_tools() -> None:
    """reporting/* must not import from cathodescope.tools.

    Per dependency_graph.md Section 6: reporting depends only on models/*.
    It must remain agnostic of the tool layer so reports can be regenerated
    from stored WorkflowResult objects without re-running tools.
    """
    violations = _violations("reporting", "cathodescope.tools")
    assert not violations, (
        "reporting/* illegally imports from cathodescope.tools — "
        f"violations: {violations}"
    )


def test_reporting_does_not_import_from_workflows() -> None:
    """reporting/* must not import from cathodescope.workflows.

    Per dependency_graph.md Section 6: reporting is a pure rendering layer
    and must not depend on the orchestration layer.
    """
    violations = _violations("reporting", "cathodescope.workflows")
    assert not violations, (
        "reporting/* illegally imports from cathodescope.workflows — "
        f"violations: {violations}"
    )


def test_provenance_does_not_import_from_tools() -> None:
    """provenance/* must not import from cathodescope.tools.

    Per dependency_graph.md Section 6: provenance/store.py depends only on
    models/*. It is a pure persistence layer and must not depend on any tool.
    """
    violations = _violations("provenance", "cathodescope.tools")
    assert not violations, (
        "provenance/* illegally imports from cathodescope.tools — "
        f"violations: {violations}"
    )


def test_benchmark_does_not_import_from_tools_directly() -> None:
    """benchmark/* must not import from cathodescope.tools directly.

    Per dependency_graph.md Section 6: benchmark/* orchestrates via
    workflows/*, never by calling tools directly. This preserves the
    invariant that tool details are hidden behind the workflow interface.
    """
    violations = _violations("benchmark", "cathodescope.tools")
    assert not violations, (
        "benchmark/* illegally imports from cathodescope.tools directly — "
        f"violations: {violations}"
    )


def test_agent_directory_is_empty() -> None:
    """agent/ either absent or contains only __init__.py with no tool imports.

    Per dependency_graph.md Section 6: the agent layer (Phase 5) may depend
    on models/* and workflows/engine.py, but never on tools/* directly.
    At this stage (Phase 4) the directory is expected to be absent or empty.
    """
    agent_dir = CATHODESCOPE_ROOT / "agent"
    if not agent_dir.exists():
        # T-30 not yet executed — acceptable at Phase 4
        return
    py_files = list(_iter_py_files(agent_dir))
    non_init = [f for f in py_files if f.name != "__init__.py"]
    assert not non_init, (
        f"agent/ contains unexpected source files beyond __init__.py: {non_init}"
    )
    violations = _violations("agent", "cathodescope.tools")
    assert not violations, (
        "agent/* illegally imports from cathodescope.tools — "
        f"violations: {violations}"
    )
