"""Unit tests for cathodescope.config.defaults.

8 tests covering all default configuration constant values.
"""

from cathodescope.config.defaults import (
    DEFAULT_CACHE_DIR,
    DEFAULT_FMAX,
    DEFAULT_LATTICE_TOLERANCE,
    DEFAULT_MAX_BOND,
    DEFAULT_MAX_STEPS,
    DEFAULT_MIN_BOND,
    DEFAULT_REPORT_INDENT,
    DEFAULT_VOLUME_TOLERANCE,
)


def test_default_fmax_is_0_01() -> None:
    """Default fmax must be 0.01 eV/Å per task_board.md T-05 notes."""
    assert DEFAULT_FMAX == 0.01


def test_default_max_steps_is_500() -> None:
    """Default max_steps must be 500 per task_board.md T-05 notes."""
    assert DEFAULT_MAX_STEPS == 500


def test_default_lattice_tolerance_is_2_percent() -> None:
    """Default lattice_tolerance must be 2.0% per task_board.md T-05 notes."""
    assert DEFAULT_LATTICE_TOLERANCE == 2.0


def test_default_volume_tolerance_is_5_percent() -> None:
    """Default volume_tolerance must be 5.0% per task_board.md T-05 notes."""
    assert DEFAULT_VOLUME_TOLERANCE == 5.0


def test_default_min_bond_is_1_0() -> None:
    """Default min_bond must be 1.0 Å per task_board.md T-05 notes."""
    assert DEFAULT_MIN_BOND == 1.0


def test_default_max_bond_is_4_0() -> None:
    """Default max_bond must be 4.0 Å per task_board.md T-05 notes."""
    assert DEFAULT_MAX_BOND == 4.0


def test_default_report_indent_is_2() -> None:
    """Default JSON indent for reports must be 2."""
    assert DEFAULT_REPORT_INDENT == 2


def test_default_cache_dir_is_nonempty_string() -> None:
    """Default cache_dir must be a non-empty string."""
    assert isinstance(DEFAULT_CACHE_DIR, str)
    assert len(DEFAULT_CACHE_DIR) > 0
