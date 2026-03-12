"""Unit tests for cathodescope.validation.convergence.

8 convergence check tests: fmax (2), energy monotonicity (3),
step count (2), run_convergence_checks (1).
"""

from cathodescope.validation.convergence import (
    check_energy_monotonicity,
    check_fmax,
    check_step_count,
    run_convergence_checks,
)

_CHECK_KEYS = {"check_name", "category", "passed", "value", "threshold", "message"}

# ---------------------------------------------------------------------------
# Test 1: fmax below threshold passes
# ---------------------------------------------------------------------------


def test_fmax_check_passes_when_below_threshold() -> None:
    result = check_fmax(0.005, threshold=0.05)

    assert result["check_name"] == "fmax"
    assert result["category"] == "convergence"
    assert result["passed"] is True
    assert result["value"] == 0.005


# ---------------------------------------------------------------------------
# Test 2: fmax above threshold fails
# ---------------------------------------------------------------------------


def test_fmax_check_fails_when_above_threshold() -> None:
    result = check_fmax(0.1, threshold=0.05)

    assert result["passed"] is False
    assert result["value"] == 0.1
    assert "above" in result["message"].lower()


# ---------------------------------------------------------------------------
# Test 3: Strictly decreasing energy passes monotonicity check
# ---------------------------------------------------------------------------


def test_energy_monotonicity_passes_decreasing_energy() -> None:
    energy_history = [-10.0, -10.5, -11.0, -11.2]
    result = check_energy_monotonicity(energy_history, tolerance=0.1)

    assert result["check_name"] == "energy_monotonicity"
    assert result["passed"] is True
    # Max increase is 0 (strictly decreasing) → value ≤ 0 ≤ tolerance
    assert float(result["value"]) <= 0.0


# ---------------------------------------------------------------------------
# Test 4: Oscillating energy fails monotonicity check
# ---------------------------------------------------------------------------


def test_energy_monotonicity_fails_oscillating_energy() -> None:
    # Step from -10 to -9 is an increase of 1.0 eV, exceeding tolerance=0.1
    energy_history = [-10.0, -9.0, -11.0]
    result = check_energy_monotonicity(energy_history, tolerance=0.1)

    assert result["passed"] is False
    assert float(result["value"]) > 0.1
    assert "exceeds" in result["message"].lower()


# ---------------------------------------------------------------------------
# Test 5: Monotonicity tolerance is configurable
# ---------------------------------------------------------------------------


def test_energy_monotonicity_tolerance_is_configurable() -> None:
    # Max increase = 0.05 eV (just below 0.1, but above 0.01)
    energy_history = [-10.0, -9.95, -11.0]

    loose = check_energy_monotonicity(energy_history, tolerance=0.1)
    assert loose["passed"] is True  # 0.05 ≤ 0.1

    strict = check_energy_monotonicity(energy_history, tolerance=0.01)
    assert strict["passed"] is False  # 0.05 > 0.01


# ---------------------------------------------------------------------------
# Test 6: Step count well within limit passes
# ---------------------------------------------------------------------------


def test_step_count_check_passes_within_limit() -> None:
    result = check_step_count(steps=100, max_steps=500)

    assert result["check_name"] == "step_count"
    assert result["category"] == "convergence"
    assert result["passed"] is True
    assert result["value"] == 100


# ---------------------------------------------------------------------------
# Test 7: Step count near limit produces a warning message
# ---------------------------------------------------------------------------


def test_step_count_check_warns_near_limit() -> None:
    # 460 / 500 = 0.92 > warn_pct=0.9 → warning, but still passed
    result = check_step_count(steps=460, max_steps=500, warn_pct=0.9)

    assert result["passed"] is True
    msg = result["message"].lower()
    assert "near" in msg or "consider" in msg


# ---------------------------------------------------------------------------
# Test 8: run_convergence_checks returns a list of CheckResult dicts
# ---------------------------------------------------------------------------


def test_convergence_checks_return_check_result_list() -> None:
    convergence_info = {
        "converged": True,
        "steps": 100,
        "energy_history": [-10.0, -10.5, -11.0],
        "fmax_history": [0.1, 0.05, 0.008],
    }
    results = run_convergence_checks(convergence_info, max_steps=500)

    assert isinstance(results, list)
    assert len(results) >= 1
    for result in results:
        assert _CHECK_KEYS.issubset(
            result.keys()
        ), f"Missing keys: {_CHECK_KEYS - result.keys()}"
        assert isinstance(result["check_name"], str)
        assert isinstance(result["category"], str)
        assert isinstance(result["passed"], bool)
        assert isinstance(result["message"], str)
