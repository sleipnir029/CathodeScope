"""Default configuration values for CathodeScope.

Provides named constants for all configurable parameters. These are the single
source of truth used by both the pydantic models (as field defaults) and tests.

All numeric defaults are from task_board.md T-05 notes:
- fmax=0.01 eV/Å, max_steps=500
- lattice_tolerance=2.0%, volume_tolerance=5.0%
- min_bond=1.0 Å, max_bond=4.0 Å
"""

# ---------------------------------------------------------------------------
# Relaxation defaults
# ---------------------------------------------------------------------------

DEFAULT_FMAX: float = 0.01
"""Force convergence criterion in eV/Å."""

DEFAULT_MAX_STEPS: int = 500
"""Maximum number of relaxation steps."""

DEFAULT_OPTIMIZER: str = "BFGS"
"""ASE optimizer class name."""

# ---------------------------------------------------------------------------
# Comparison defaults
# ---------------------------------------------------------------------------

DEFAULT_LATTICE_TOLERANCE: float = 2.0
"""Maximum allowed lattice parameter deviation from MP reference (%)."""

DEFAULT_VOLUME_TOLERANCE: float = 5.0
"""Maximum allowed unit-cell volume deviation from MP reference (%)."""

# ---------------------------------------------------------------------------
# Validation defaults
# ---------------------------------------------------------------------------

DEFAULT_MIN_BOND: float = 1.0
"""Minimum allowed interatomic distance in Å."""

DEFAULT_MAX_BOND: float = 4.0
"""Maximum allowed interatomic distance for bond detection in Å."""

# ---------------------------------------------------------------------------
# Report defaults
# ---------------------------------------------------------------------------

DEFAULT_REPORT_INDENT: int = 2
"""JSON indentation level for artifact files."""

# ---------------------------------------------------------------------------
# Cache defaults
# ---------------------------------------------------------------------------

DEFAULT_CACHE_DIR: str = "artifacts/cache/mp"
"""Directory path for MP API cache files, relative to project root."""

# ---------------------------------------------------------------------------
# Benchmark defaults (benchmark materials from master_plan.md)
# ---------------------------------------------------------------------------

DEFAULT_BENCHMARK_MATERIALS: tuple[str, ...] = (
    "mp-22526",  # LiCoO2 — R-3m layered oxide
    "mp-19017",  # LiFePO4 — Pnma olivine
    "mp-18767",  # LiMn2O4 — Fd-3m spinel
)
"""Materials Project IDs for the three benchmark cathode materials."""
