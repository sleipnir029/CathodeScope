"""Reference comparator tool.

Computes quantitative deviations between relaxed and MP reference structures:
lattice parameter deviations, angle deviations, volume deviation, symmetry
preservation.

All deviations use the formula: ``|relaxed - reference| / reference * 100`` (%).
The word "deviation" is used throughout, never "error".

Implemented in T-11.
"""

from typing import Any

from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from cathodescope.config.settings import ComparisonConfig
from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ErrorRecord, ToolResult

_TOOL_VERSION = "0.1.0"


def compare(
    relaxed: Structure,
    reference: Structure,
    config: ComparisonConfig | None = None,
) -> ToolResult:
    """Compare a relaxed structure against a Materials Project reference structure.

    Computes lattice parameter deviations (a, b, c), angle deviations
    (alpha, beta, gamma), volume deviation, and symmetry preservation.
    All deviations use the formula: ``|relaxed - reference| / reference * 100``.

    Evidence type is ``'A-compared'`` per the scientific validity matrix —
    direct comparison against authoritative MP reference data (PBE+U).

    Args:
        relaxed: Pymatgen Structure produced by MACE-MP-0 relaxation.
        reference: Pymatgen Structure from the Materials Project (the reference).
        config: Optional ComparisonConfig with tolerance thresholds.
            Defaults to ``ComparisonConfig()`` (lattice 2%, volume 5%).

    Returns:
        A ToolResult with ``status='success'`` containing:

        - ``lattice_deviations``: dict with keys ``a``, ``b``, ``c`` (% deviation)
        - ``angle_deviations``: dict with keys ``alpha``, ``beta``, ``gamma``
          (% deviation)
        - ``volume_deviation``: float (% deviation)
        - ``symmetry_preserved``: bool — True if space group symbols match
        - ``reference_space_group``: space group symbol of the reference
        - ``relaxed_space_group``: space group symbol of the relaxed structure
        - ``within_lattice_tolerance``: bool — True if max(a,b,c) deviation ≤ tolerance
        - ``within_volume_tolerance``: bool — True if volume deviation ≤ tolerance

        Returns ``status='failure'`` with ``InputError`` if compositions do not match.
    """
    if config is None:
        config = ComparisonConfig()

    prov = create_provenance(
        created_by="cathodescope",
        tool_name="reference_comparator",
        tool_version=_TOOL_VERSION,
        config_snapshot={
            "lattice_tolerance": config.lattice_tolerance,
            "volume_tolerance": config.volume_tolerance,
        },
    )

    # --- Composition guard ---------------------------------------------------
    if (
        relaxed.composition.reduced_composition
        != reference.composition.reduced_composition
    ):
        return ToolResult(
            tool_name="reference_comparator",
            status="failure",
            error=ErrorRecord(
                error_type="InputError",
                message=(
                    f"Composition mismatch: relaxed has "
                    f"'{relaxed.composition.reduced_formula}', "
                    f"reference has '{reference.composition.reduced_formula}'. "
                    "Both structures must share the same reduced composition."
                ),
                source="reference_comparator",
            ),
            provenance=prov,
        )

    # --- Lattice parameter deviations (%) -----------------------------------
    rl = relaxed.lattice
    ref_l = reference.lattice

    lattice_deviations: dict[str, float] = {
        "a": abs(rl.a - ref_l.a) / ref_l.a * 100,
        "b": abs(rl.b - ref_l.b) / ref_l.b * 100,
        "c": abs(rl.c - ref_l.c) / ref_l.c * 100,
    }

    # --- Angle deviations (%) -----------------------------------------------
    angle_deviations: dict[str, float] = {
        "alpha": abs(rl.alpha - ref_l.alpha) / ref_l.alpha * 100,
        "beta": abs(rl.beta - ref_l.beta) / ref_l.beta * 100,
        "gamma": abs(rl.gamma - ref_l.gamma) / ref_l.gamma * 100,
    }

    # --- Volume deviation (%) -----------------------------------------------
    volume_deviation: float = abs(rl.volume - ref_l.volume) / ref_l.volume * 100

    # --- Symmetry comparison ------------------------------------------------
    relaxed_sg: str = SpacegroupAnalyzer(relaxed).get_space_group_symbol()
    reference_sg: str = SpacegroupAnalyzer(reference).get_space_group_symbol()
    symmetry_preserved: bool = relaxed_sg == reference_sg

    # --- Tolerance flags ----------------------------------------------------
    max_lattice_dev = max(lattice_deviations.values())
    within_lattice_tolerance: bool = max_lattice_dev <= config.lattice_tolerance
    within_volume_tolerance: bool = volume_deviation <= config.volume_tolerance

    data: dict[str, Any] = {
        "lattice_deviations": lattice_deviations,
        "angle_deviations": angle_deviations,
        "volume_deviation": volume_deviation,
        "symmetry_preserved": symmetry_preserved,
        "reference_space_group": reference_sg,
        "relaxed_space_group": relaxed_sg,
        "within_lattice_tolerance": within_lattice_tolerance,
        "within_volume_tolerance": within_volume_tolerance,
    }

    return ToolResult(
        tool_name="reference_comparator",
        status="success",
        data=data,
        evidence_type="A-compared",
        provenance=prov,
    )
