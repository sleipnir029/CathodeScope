"""T-30: Agent scaffolding tests.

Verifies that cathodescope.agent is an importable empty stub with no
functionality and no forbidden dependencies.
"""

from __future__ import annotations

import pathlib

AGENT_DIR = (
    pathlib.Path(__file__).parent.parent.parent.parent / "cathodescope" / "agent"
)


def test_agent_module_importable() -> None:
    """cathodescope.agent imports without error and exposes __all__."""
    import cathodescope.agent as agent

    assert hasattr(agent, "__all__")
    assert agent.__all__ == []


def test_agent_directory_contains_only_init() -> None:
    """cathodescope/agent/ contains exactly one file: __init__.py.

    No agent functionality is permitted at Phase 4 — the directory is a
    clean boundary stub for Phase 5 to build on.
    """
    assert AGENT_DIR.exists(), "cathodescope/agent/ directory does not exist"
    py_files = sorted(AGENT_DIR.rglob("*.py"))
    assert len(py_files) == 1, (
        f"Expected only __init__.py in agent/, found: {[f.name for f in py_files]}"
    )
    assert py_files[0].name == "__init__.py", (
        f"Unexpected file in agent/: {py_files[0].name}"
    )
