"""Structural validation checks.

Implements bond length, atom overlap, and coordination number checks.
Returns structured CheckResult dicts with check_name, category, passed,
value, threshold, message.

Implemented in T-12.
"""

from typing import Any

from pymatgen.core.structure import Structure

from cathodescope.validation import CheckResult

# ---------------------------------------------------------------------------
# Default thresholds (copied from config.defaults to avoid config/* import)
# ---------------------------------------------------------------------------

_DEFAULT_MIN_BOND: float = 1.0  # Å — matches config.defaults.DEFAULT_MIN_BOND
_DEFAULT_MAX_BOND: float = 4.0  # Å — matches config.defaults.DEFAULT_MAX_BOND
_DEFAULT_OVERLAP: float = 0.5  # Å — strict atom-overlap threshold


def _parse_structure(structure: dict[str, Any]) -> Structure:
    """Return a pymatgen Structure from a serialised dict."""
    return Structure.from_dict(structure)


def _min_neighbour_distance(structure: Structure, cutoff: float) -> float:
    """Return the minimum pairwise interatomic distance within *cutoff* Å.

    Returns ``float('inf')`` if no neighbour pairs are found.
    """
    all_neighbors = structure.get_all_neighbors(r=cutoff, include_index=False)
    min_dist = float("inf")
    for site_neighbors in all_neighbors:
        for nn in site_neighbors:
            if nn.nn_distance < min_dist:
                min_dist = nn.nn_distance
    return min_dist


# ---------------------------------------------------------------------------
# Public check functions
# ---------------------------------------------------------------------------


def check_bond_lengths(
    structure: dict[str, Any],
    min_bond: float = _DEFAULT_MIN_BOND,
    max_bond: float = _DEFAULT_MAX_BOND,
) -> CheckResult:
    """Check that the minimum interatomic distance is within [min_bond, max_bond].

    Args:
        structure: Serialised pymatgen Structure dict.
        min_bond: Minimum allowed interatomic distance in Å.
        max_bond: Maximum cutoff for neighbour search in Å.  If no neighbour is
            found within this radius the structure is considered unphysically
            sparse ("exploded").

    Returns:
        A ``CheckResult`` dict.  ``passed=False`` if the minimum distance is
        below *min_bond* (collapsed) or if no neighbour is found within *max_bond*
        (exploded).
    """
    s = _parse_structure(structure)
    min_dist = _min_neighbour_distance(s, cutoff=max_bond)
    threshold = {"min_bond": min_bond, "max_bond": max_bond}

    if min_dist == float("inf"):
        return CheckResult(
            check_name="bond_lengths",
            category="structural",
            passed=False,
            value=None,
            threshold=threshold,
            message=(
                f"No interatomic bonds found within {max_bond} Å cutoff. "
                "Structure may be unphysically sparse or exploded."
            ),
        )

    if min_dist < min_bond:
        return CheckResult(
            check_name="bond_lengths",
            category="structural",
            passed=False,
            value=round(min_dist, 4),
            threshold=threshold,
            message=(
                f"Minimum bond length {min_dist:.4f} Å is below the minimum "
                f"threshold of {min_bond} Å. Structure may be collapsed."
            ),
        )

    return CheckResult(
        check_name="bond_lengths",
        category="structural",
        passed=True,
        value=round(min_dist, 4),
        threshold=threshold,
        message=(
            f"Minimum bond length {min_dist:.4f} Å is within the acceptable "
            f"range [{min_bond}, {max_bond}] Å."
        ),
    )


def check_atom_overlap(
    structure: dict[str, Any],
    overlap_threshold: float = _DEFAULT_OVERLAP,
) -> CheckResult:
    """Check for atom-atom overlap closer than *overlap_threshold* Å.

    Args:
        structure: Serialised pymatgen Structure dict.
        overlap_threshold: Distance threshold in Å below which two atoms are
            considered to overlap.

    Returns:
        A ``CheckResult`` dict.  ``passed=False`` if any atom pair is closer
        than *overlap_threshold*.
    """
    s = _parse_structure(structure)
    min_dist = _min_neighbour_distance(s, cutoff=overlap_threshold)

    if min_dist < overlap_threshold:
        return CheckResult(
            check_name="atom_overlap",
            category="structural",
            passed=False,
            value=round(min_dist, 4),
            threshold=overlap_threshold,
            message=(
                f"Atom overlap detected: minimum interatomic distance {min_dist:.4f} Å "
                f"is below the overlap threshold of {overlap_threshold} Å."
            ),
        )

    return CheckResult(
        check_name="atom_overlap",
        category="structural",
        passed=True,
        value=None,
        threshold=overlap_threshold,
        message=f"No atom overlap detected within {overlap_threshold} Å threshold.",
    )


def check_coordination_numbers(
    structure: dict[str, Any],
    cutoff: float = _DEFAULT_MAX_BOND,
) -> CheckResult:
    """Return average coordination numbers per element type.

    This check is always informational (``passed=True``).  It reports the
    average number of neighbours each element type has within *cutoff* Å.

    Args:
        structure: Serialised pymatgen Structure dict.
        cutoff: Neighbour search cutoff in Å.

    Returns:
        A ``CheckResult`` dict with ``value`` set to a ``dict[str, float]``
        mapping element symbol to average coordination number.
    """
    s = _parse_structure(structure)
    all_neighbors = s.get_all_neighbors(r=cutoff, include_index=False)

    element_counts: dict[str, list[int]] = {}
    for site, site_neighbors in zip(s.sites, all_neighbors):
        elem = str(site.specie)
        if elem not in element_counts:
            element_counts[elem] = []
        element_counts[elem].append(len(site_neighbors))

    avg_by_element = {
        elem: round(sum(counts) / len(counts), 2)
        for elem, counts in element_counts.items()
    }

    return CheckResult(
        check_name="coordination_numbers",
        category="structural",
        passed=True,
        value=avg_by_element,
        threshold=cutoff,
        message=(
            f"Average coordination numbers (cutoff {cutoff} Å): {avg_by_element}."
        ),
    )


def run_structural_checks(
    structure: dict[str, Any],
    min_bond: float = _DEFAULT_MIN_BOND,
    max_bond: float = _DEFAULT_MAX_BOND,
) -> list[CheckResult]:
    """Run all structural checks and return a list of CheckResult dicts.

    Runs bond-length, atom-overlap, and coordination-number checks.

    Args:
        structure: Serialised pymatgen Structure dict.
        min_bond: Minimum allowed interatomic distance in Å.
        max_bond: Maximum cutoff for bond detection in Å.

    Returns:
        Ordered list of ``CheckResult`` dicts (bond_lengths, atom_overlap,
        coordination_numbers).
    """
    return [
        check_bond_lengths(structure, min_bond=min_bond, max_bond=max_bond),
        check_atom_overlap(structure),
        check_coordination_numbers(structure, cutoff=max_bond),
    ]
