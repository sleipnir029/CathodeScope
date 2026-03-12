"""Structure relaxer tool.

MACE-MP-0 based structure relaxation using ASE FIRE optimizer
and FrechetCellFilter for cell relaxation.
Accepts calculator via dependency injection.

Implemented in T-10. Integration testing in T-20.
"""

from typing import Any

import numpy as np
from ase.filters import FrechetCellFilter
from ase.optimize import FIRE
from pymatgen.core.structure import Structure
from pymatgen.io.ase import AseAtomsAdaptor

from cathodescope.config.settings import RelaxationConfig
from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ErrorRecord, ToolResult

_TOOL_VERSION = "0.1.0"

# Physical sanity limits applied to the relaxed structure.
_DIVERGENCE_DELTA = 500.0  # eV: energy increase beyond this signals divergence
_MAX_VOLUME_CHANGE_PCT = 50.0  # %: volume change beyond this is unphysical
_MIN_BOND_ANGSTROM = 0.5  # Å: interatomic distance below this signals collapse


def _build_provenance(
    mace_model_version: str,
    config: RelaxationConfig,
    relax_cell: bool,
) -> Any:
    """Build a ProvenanceRecord for the structure_relaxer tool."""
    return create_provenance(
        created_by="cathodescope",
        tool_name="structure_relaxer",
        tool_version=_TOOL_VERSION,
        notes=f"MACE-MP-0 model version: {mace_model_version}",
        config_snapshot={
            "fmax": config.fmax,
            "max_steps": config.max_steps,
            "relax_cell": relax_cell,
            "mace_model_version": mace_model_version,
        },
    )


def _failure_result(
    error_type: str,
    message: str,
    mace_model_version: str,
    config: RelaxationConfig,
    relax_cell: bool,
) -> ToolResult:
    """Return a failure ToolResult with the given error type and message."""
    return ToolResult(
        tool_name="structure_relaxer",
        status="failure",
        error=ErrorRecord(
            error_type=error_type,  # type: ignore[arg-type]
            message=message,
            source="structure_relaxer",
        ),
        provenance=_build_provenance(mace_model_version, config, relax_cell),
    )


def _get_min_interatomic_distance(structure: Structure) -> float:
    """Return the minimum pairwise interatomic distance (with PBC) in Ångströms.

    Uses a 4 Å neighbour cutoff, which comfortably captures all relevant bonds
    in cathode oxide materials (Li-O ~2.1 Å, TM-O ~1.9 Å).

    Args:
        structure: Pymatgen Structure to analyse.

    Returns:
        Minimum interatomic distance in Å, or ``float('inf')`` if no
        neighbours are found within 4 Å.
    """
    all_neighbors = structure.get_all_neighbors(r=4.0, include_index=False)
    min_dist = float("inf")
    for site_neighbors in all_neighbors:
        for nn in site_neighbors:
            if nn.nn_distance < min_dist:
                min_dist = nn.nn_distance
    return min_dist


def relax(
    structure: Structure,
    config: RelaxationConfig,
    calculator: Any,
    *,
    relax_cell: bool = True,
    mace_model_version: str = "unknown",
    _max_volume_change_pct: float = _MAX_VOLUME_CHANGE_PCT,
    _min_bond_angstrom: float = _MIN_BOND_ANGSTROM,
) -> ToolResult:
    """Relax a pymatgen Structure using an ASE FIRE optimizer.

    Accepts any ASE-compatible calculator via dependency injection so that
    unit tests can use a ``MockCalculator`` without loading MACE.  In
    production, pass a ``mace.calculators.MACECalculator`` instance.

    The function runs an ASE FIRE optimisation loop with optional
    :class:`~ase.filters.FrechetCellFilter` for simultaneous cell and
    position relaxation.  At each step, forces are inspected for NaN values
    and the total energy is monitored for runaway divergence.  After the run,
    the final structure is checked for unphysical volume change and atom–atom
    collapse.

    Args:
        structure: Input pymatgen Structure to relax.
        config: RelaxationConfig specifying ``fmax`` (eV/Å convergence
            criterion) and ``max_steps`` (maximum optimisation steps).
        calculator: An ASE-compatible calculator (must implement
            ``energy``, ``forces``, and ``stress`` properties).
        relax_cell: If ``True``, wrap atoms in
            :class:`~ase.filters.FrechetCellFilter` to allow simultaneous
            cell and position relaxation.  Default ``True``.
        mace_model_version: Version string of the MACE model used.  Recorded
            in the provenance ``config_snapshot``.  Default ``"unknown"``.
        _max_volume_change_pct: Maximum allowed volume change (%) relative to
            the input structure.  Relaxations exceeding this limit return a
            ``ValidationError``.  This parameter uses an underscore prefix to
            indicate it is primarily for testing — production code should use
            the default.
        _min_bond_angstrom: Minimum allowed interatomic distance (Å) in the
            relaxed structure.  Structures with any bond shorter than this
            return a ``ValidationError``.  This parameter uses an underscore
            prefix to indicate it is primarily for testing.

    Returns:
        A :class:`~cathodescope.models.results.ToolResult` with:

        - ``status='success'``: converged within ``max_steps``.
        - ``status='partial'``: ran to ``max_steps`` without convergence.
        - ``status='failure'``: NaN forces, energy divergence, excessive
          volume change, or structure collapse detected.

        ``data`` keys on success/partial:

        - ``structure``: relaxed pymatgen :class:`~pymatgen.core.structure.Structure`
          serialised as a dict.
        - ``final_energy`` (float): total energy at the last step in eV.
        - ``final_fmax`` (float): maximum force at the last step in eV/Å.
        - ``convergence_info`` (dict): ``converged`` (bool), ``steps`` (int),
          ``energy_history`` (list[float]), ``fmax_history`` (list[float]).
        - ``mace_model_version`` (str): passed-in model version string.

        ``evidence_type`` is ``'A-computed'`` for all non-failure results.
    """
    # --- Setup ---------------------------------------------------------------
    atoms = AseAtomsAdaptor.get_atoms(structure)
    atoms.calc = calculator
    initial_volume = atoms.get_volume()

    optim_target: Any = FrechetCellFilter(atoms) if relax_cell else atoms
    optimizer = FIRE(optim_target, logfile=None)

    energy_history: list[float] = []
    fmax_history: list[float] = []
    converged = False

    # --- Optimisation loop ---------------------------------------------------
    try:
        for is_converged in optimizer.irun(fmax=config.fmax, steps=config.max_steps):
            # Forces are cached from irun's get_gradient() call; re-reading
            # them here does NOT trigger a new calculator evaluation.
            f = optim_target.get_forces()

            # NaN forces: calculator produced invalid output.
            if np.any(np.isnan(f)):
                return _failure_result(
                    "ComputationError",
                    "NaN forces encountered during FIRE relaxation. "
                    "Check the calculator and input structure.",
                    mace_model_version,
                    config,
                    relax_cell,
                )

            e = float(atoms.get_potential_energy())
            fmax_val = float(np.sqrt((f**2).sum(axis=1).max()))

            # Divergence: energy climbed far above the initial value.
            if energy_history and e > energy_history[0] + _DIVERGENCE_DELTA:
                return _failure_result(
                    "ComputationError",
                    f"Energy diverged to {e:.2f} eV "
                    f"(initial: {energy_history[0]:.2f} eV, "
                    f"delta limit: {_DIVERGENCE_DELTA:.0f} eV). "
                    "Method: MACE-MP-0 FIRE optimizer.",
                    mace_model_version,
                    config,
                    relax_cell,
                )

            energy_history.append(e)
            fmax_history.append(fmax_val)
            converged = bool(is_converged)

            if is_converged:
                break

    except Exception as exc:  # noqa: BLE001
        return _failure_result(
            "ComputationError",
            f"Unexpected error during FIRE relaxation: {exc}",
            mace_model_version,
            config,
            relax_cell,
        )

    # --- Post-run validation -------------------------------------------------

    # Volume change check.
    final_volume = atoms.get_volume()
    volume_change_pct = abs(final_volume - initial_volume) / initial_volume * 100.0
    if volume_change_pct > _max_volume_change_pct:
        return _failure_result(
            "ValidationError",
            f"Excessive volume change: {volume_change_pct:.1f}% "
            f"(limit: {_max_volume_change_pct:.1f}%). "
            "The relaxed structure may be unphysical. "
            "Method: MACE-MP-0 FIRE optimizer with FrechetCellFilter.",
            mace_model_version,
            config,
            relax_cell,
        )

    # Structure collapse check.
    relaxed_obj = AseAtomsAdaptor.get_structure(atoms)
    relaxed: Structure = (
        relaxed_obj
        if isinstance(relaxed_obj, Structure)
        else Structure.from_dict(relaxed_obj.as_dict())
    )
    min_dist = _get_min_interatomic_distance(relaxed)
    if min_dist < _min_bond_angstrom:
        return _failure_result(
            "ValidationError",
            f"Structure collapse detected: minimum interatomic distance "
            f"{min_dist:.3f} Å < {_min_bond_angstrom:.3f} Å. "
            "The relaxed structure is unphysical. "
            "Method: MACE-MP-0 FIRE optimizer.",
            mace_model_version,
            config,
            relax_cell,
        )

    # --- Build result --------------------------------------------------------
    warnings: list[str] = []
    if not converged:
        final_fmax = fmax_history[-1] if fmax_history else float("nan")
        warnings.append(
            f"Structure did not converge within {config.max_steps} steps. "
            f"Final fmax: {final_fmax:.4f} eV/Å. "
            "Method: MACE-MP-0 FIRE optimizer."
        )

    return ToolResult(
        tool_name="structure_relaxer",
        status="success" if converged else "partial",
        data={
            "structure": relaxed.as_dict(),
            "final_energy": energy_history[-1] if energy_history else None,
            "final_fmax": fmax_history[-1] if fmax_history else None,
            "convergence_info": {
                "converged": converged,
                "steps": optimizer.nsteps,
                "energy_history": energy_history,
                "fmax_history": fmax_history,
            },
            "mace_model_version": mace_model_version,
        },
        evidence_type="A-computed",
        warnings=warnings,
        provenance=_build_provenance(mace_model_version, config, relax_cell),
    )
