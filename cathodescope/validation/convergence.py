"""Convergence validation checks.

Implements fmax convergence, energy monotonicity, and step count checks.
Returns structured CheckResult dicts with check_name, category, passed,
value, threshold, message.

Implemented in T-12.
"""

from typing import Any

from cathodescope.validation import CheckResult

# ---------------------------------------------------------------------------
# Default thresholds
# ---------------------------------------------------------------------------

_DEFAULT_FMAX_THRESHOLD: float = 0.05   # eV/Å — lenient post-hoc check
_DEFAULT_ENERGY_TOLERANCE: float = 0.1  # eV  — max allowed single-step increase
_DEFAULT_WARN_PCT: float = 0.9          # fraction of max_steps that triggers warning
_DEFAULT_MAX_STEPS: int = 500


# ---------------------------------------------------------------------------
# Public check functions
# ---------------------------------------------------------------------------


def check_fmax(
    fmax: float,
    threshold: float = _DEFAULT_FMAX_THRESHOLD,
) -> CheckResult:
    """Check that the final maximum force component is at or below *threshold*.

    Args:
        fmax: Final maximum force in eV/Å from the relaxation run.
        threshold: Convergence threshold in eV/Å.

    Returns:
        A ``CheckResult`` dict.  ``passed=True`` when ``fmax <= threshold``.
    """
    passed = fmax <= threshold
    return CheckResult(
        check_name="fmax",
        category="convergence",
        passed=passed,
        value=round(fmax, 6),
        threshold=threshold,
        message=(
            f"Final fmax {fmax:.6f} eV/Å is "
            f"{'within' if passed else 'above'} the convergence threshold "
            f"of {threshold} eV/Å."
        ),
    )


def check_energy_monotonicity(
    energy_history: list[float],
    tolerance: float = _DEFAULT_ENERGY_TOLERANCE,
) -> CheckResult:
    """Check that the energy does not increase by more than *tolerance* between steps.

    A well-behaved relaxation should have monotonically decreasing energy.
    Small oscillations up to *tolerance* eV are permitted to accommodate
    line-search artefacts.

    Args:
        energy_history: List of total energies (eV) recorded at each step.
        tolerance: Maximum allowed single-step energy increase in eV.

    Returns:
        A ``CheckResult`` dict.  ``passed=True`` when all step-to-step energy
        increases are within *tolerance*.  Returns ``passed=True`` with an
        informational message if fewer than 2 data points are available.
    """
    if len(energy_history) < 2:
        return CheckResult(
            check_name="energy_monotonicity",
            category="convergence",
            passed=True,
            value=None,
            threshold=tolerance,
            message=(
                "Insufficient energy history to check monotonicity "
                "(fewer than 2 steps)."
            ),
        )

    max_increase = max(b - a for a, b in zip(energy_history[:-1], energy_history[1:]))
    passed = max_increase <= tolerance

    return CheckResult(
        check_name="energy_monotonicity",
        category="convergence",
        passed=passed,
        value=round(max_increase, 6),
        threshold=tolerance,
        message=(
            f"Maximum energy increase between steps: {max_increase:.6f} eV. "
            f"{'Within' if passed else 'Exceeds'} monotonicity tolerance "
            f"of {tolerance} eV."
        ),
    )


def check_step_count(
    steps: int,
    max_steps: int,
    warn_pct: float = _DEFAULT_WARN_PCT,
) -> CheckResult:
    """Check that the step count did not reach the maximum allowed.

    Args:
        steps: Number of optimisation steps taken.
        max_steps: Maximum allowed steps (from RelaxationConfig).
        warn_pct: Fraction of *max_steps* at which a near-limit warning is
            emitted (default 0.9).

    Returns:
        A ``CheckResult`` dict.  ``passed=False`` when ``steps >= max_steps``
        (relaxation hit the step limit and may not be converged).
    """
    passed = steps < max_steps
    ratio = steps / max_steps if max_steps > 0 else 1.0

    if not passed:
        message = (
            f"Step count {steps} reached the maximum limit of {max_steps}. "
            "Relaxation may not have converged."
        )
    elif ratio >= warn_pct:
        message = (
            f"Step count {steps} is near the maximum limit of {max_steps} "
            f"({100 * ratio:.0f}%). Consider increasing max_steps."
        )
    else:
        message = (
            f"Step count {steps} is well within the maximum limit of {max_steps}."
        )

    return CheckResult(
        check_name="step_count",
        category="convergence",
        passed=passed,
        value=steps,
        threshold={"max_steps": max_steps, "warn_pct": warn_pct},
        message=message,
    )


def run_convergence_checks(
    convergence_info: dict[str, Any],
    max_steps: int = _DEFAULT_MAX_STEPS,
    fmax_threshold: float = _DEFAULT_FMAX_THRESHOLD,
    energy_tolerance: float = _DEFAULT_ENERGY_TOLERANCE,
    warn_pct: float = _DEFAULT_WARN_PCT,
) -> list[CheckResult]:
    """Run all convergence checks on a convergence_info dict.

    Expects the ``convergence_info`` dict produced by
    ``cathodescope.tools.structure_relaxer.relax()``:
    ``{"converged": bool, "steps": int, "energy_history": list[float],
    "fmax_history": list[float]}``.

    Args:
        convergence_info: Dict with relaxation trajectory data.
        max_steps: Maximum allowed steps used in the relaxation run.
        fmax_threshold: Convergence threshold for the fmax check in eV/Å.
        energy_tolerance: Maximum allowed single-step energy increase in eV.
        warn_pct: Fraction of *max_steps* at which a near-limit warning fires.

    Returns:
        List of ``CheckResult`` dicts (fmax, energy_monotonicity, step_count).
        The fmax check is omitted if ``fmax_history`` is empty.
    """
    results: list[CheckResult] = []

    fmax_history: list[float] = convergence_info.get("fmax_history", [])
    if fmax_history:
        results.append(check_fmax(fmax_history[-1], threshold=fmax_threshold))

    energy_history: list[float] = convergence_info.get("energy_history", [])
    results.append(
        check_energy_monotonicity(energy_history, tolerance=energy_tolerance)
    )

    steps: int = convergence_info.get("steps", 0)
    results.append(check_step_count(steps, max_steps, warn_pct=warn_pct))

    return results
