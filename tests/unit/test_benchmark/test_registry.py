"""Unit tests for cathodescope.benchmark.registry.

Tests implemented in T-22.
"""

import pytest

from cathodescope.benchmark.registry import BenchmarkMaterialRegistry


class TestBenchmarkMaterialRegistry:
    """Tests for BenchmarkMaterialRegistry."""

    def test_registry_contains_3_phase1_materials(self) -> None:
        """Phase 1 benchmark set must have exactly 3 materials."""
        registry = BenchmarkMaterialRegistry()
        materials = registry.get_materials("phase1_structural_analysis")
        assert len(materials) == 3

    def test_registry_licoo2_entry_correct(self) -> None:
        """LiCoO2 entry must match expected mp_id, formula, family, tags."""
        registry = BenchmarkMaterialRegistry()
        materials = registry.get_materials("phase1_structural_analysis")
        licoo2 = next(m for m in materials if m["mp_id"] == "mp-22526")
        assert licoo2["formula"] == "LiCoO2"
        assert licoo2["family"] == "layered_oxide"
        assert "phase1" in licoo2["benchmark_tags"]

    def test_registry_lifepo4_entry_correct(self) -> None:
        """LiFePO4 entry must match expected mp_id, formula, family, tags."""
        registry = BenchmarkMaterialRegistry()
        materials = registry.get_materials("phase1_structural_analysis")
        lifepo4 = next(m for m in materials if m["mp_id"] == "mp-19017")
        assert lifepo4["formula"] == "LiFePO4"
        assert lifepo4["family"] == "olivine_polyanion"
        assert "phase1" in lifepo4["benchmark_tags"]

    def test_registry_limn2o4_entry_correct(self) -> None:
        """LiMn2O4 entry must match expected mp_id, formula, family, tags."""
        registry = BenchmarkMaterialRegistry()
        materials = registry.get_materials("phase1_structural_analysis")
        limn2o4 = next(m for m in materials if m["mp_id"] == "mp-18767")
        assert limn2o4["formula"] == "LiMn2O4"
        assert limn2o4["family"] == "spinel"
        assert "phase1" in limn2o4["benchmark_tags"]

    def test_registry_get_by_name_returns_material_set(self) -> None:
        """get_materials returns a list of dicts for a known benchmark name."""
        registry = BenchmarkMaterialRegistry()
        materials = registry.get_materials("phase1_structural_analysis")
        assert isinstance(materials, list)
        for entry in materials:
            assert isinstance(entry, dict)
            assert "formula" in entry
            assert "mp_id" in entry
            assert "family" in entry
            assert "benchmark_tags" in entry

    def test_registry_unknown_benchmark_raises_error(self) -> None:
        """get_materials raises ValueError for an unknown benchmark name."""
        registry = BenchmarkMaterialRegistry()
        with pytest.raises(ValueError, match="unknown benchmark"):
            registry.get_materials("nonexistent_benchmark")

    def test_registry_materials_have_correct_families(self) -> None:
        """All phase1 materials use only allowed family literals."""
        allowed = {"layered_oxide", "olivine_polyanion", "spinel"}
        registry = BenchmarkMaterialRegistry()
        materials = registry.get_materials("phase1_structural_analysis")
        for entry in materials:
            assert entry["family"] in allowed

    def test_registry_materials_have_benchmark_tags(self) -> None:
        """Every material in the phase1 set carries the 'phase1' benchmark tag."""
        registry = BenchmarkMaterialRegistry()
        materials = registry.get_materials("phase1_structural_analysis")
        for entry in materials:
            assert isinstance(entry["benchmark_tags"], list)
            assert "phase1" in entry["benchmark_tags"]
