"""Unit tests for cathodescope.tools.structure_relaxer.

19 tests using dependency-injected mock calculators.
Implemented in T-10. Real MACE integration is T-20.
"""

import json
from pathlib import Path
from typing import Any

import numpy as np
from ase.calculators.calculator import Calculator

from cathodescope.config.settings import RelaxationConfig
from cathodescope.models.results import ToolResult
from cathodescope.tools.structure_relaxer import relax

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

_FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "mp_responses"


def _load_structure() -> dict[str, Any]:
    """Load LiCoO2 structure dict from fixture."""
    data: dict[str, Any] = json.loads(
        (_FIXTURE_DIR / "mp-22526.json").read_text(encoding="utf-8")
    )
    return data["structure"]  # type: ignore[return-value]


def _make_licoo2_structure() -> Any:
    """Return a pymatgen Structure for LiCoO2 (conventional cell)."""
    from pymatgen.core.structure import Structure
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    s = Structure.from_dict(_load_structure())
    return SpacegroupAnalyzer(s).get_conventional_standard_structure()


def _make_config(fmax: float = 0.01, max_steps: int = 500) -> RelaxationConfig:
    """Return a RelaxationConfig with optional overrides."""
    return RelaxationConfig(fmax=fmax, max_steps=max_steps)


# ---------------------------------------------------------------------------
# Mock calculators
# ---------------------------------------------------------------------------


class _ConvergingCalc(Calculator):
    """Calculator that returns zero forces → immediately converged."""

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self) -> None:
        super().__init__()
        self.use_cache = True  # enable ASE result caching

    def calculate(
        self, atoms: Any, properties: list[str], system_changes: list[str]
    ) -> None:
        """Return zero forces so any fmax threshold is immediately met."""
        n = len(atoms)
        self.results = {
            "energy": -10.0,
            "forces": np.zeros((n, 3)),
            "stress": np.zeros(6),
        }


class _NonConvergingCalc(Calculator):
    """Calculator that always returns forces above any reasonable fmax."""

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self) -> None:
        super().__init__()
        self.use_cache = True

    def calculate(
        self, atoms: Any, properties: list[str], system_changes: list[str]
    ) -> None:
        """Return constant large forces so the optimizer never converges."""
        n = len(atoms)
        forces = np.zeros((n, 3))
        forces[0, 0] = 1.0  # fmax = 1.0 eV/Å, always above threshold
        self.results = {
            "energy": -10.0,
            "forces": forces,
            "stress": np.zeros(6),
        }


class _NaNForcesCalc(Calculator):
    """Calculator that returns NaN forces."""

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self) -> None:
        super().__init__()
        self.use_cache = True

    def calculate(
        self, atoms: Any, properties: list[str], system_changes: list[str]
    ) -> None:
        """Return NaN forces to simulate a broken calculator."""
        n = len(atoms)
        self.results = {
            "energy": float("nan"),
            "forces": np.full((n, 3), float("nan")),
            "stress": np.zeros(6),
        }


class _DivergingCalc(Calculator):
    """Calculator that returns enormous energy after the first step."""

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self) -> None:
        super().__init__()
        self.use_cache = True
        self._n = 0  # call counter (cached, so counts unique configs)

    def calculate(
        self, atoms: Any, properties: list[str], system_changes: list[str]
    ) -> None:
        """First call returns normal energy; subsequent calls return 1e10 eV."""
        n = len(atoms)
        energy = -10.0 if self._n == 0 else 1e10
        self._n += 1
        forces = np.zeros((n, 3))
        forces[0, 0] = 0.1  # non-zero force triggers at least one optimizer step
        self.results = {
            "energy": energy,
            "forces": forces,
            "stress": np.zeros(6),
        }


class _BigStressCalc(Calculator):
    """Calculator with huge cell stress (forces atoms to zero, cell expands)."""

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self) -> None:
        super().__init__()
        self.use_cache = True

    def calculate(
        self, atoms: Any, properties: list[str], system_changes: list[str]
    ) -> None:
        """Zero atomic forces but huge cell stress → cell expands under optimizer."""
        n = len(atoms)
        self.results = {
            "energy": -10.0,
            "forces": np.zeros((n, 3)),
            "stress": np.ones(6) * 1e3,  # large isotropic stress
        }


class _FixedFmaxCalc(Calculator):
    """Calculator that returns a fixed fmax value regardless of positions."""

    implemented_properties = ["energy", "forces", "stress"]

    def __init__(self, fmax_value: float) -> None:
        super().__init__()
        self.use_cache = True
        self._fmax_value = fmax_value

    def calculate(
        self, atoms: Any, properties: list[str], system_changes: list[str]
    ) -> None:
        """Return forces such that fmax == self._fmax_value."""
        n = len(atoms)
        forces = np.zeros((n, 3))
        forces[0, 0] = self._fmax_value
        self.results = {
            "energy": -10.0,
            "forces": forces,
            "stress": np.zeros(6),
        }


# ---------------------------------------------------------------------------
# Tests 1–5: Return type and data field presence
# ---------------------------------------------------------------------------


def test_relax_returns_tool_result() -> None:
    """relax() returns a ToolResult instance."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert isinstance(result, ToolResult)


def test_relax_evidence_type_is_a_computed() -> None:
    """Successful relaxation carries evidence_type='A-computed'."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.evidence_type == "A-computed"


def test_relax_data_contains_relaxed_structure() -> None:
    """result.data contains a 'structure' key."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    assert "structure" in result.data


def test_relax_data_contains_final_energy() -> None:
    """result.data contains a 'final_energy' key."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    assert "final_energy" in result.data


def test_relax_data_contains_final_fmax() -> None:
    """result.data contains a 'final_fmax' key."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    assert "final_fmax" in result.data


# ---------------------------------------------------------------------------
# Tests 6–10: convergence_info sub-dict structure
# ---------------------------------------------------------------------------


def test_relax_data_contains_convergence_info() -> None:
    """result.data contains a 'convergence_info' key."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    assert "convergence_info" in result.data


def test_relax_convergence_info_has_converged_flag() -> None:
    """convergence_info['converged'] is a bool."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    ci = result.data["convergence_info"]
    assert isinstance(ci["converged"], bool)


def test_relax_convergence_info_has_steps_count() -> None:
    """convergence_info['steps'] is an int."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    ci = result.data["convergence_info"]
    assert isinstance(ci["steps"], int)


def test_relax_convergence_info_has_energy_history() -> None:
    """convergence_info['energy_history'] is a list of floats."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    ci = result.data["convergence_info"]
    assert isinstance(ci["energy_history"], list)
    assert len(ci["energy_history"]) >= 1


def test_relax_convergence_info_has_fmax_history() -> None:
    """convergence_info['fmax_history'] is a list of floats."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(structure, config, _ConvergingCalc())
    assert result.data is not None
    ci = result.data["convergence_info"]
    assert isinstance(ci["fmax_history"], list)
    assert len(ci["fmax_history"]) >= 1


# ---------------------------------------------------------------------------
# Tests 11–15: Error paths
# ---------------------------------------------------------------------------


def test_relax_non_convergence_returns_warning_status() -> None:
    """Non-convergence produces status='partial' with at least one warning."""
    structure = _make_licoo2_structure()
    config = _make_config(fmax=0.01, max_steps=3)
    result = relax(structure, config, _NonConvergingCalc(), relax_cell=False)
    assert result.status == "partial"
    assert len(result.warnings) >= 1


def test_relax_divergence_raises_computation_error() -> None:
    """Diverging energy produces status='failure' with ComputationError."""
    structure = _make_licoo2_structure()
    config = _make_config(fmax=0.01, max_steps=10)
    result = relax(structure, config, _DivergingCalc(), relax_cell=False)
    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "ComputationError"
    assert result.error.source == "structure_relaxer"


def test_relax_nan_forces_raises_computation_error() -> None:
    """NaN forces produce status='failure' with ComputationError."""
    structure = _make_licoo2_structure()
    config = _make_config(fmax=0.01, max_steps=10)
    result = relax(structure, config, _NaNForcesCalc(), relax_cell=False)
    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "ComputationError"
    assert result.error.source == "structure_relaxer"


def test_relax_excessive_volume_change_raises_validation_error() -> None:
    """Excessive cell volume change produces status='failure' with ValidationError.

    Uses relax_cell=True with large cell stress forces and a low volume-change
    threshold (_max_volume_change_pct=5.0) to reliably trigger the check.
    """
    structure = _make_licoo2_structure()
    config = _make_config(fmax=0.01, max_steps=15)
    result = relax(
        structure,
        config,
        _BigStressCalc(),
        relax_cell=True,
        _max_volume_change_pct=5.0,  # low threshold: any expansion >5% fails
    )
    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "ValidationError"
    assert result.error.source == "structure_relaxer"


def test_relax_structure_collapse_raises_validation_error() -> None:
    """Structure with atoms closer than threshold produces ValidationError.

    Uses a high _min_bond_angstrom threshold (5.0 Å) so that any real
    bond (typically 1.5–3.5 Å) triggers the collapse check.
    """
    structure = _make_licoo2_structure()
    config = _make_config(fmax=0.01, max_steps=10)
    result = relax(
        structure,
        config,
        _ConvergingCalc(),
        relax_cell=False,
        _min_bond_angstrom=5.0,  # all real bonds are shorter than 5 Å
    )
    assert result.status == "failure"
    assert result.error is not None
    assert result.error.error_type == "ValidationError"
    assert result.error.source == "structure_relaxer"


# ---------------------------------------------------------------------------
# Tests 16–17: Config is respected
# ---------------------------------------------------------------------------


def test_relax_respects_fmax_config() -> None:
    """A looser fmax threshold converges when tighter one would not.

    _FixedFmaxCalc(0.05) always returns fmax=0.05.
    With config.fmax=0.10 (looser), fmax=0.05 < 0.10 → converged.
    With config.fmax=0.01 (tighter), fmax=0.05 > 0.01 → not converged.
    """
    structure = _make_licoo2_structure()
    calc = _FixedFmaxCalc(0.05)

    result_loose = relax(
        structure, _make_config(fmax=0.10, max_steps=5), calc, relax_cell=False
    )
    assert result_loose.status == "success"
    assert result_loose.data is not None
    assert result_loose.data["convergence_info"]["converged"] is True


def test_relax_respects_max_steps_config() -> None:
    """max_steps=2 with non-converging forces results in partial status."""
    structure = _make_licoo2_structure()
    config = _make_config(fmax=0.001, max_steps=2)
    result = relax(structure, config, _NonConvergingCalc(), relax_cell=False)
    assert result.status == "partial"
    assert result.data is not None
    assert result.data["convergence_info"]["steps"] <= 2


# ---------------------------------------------------------------------------
# Test 18: Cell relaxation enabled
# ---------------------------------------------------------------------------


def test_relax_with_cell_relaxation_enabled() -> None:
    """relax() works with relax_cell=True (FrechetCellFilter applied).

    Uses zero atomic forces and zero stress → immediately converged.
    """
    structure = _make_licoo2_structure()
    config = _make_config(fmax=0.01, max_steps=500)

    class _ZeroAllCalc(Calculator):
        implemented_properties = ["energy", "forces", "stress"]

        def __init__(self) -> None:
            super().__init__()
            self.use_cache = True

        def calculate(
            self, atoms: Any, properties: list[str], system_changes: list[str]
        ) -> None:
            n = len(atoms)
            self.results = {
                "energy": -10.0,
                "forces": np.zeros((n, 3)),
                "stress": np.zeros(6),
            }

    result = relax(structure, config, _ZeroAllCalc(), relax_cell=True)
    assert result.status == "success"
    assert result.data is not None
    assert "structure" in result.data
    assert result.data["convergence_info"]["converged"] is True


# ---------------------------------------------------------------------------
# Test 19: Provenance records MACE model version
# ---------------------------------------------------------------------------


def test_relax_provenance_records_mace_model_version() -> None:
    """Provenance config_snapshot contains 'mace_model_version' key."""
    structure = _make_licoo2_structure()
    config = _make_config()
    result = relax(
        structure,
        config,
        _ConvergingCalc(),
        mace_model_version="MACE-MP-0-v0.3.6",
    )
    expected = "MACE-MP-0-v0.3.6"
    assert result.provenance.config_snapshot.get("mace_model_version") == expected
