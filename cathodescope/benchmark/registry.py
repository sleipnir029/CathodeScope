"""Benchmark material registry.

Defines the set of benchmark materials (LiCoO2, LiFePO4, LiMn2O4)
with mp_ids, expected space groups, and atom counts.

Implemented in T-22.
"""

from typing import Any

_PHASE1_MATERIALS: list[dict[str, Any]] = [
    {
        "formula": "LiCoO2",
        "mp_id": "mp-22526",
        "family": "layered_oxide",
        "benchmark_tags": ["phase1"],
    },
    {
        "formula": "LiFePO4",
        "mp_id": "mp-19017",
        "family": "olivine_polyanion",
        "benchmark_tags": ["phase1"],
    },
    {
        "formula": "LiMn2O4",
        "mp_id": "mp-18767",
        "family": "spinel",
        "benchmark_tags": ["phase1"],
    },
]

_BENCHMARK_REGISTRY: dict[str, list[dict[str, Any]]] = {
    "phase1_structural_analysis": _PHASE1_MATERIALS,
}


class BenchmarkMaterialRegistry:
    """Registry defining which materials belong to each benchmark set.

    Separates material definitions from runner logic. Benchmark sets are
    keyed by name (e.g. ``"phase1_structural_analysis"``). Each entry
    contains ``formula``, ``mp_id``, ``family``, and ``benchmark_tags``.
    """

    def get_materials(self, benchmark_name: str) -> list[dict[str, Any]]:
        """Return the list of material entries for a named benchmark set.

        Parameters
        ----------
        benchmark_name:
            Name of the benchmark set, e.g. ``"phase1_structural_analysis"``.

        Returns
        -------
        list[dict[str, Any]]
            Each dict has keys: ``formula``, ``mp_id``, ``family``,
            ``benchmark_tags``.

        Raises
        ------
        ValueError
            If ``benchmark_name`` is not a registered benchmark.
        """
        if benchmark_name not in _BENCHMARK_REGISTRY:
            raise ValueError(
                f"unknown benchmark: {benchmark_name!r}. "
                f"Known benchmarks: {list(_BENCHMARK_REGISTRY)}"
            )
        return list(_BENCHMARK_REGISTRY[benchmark_name])
