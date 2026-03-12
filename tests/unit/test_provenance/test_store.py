"""Unit tests for cathodescope.provenance.store.

17 tests implemented in T-06.
"""

import json
import os
import stat
from pathlib import Path
from typing import Any

import pytest

from cathodescope.provenance.store import ArtifactError, ArtifactStore

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_canonical(material_id: str = "mat-abc") -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "material_id": material_id,
        "formula": "LiCoO2",
        "provenance": {"tool": "test", "version": "0.1.0"},
    }


def _make_workflow_result(workflow_run_id: str = "wf-123") -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "workflow_run_id": workflow_run_id,
        "workflow_name": "structural_analysis",
        "status": "success",
        "provenance": {"tool": "test"},
    }


def _make_step_result(step_name: str = "resolve") -> dict[str, Any]:
    return {
        "step_name": step_name,
        "step_index": 0,
        "status": "success",
    }


def _make_report(report_id: str = "rep-001") -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "report_id": report_id,
        "material_id": "mat-abc",
        "title": "Structural Analysis: LiCoO2",
        "provenance": {"tool": "test"},
    }


def _make_benchmark_row(
    benchmark_run_id: str = "bench-1", material_id: str = "mat-abc"
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "benchmark_run_id": benchmark_run_id,
        "material_id": material_id,
        "formula": "LiCoO2",
        "status": "success",
    }


def _make_benchmark_summary(benchmark_run_id: str = "bench-1") -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "benchmark_run_id": benchmark_run_id,
        "benchmark_name": "phase1_structural_analysis",
        "materials_count": 1,
        "status_counts": {"success": 1},
        "provenance": {"tool": "test"},
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestArtifactStoreWrite:
    """Tests for write methods."""

    def test_store_write_canonical_material(self, tmp_path: Path) -> None:
        """write_canonical_material creates canonical.json at correct path."""
        store = ArtifactStore(root=tmp_path)
        data = _make_canonical("mat-001")
        store.write_canonical_material("mat-001", data)
        expected = tmp_path / "materials" / "mat-001" / "canonical.json"
        assert expected.exists()

    def test_store_read_canonical_material(self, tmp_path: Path) -> None:
        """read_canonical_material returns the same dict that was written."""
        store = ArtifactStore(root=tmp_path)
        data = _make_canonical("mat-002")
        store.write_canonical_material("mat-002", data)
        result = store.read_canonical_material("mat-002")
        assert result["material_id"] == "mat-002"
        assert result["formula"] == "LiCoO2"

    def test_store_write_workflow_result(self, tmp_path: Path) -> None:
        """write_workflow_result creates result.json at correct path."""
        store = ArtifactStore(root=tmp_path)
        data = _make_workflow_result("wf-aaa")
        store.write_workflow_result("wf-aaa", data)
        expected = tmp_path / "workflows" / "wf-aaa" / "result.json"
        assert expected.exists()

    def test_store_read_workflow_result(self, tmp_path: Path) -> None:
        """read_workflow_result returns the dict that was written."""
        store = ArtifactStore(root=tmp_path)
        data = _make_workflow_result("wf-bbb")
        store.write_workflow_result("wf-bbb", data)
        result = store.read_workflow_result("wf-bbb")
        assert result["workflow_run_id"] == "wf-bbb"
        assert result["status"] == "success"

    def test_store_write_step_results(self, tmp_path: Path) -> None:
        """write_step_result creates a zero-padded step file under steps/."""
        store = ArtifactStore(root=tmp_path)
        data = _make_step_result("resolve")
        store.write_step_result("wf-ccc", step_index=0, step_name="resolve", data=data)
        expected = tmp_path / "workflows" / "wf-ccc" / "steps" / "00_resolve.json"
        assert expected.exists()

    def test_store_write_report(self, tmp_path: Path) -> None:
        """write_report creates report.json and report.md at correct path."""
        store = ArtifactStore(root=tmp_path)
        data = _make_report("rep-001")
        store.write_report("rep-001", data, markdown="# Report\n\nContent here.")
        assert (tmp_path / "reports" / "rep-001" / "report.json").exists()
        assert (tmp_path / "reports" / "rep-001" / "report.md").exists()

    def test_store_write_benchmark_row(self, tmp_path: Path) -> None:
        """write_benchmark_row creates rows/{material_id}.json."""
        store = ArtifactStore(root=tmp_path)
        data = _make_benchmark_row("bench-1", "mat-abc")
        store.write_benchmark_row("bench-1", "mat-abc", data)
        expected = tmp_path / "benchmarks" / "bench-1" / "rows" / "mat-abc.json"
        assert expected.exists()

    def test_store_write_benchmark_summary(self, tmp_path: Path) -> None:
        """write_benchmark_summary creates summary.json under benchmark run dir."""
        store = ArtifactStore(root=tmp_path)
        data = _make_benchmark_summary("bench-2")
        store.write_benchmark_summary("bench-2", data)
        expected = tmp_path / "benchmarks" / "bench-2" / "summary.json"
        assert expected.exists()


class TestArtifactStoreDirectoryStructure:
    """Tests for directory layout and schema compliance."""

    def test_store_directory_structure_matches_schema(
        self, tmp_path: Path
    ) -> None:
        """Written artifacts land exactly where artifact_schema.md Section 3 says."""
        store = ArtifactStore(root=tmp_path)

        store.write_canonical_material("mat-x", _make_canonical("mat-x"))
        store.write_workflow_result("wf-x", _make_workflow_result("wf-x"))
        store.write_step_result("wf-x", 0, "resolve", _make_step_result("resolve"))
        store.write_report("rep-x", _make_report("rep-x"), markdown="# R")
        store.write_benchmark_row(
            "bench-x", "mat-x", _make_benchmark_row("bench-x", "mat-x")
        )
        store.write_benchmark_summary("bench-x", _make_benchmark_summary("bench-x"))

        assert (tmp_path / "materials" / "mat-x" / "canonical.json").exists()
        assert (tmp_path / "workflows" / "wf-x" / "result.json").exists()
        assert (tmp_path / "workflows" / "wf-x" / "steps" / "00_resolve.json").exists()
        assert (tmp_path / "reports" / "rep-x" / "report.json").exists()
        assert (tmp_path / "reports" / "rep-x" / "report.md").exists()
        assert (tmp_path / "benchmarks" / "bench-x" / "summary.json").exists()
        assert (tmp_path / "benchmarks" / "bench-x" / "rows" / "mat-x.json").exists()

    def test_store_json_uses_2_space_indent(self, tmp_path: Path) -> None:
        """JSON files must use 2-space indentation."""
        store = ArtifactStore(root=tmp_path)
        store.write_canonical_material("mat-indent", _make_canonical("mat-indent"))
        path = tmp_path / "materials" / "mat-indent" / "canonical.json"
        raw = path.read_text()
        # First data line should be indented with exactly 2 spaces
        lines = raw.splitlines()
        two_space = [
            ln for ln in lines if ln.startswith("  ") and not ln.startswith("   ")
        ]
        assert len(two_space) > 0, "Expected 2-space-indented lines in JSON output"


class TestArtifactStoreImmutability:
    """Tests for file immutability enforcement."""

    def test_store_files_are_read_only_after_write(
        self, tmp_path: Path
    ) -> None:
        """Artifact files must have read-only permissions after write."""
        store = ArtifactStore(root=tmp_path)
        store.write_canonical_material("mat-ro", _make_canonical("mat-ro"))
        path = tmp_path / "materials" / "mat-ro" / "canonical.json"
        mode = stat.S_IMODE(os.stat(path).st_mode)
        assert mode == 0o444, f"Expected 0o444, got {oct(mode)}"

    def test_store_overwrite_raises_artifact_error(
        self, tmp_path: Path
    ) -> None:
        """Writing to an existing non-cache artifact path raises ArtifactError."""
        store = ArtifactStore(root=tmp_path)
        store.write_canonical_material("mat-dup", _make_canonical("mat-dup"))
        with pytest.raises(ArtifactError, match="already exists"):
            store.write_canonical_material("mat-dup", _make_canonical("mat-dup"))


class TestArtifactStoreProvenance:
    """Tests for provenance convenience copies."""

    def test_store_write_provenance_json_convenience_copy(
        self, tmp_path: Path
    ) -> None:
        """Writing canonical_material also produces a provenance.json beside it."""
        store = ArtifactStore(root=tmp_path)
        data = _make_canonical("mat-prov")
        store.write_canonical_material("mat-prov", data)
        prov_path = tmp_path / "materials" / "mat-prov" / "provenance.json"
        assert prov_path.exists()
        prov_data = json.loads(prov_path.read_text())
        assert prov_data == data["provenance"]


class TestArtifactStoreIntegrity:
    """Tests for verify_integrity method."""

    def test_store_integrity_check_passes_when_complete(
        self, tmp_path: Path
    ) -> None:
        """verify_integrity returns True when result.json exists for workflow."""
        store = ArtifactStore(root=tmp_path)
        store.write_workflow_result("wf-ok", _make_workflow_result("wf-ok"))
        assert store.verify_integrity("wf-ok") is True

    def test_store_integrity_check_fails_when_file_missing(
        self, tmp_path: Path
    ) -> None:
        """verify_integrity raises ArtifactError when result.json is deleted."""
        store = ArtifactStore(root=tmp_path)
        store.write_workflow_result("wf-bad", _make_workflow_result("wf-bad"))
        result_path = tmp_path / "workflows" / "wf-bad" / "result.json"
        # restore write permission so we can delete it
        os.chmod(result_path, 0o644)
        result_path.unlink()
        with pytest.raises(ArtifactError, match="missing"):
            store.verify_integrity("wf-bad")


class TestArtifactStoreCache:
    """Tests for cache write/read (overwrite allowed)."""

    def test_store_cache_write_and_read(self, tmp_path: Path) -> None:
        """Cache write creates the file; read returns the same data."""
        store = ArtifactStore(root=tmp_path)
        data = {"mp_id": "mp-22526", "structure": {"lattice": {}, "sites": []}}
        store.write_cache("mp-22526", "abc123", data)
        expected = tmp_path / "cache" / "mp" / "mp-22526_abc123.json"
        assert expected.exists()
        result = store.read_cache("mp-22526", "abc123")
        assert result["mp_id"] == "mp-22526"

    def test_store_cache_overwrite_is_allowed(self, tmp_path: Path) -> None:
        """Writing to an existing cache key does NOT raise ArtifactError."""
        store = ArtifactStore(root=tmp_path)
        data_v1 = {"mp_id": "mp-22526", "version": 1}
        data_v2 = {"mp_id": "mp-22526", "version": 2}
        store.write_cache("mp-22526", "hash1", data_v1)
        store.write_cache("mp-22526", "hash1", data_v2)  # must not raise
        result = store.read_cache("mp-22526", "hash1")
        assert result["version"] == 2
