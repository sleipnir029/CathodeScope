"""Artifact store.

Implements ArtifactStore with write/read/exists/verify_integrity methods.
Directory layout per artifact_schema.md Section 3.
Artifacts are read-only after write (except cache directory).

Implemented in T-06.
"""

import json
import os
from pathlib import Path
from typing import Any


class ArtifactError(Exception):
    """Raised for artifact storage violations.

    Covers: overwrite attempts on immutable artifacts, missing files during
    integrity checks, and read errors on corrupted or absent artifact files.
    """


class ArtifactStore:
    """Filesystem-backed artifact store for CathodeScope workflow outputs.

    All non-cache artifacts are written once and then set to read-only
    (permissions 0o444). Overwrite attempts raise ``ArtifactError``.
    The cache directory (``cache/mp/``) is the sole exception: cache entries
    may be overwritten freely.

    Directory layout follows ``artifact_schema.md`` Section 3 exactly::

        {root}/
        ├── materials/{material_id}/canonical.json
        │                          /provenance.json
        ├── workflows/{run_id}/result.json
        │                     /provenance.json
        │                     /steps/{idx:02}_{name}.json
        ├── reports/{report_id}/report.json
        │                      /report.md
        │                      /provenance.json
        ├── benchmarks/{run_id}/summary.json
        │                      /provenance.json
        │                      /rows/{material_id}.json
        └── cache/mp/{mp_id}_{fields_hash}.json

    Parameters
    ----------
    root:
        Root directory for artifact storage. Created on first write if absent.
    """

    def __init__(self, root: Path | str) -> None:
        self._root = Path(root)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_json(self, path: Path, data: dict[str, Any], *, readonly: bool) -> None:
        """Write *data* as 2-space-indented JSON to *path*.

        Creates parent directories as needed. When *readonly* is True the file
        is chmod'd to 0o444 after writing.

        Raises
        ------
        ArtifactError
            If *path* already exists and *readonly* is True (immutability guard).
        """
        if readonly and path.exists():
            raise ArtifactError(
                f"Artifact already exists and is immutable: {path}. "
                "Create a new artifact with a different ID instead of overwriting."
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        # For cache (not readonly), make writable first if it exists
        if path.exists():
            os.chmod(path, 0o644)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        if readonly:
            os.chmod(path, 0o444)

    def _read_json(self, path: Path) -> dict[str, Any]:
        """Read and return a JSON dict from *path*.

        Raises
        ------
        ArtifactError
            If *path* does not exist or cannot be parsed.
        """
        if not path.exists():
            raise ArtifactError(f"Artifact file missing: {path}")
        result: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return result

    def _write_provenance_copy(self, directory: Path, data: dict[str, Any]) -> None:
        """Write a convenience provenance.json alongside the artifact directory.

        Only writes if the *data* dict contains a 'provenance' key.
        The provenance.json is also set to read-only after writing.
        """
        if "provenance" not in data:
            return
        prov_path = directory / "provenance.json"
        if not prov_path.exists():
            prov_path.parent.mkdir(parents=True, exist_ok=True)
            serialized = json.dumps(data["provenance"], indent=2)
            prov_path.write_text(serialized, encoding="utf-8")
            os.chmod(prov_path, 0o444)

    # ------------------------------------------------------------------
    # Canonical material
    # ------------------------------------------------------------------

    def write_canonical_material(self, material_id: str, data: dict[str, Any]) -> None:
        """Write a CanonicalMaterial record.

        Creates:
        - ``materials/{material_id}/canonical.json``
        - ``materials/{material_id}/provenance.json`` (if provenance present)

        Parameters
        ----------
        material_id:
            Internal CathodeScope material UUID string.
        data:
            JSON-serializable CanonicalMaterial dict.

        Raises
        ------
        ArtifactError
            If canonical.json for *material_id* already exists.
        """
        mat_dir = self._root / "materials" / material_id
        self._write_json(mat_dir / "canonical.json", data, readonly=True)
        self._write_provenance_copy(mat_dir, data)

    def read_canonical_material(self, material_id: str) -> dict[str, Any]:
        """Read and return the CanonicalMaterial dict for *material_id*.

        Raises
        ------
        ArtifactError
            If the file does not exist.
        """
        path = self._root / "materials" / material_id / "canonical.json"
        return self._read_json(path)

    # ------------------------------------------------------------------
    # Workflow result
    # ------------------------------------------------------------------

    def write_workflow_result(self, workflow_run_id: str, data: dict[str, Any]) -> None:
        """Write a WorkflowResult record.

        Creates:
        - ``workflows/{workflow_run_id}/result.json``
        - ``workflows/{workflow_run_id}/provenance.json`` (if provenance present)

        Raises
        ------
        ArtifactError
            If result.json for *workflow_run_id* already exists.
        """
        wf_dir = self._root / "workflows" / workflow_run_id
        self._write_json(wf_dir / "result.json", data, readonly=True)
        self._write_provenance_copy(wf_dir, data)

    def read_workflow_result(self, workflow_run_id: str) -> dict[str, Any]:
        """Read and return the WorkflowResult dict for *workflow_run_id*.

        Raises
        ------
        ArtifactError
            If the file does not exist.
        """
        path = self._root / "workflows" / workflow_run_id / "result.json"
        return self._read_json(path)

    # ------------------------------------------------------------------
    # Step result
    # ------------------------------------------------------------------

    def write_step_result(
        self,
        workflow_run_id: str,
        step_index: int,
        step_name: str,
        data: dict[str, Any],
    ) -> None:
        """Write a StepResult record for one workflow step.

        File path: ``workflows/{run_id}/steps/{step_index:02d}_{step_name}.json``

        Parameters
        ----------
        workflow_run_id:
            UUID of the parent workflow run.
        step_index:
            Zero-based step index (zero-padded to two digits in filename).
        step_name:
            Human-readable step name (e.g. ``"resolve"``, ``"fetch"``).
        data:
            JSON-serializable StepResult dict.

        Raises
        ------
        ArtifactError
            If the step file already exists.
        """
        steps_dir = self._root / "workflows" / workflow_run_id / "steps"
        filename = f"{step_index:02d}_{step_name}.json"
        self._write_json(steps_dir / filename, data, readonly=True)

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def write_report(
        self,
        report_id: str,
        data: dict[str, Any],
        markdown: str | None = None,
    ) -> None:
        """Write a ReportRecord and optional Markdown file.

        Creates:
        - ``reports/{report_id}/report.json``
        - ``reports/{report_id}/report.md`` (only if *markdown* is provided)
        - ``reports/{report_id}/provenance.json`` (if provenance present)

        Raises
        ------
        ArtifactError
            If report.json for *report_id* already exists.
        """
        rep_dir = self._root / "reports" / report_id
        self._write_json(rep_dir / "report.json", data, readonly=True)
        if markdown is not None:
            md_path = rep_dir / "report.md"
            if md_path.exists():
                raise ArtifactError(
                    f"Artifact already exists and is immutable: {md_path}."
                )
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(markdown, encoding="utf-8")
            os.chmod(md_path, 0o444)
        self._write_provenance_copy(rep_dir, data)

    # ------------------------------------------------------------------
    # Benchmark row and summary
    # ------------------------------------------------------------------

    def write_benchmark_row(
        self,
        benchmark_run_id: str,
        material_id: str,
        data: dict[str, Any],
    ) -> None:
        """Write a BenchmarkRow for one material within a benchmark run.

        File path: ``benchmarks/{benchmark_run_id}/rows/{material_id}.json``

        Raises
        ------
        ArtifactError
            If the row file already exists.
        """
        rows_dir = self._root / "benchmarks" / benchmark_run_id / "rows"
        self._write_json(rows_dir / f"{material_id}.json", data, readonly=True)

    def write_benchmark_summary(
        self,
        benchmark_run_id: str,
        data: dict[str, Any],
    ) -> None:
        """Write a BenchmarkSummary record.

        File path: ``benchmarks/{benchmark_run_id}/summary.json``

        Raises
        ------
        ArtifactError
            If summary.json for *benchmark_run_id* already exists.
        """
        bench_dir = self._root / "benchmarks" / benchmark_run_id
        self._write_json(bench_dir / "summary.json", data, readonly=True)
        self._write_provenance_copy(bench_dir, data)

    # ------------------------------------------------------------------
    # Cache (overwrite allowed)
    # ------------------------------------------------------------------

    def write_cache(
        self,
        mp_id: str,
        fields_hash: str,
        data: dict[str, Any],
    ) -> None:
        """Write a cached MP API response.

        File path: ``cache/mp/{mp_id}_{fields_hash}.json``
        Cache files may be overwritten freely (not subject to immutability).

        Parameters
        ----------
        mp_id:
            Materials Project ID (e.g. ``"mp-22526"``).
        fields_hash:
            SHA-256 hex digest of the sorted API field names.
        data:
            JSON-serializable API response payload.
        """
        cache_path = self._root / "cache" / "mp" / f"{mp_id}_{fields_hash}.json"
        self._write_json(cache_path, data, readonly=False)

    def read_cache(self, mp_id: str, fields_hash: str) -> dict[str, Any]:
        """Read and return a cached MP API response.

        Raises
        ------
        ArtifactError
            If the cache file does not exist.
        """
        path = self._root / "cache" / "mp" / f"{mp_id}_{fields_hash}.json"
        return self._read_json(path)

    # ------------------------------------------------------------------
    # Existence check
    # ------------------------------------------------------------------

    def exists(self, path: Path | str) -> bool:
        """Return True if *path* (absolute or relative to root) exists.

        Parameters
        ----------
        path:
            Absolute path or path relative to the store root.
        """
        p = Path(path)
        if not p.is_absolute():
            p = self._root / p
        return p.exists()

    # ------------------------------------------------------------------
    # Integrity check
    # ------------------------------------------------------------------

    def verify_integrity(self, workflow_run_id: str) -> bool:
        """Verify that required artifacts exist for *workflow_run_id*.

        Checks that ``workflows/{workflow_run_id}/result.json`` is present.
        Raises ``ArtifactError`` listing every missing file if any are absent.

        Parameters
        ----------
        workflow_run_id:
            UUID of the workflow run to verify.

        Returns
        -------
        bool
            ``True`` when all required artifacts are present.

        Raises
        ------
        ArtifactError
            If any required artifact file is missing.
        """
        wf_dir = self._root / "workflows" / workflow_run_id
        required = [wf_dir / "result.json"]
        missing = [str(p) for p in required if not p.exists()]
        if missing:
            raise ArtifactError(
                f"Integrity check failed for workflow {workflow_run_id!r}. "
                f"missing artifacts: {missing}"
            )
        return True
