"""CathodeScope validation layer.

Pure validation functions with no tool dependencies.
Depends only on models/* and external libs (pymatgen, numpy).
Implemented in T-12 and T-13.
"""

from typing import Any, TypedDict


class CheckResult(TypedDict):
    """Structured result from a single validation check.

    Every check function returns a ``CheckResult`` dict with these six keys.
    All check results are structured to allow programmatic inspection
    and human-readable reporting.
    """

    check_name: str
    """Name of the check (e.g. ``'bond_lengths'``, ``'fmax'``)."""

    category: str
    """Category of the check (e.g. ``'structural'``, ``'convergence'``)."""

    passed: bool
    """``True`` if the check criterion was satisfied."""

    value: Any
    """Measured value from the check (``None`` if not applicable)."""

    threshold: Any
    """Threshold or acceptable range used in the check."""

    message: str
    """Human-readable message describing the check result."""
