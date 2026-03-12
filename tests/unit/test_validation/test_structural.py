"""Unit tests for cathodescope.validation.structural.

8 structural check tests: bond lengths (5), atom overlap (1),
coordination (1), run_structural_checks (1).
"""

import pytest
from pymatgen.core import Lattice, Structure

from cathodescope.validation.structural import (
    check_atom_overlap,
    check_bond_lengths,
    check_coordination_numbers,
    run_structural_checks,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CHECK_KEYS = {"check_name", "category", "passed", "value", "threshold", "message"}


def _bcc_li_dict(a: float) -> dict:
    """BCC Li structure with lattice parameter *a* Å, serialised as dict."""
    lattice = Lattice.cubic(a)
    s = Structure(lattice, ["Li", "Li"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    return s.as_dict()


def _single_li_dict(a: float) -> dict:
    """Single Li atom in a cubic cell of side *a* Å."""
    lattice = Lattice.cubic(a)
    s = Structure(lattice, ["Li"], [[0, 0, 0]])
    return s.as_dict()


# BCC nearest-neighbour distance: a * sqrt(3) / 2
# a=3.5 Å  → ~3.03 Å  (normal, between 1.0 and 4.0)
# a=0.8 Å  → ~0.69 Å  (collapsed, < 1.0 Å default min_bond)
# a=0.3 Å  → ~0.26 Å  (overlap, < 0.5 Å overlap_threshold)
# Single Li in 10 Å cell → nearest image at 10 Å (exploded, > 4.0 Å default max_bond)
# Single Li in  5 Å cell → nearest image at  5 Å (> 4.0 but < 6.0 for configurable test)


# ---------------------------------------------------------------------------
# Test 1: Normal structure passes bond-length check
# ---------------------------------------------------------------------------


def test_bond_length_check_passes_normal_structure() -> None:
    result = check_bond_lengths(_bcc_li_dict(3.5))

    assert result["check_name"] == "bond_lengths"
    assert result["category"] == "structural"
    assert result["passed"] is True
    assert result["value"] is not None
    assert float(result["value"]) > 1.0


# ---------------------------------------------------------------------------
# Test 2: Collapsed structure fails bond-length check
# ---------------------------------------------------------------------------


def test_bond_length_check_fails_collapsed_structure() -> None:
    # BCC Li with a=0.8 Å → nearest-neighbour ≈ 0.69 Å < 1.0 Å (default min_bond)
    result = check_bond_lengths(_bcc_li_dict(0.8))

    assert result["passed"] is False
    assert result["value"] is not None
    assert float(result["value"]) < 1.0
    msg = result["message"].lower()
    assert "collapsed" in msg or "below" in msg


# ---------------------------------------------------------------------------
# Test 3: Exploded structure fails bond-length check
# ---------------------------------------------------------------------------


def test_bond_length_check_fails_exploded_structure() -> None:
    # Single Li in a 10 Å cubic cell → nearest image at 10 Å > 4.0 Å (default max_bond)
    result = check_bond_lengths(_single_li_dict(10.0))

    assert result["passed"] is False
    assert result["value"] is None  # no bond found
    assert "exploded" in result["message"].lower() or "no" in result["message"].lower()


# ---------------------------------------------------------------------------
# Test 4: Minimum bond-length threshold is configurable
# ---------------------------------------------------------------------------


def test_min_bond_length_threshold_is_configurable() -> None:
    # BCC Li a=0.8 Å → nearest-neighbour ≈ 0.69 Å
    # Default min_bond=1.0 → fails; custom min_bond=0.5 → passes (0.69 > 0.5)
    structure = _bcc_li_dict(0.8)

    default_result = check_bond_lengths(structure)
    assert default_result["passed"] is False

    custom_result = check_bond_lengths(structure, min_bond=0.5)
    assert custom_result["passed"] is True


# ---------------------------------------------------------------------------
# Test 5: Maximum bond-length threshold is configurable
# ---------------------------------------------------------------------------


def test_max_bond_length_threshold_is_configurable() -> None:
    # Single Li in 5 Å cell → nearest image at 5 Å
    # Default max_bond=4.0 → no neighbour found → fails
    # Custom max_bond=6.0 → neighbour at 5 Å found, 5 Å > min_bond=1.0 → passes
    structure = _single_li_dict(5.0)

    default_result = check_bond_lengths(structure)
    assert default_result["passed"] is False

    custom_result = check_bond_lengths(structure, max_bond=6.0)
    assert custom_result["passed"] is True


# ---------------------------------------------------------------------------
# Test 6: Atom-overlap check detects overlapping atoms
# ---------------------------------------------------------------------------


def test_atom_overlap_check_detects_overlapping_atoms() -> None:
    # BCC Li with a=0.3 Å → nearest-neighbour ≈ 0.26 Å < 0.5 Å overlap_threshold
    result = check_atom_overlap(_bcc_li_dict(0.3))

    assert result["check_name"] == "atom_overlap"
    assert result["passed"] is False
    assert float(result["value"]) < 0.5
    assert "overlap" in result["message"].lower()


# ---------------------------------------------------------------------------
# Test 7: Coordination check returns coordination numbers
# ---------------------------------------------------------------------------


def test_coordination_check_returns_coordination_numbers() -> None:
    # BCC Li with a=3.5 Å: 8 nearest neighbours per site within 4 Å
    result = check_coordination_numbers(_bcc_li_dict(3.5))

    assert result["check_name"] == "coordination_numbers"
    assert result["passed"] is True  # always informational
    assert isinstance(result["value"], dict)
    assert "Li" in result["value"]
    # BCC has 8 nearest (a*√3/2 ≈ 3.03 Å) + 6 next-nearest (a = 3.5 Å) = 14 within 4 Å
    assert result["value"]["Li"] == pytest.approx(14.0)


# ---------------------------------------------------------------------------
# Test 8: run_structural_checks returns a list of CheckResult dicts
# ---------------------------------------------------------------------------


def test_structural_checks_return_check_result_list() -> None:
    structure = _bcc_li_dict(3.5)
    results = run_structural_checks(structure)

    assert isinstance(results, list)
    assert len(results) >= 1
    for result in results:
        assert _CHECK_KEYS.issubset(
            result.keys()
        ), f"Missing keys in check result: {_CHECK_KEYS - result.keys()}"
        assert isinstance(result["check_name"], str)
        assert isinstance(result["category"], str)
        assert isinstance(result["passed"], bool)
        assert isinstance(result["message"], str)
