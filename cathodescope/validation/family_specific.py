"""Family-specific validation checks (stubs for MVP).

Returns empty check lists for all families.
Expanded in Phase 4 for Jahn-Teller effects (LiMn2O4) and
polaron ordering (LiFePO4).

Implemented in T-12 (stubs).
"""

from typing import Any

from cathodescope.validation import CheckResult


def run_family_specific_checks(
    structure: dict[str, Any],
    family: str,
) -> list[CheckResult]:
    """Return family-specific validation checks for *family*.

    Args:
        structure: Serialised pymatgen Structure dict.
        family: Material family string (e.g. ``"layered_oxide"``,
            ``"spinel"``).

    Returns:
        Empty list for MVP.
        # EXPAND IN PHASE 4
    """
    _ = structure  # unused in MVP stub
    _ = family  # unused in MVP stub
    return []
