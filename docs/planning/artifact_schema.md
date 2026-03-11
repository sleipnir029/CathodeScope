# CathodeScope Artifact Schema

> Definitive schema reference for every data structure CathodeScope persists.
> All data artifacts are immutable, provenance-tracked, and JSON-serializable.

---

## 1. Design Principles

- **Immutability**: All artifacts are write-once. Once a workflow run completes, its artifacts are never modified in place. New runs create new artifacts.
- **JSON-serializable**: Every record can be serialized to JSON for storage and interchange.
- **Provenance everywhere**: Every artifact carries a `ProvenanceRecord` linking it to its inputs, configuration, and software versions.
- **Schema versioned**: Every record has a `schema_version` field (semver) for forward compatibility.
- **No free-form dependencies**: No downstream module depends on free-form text output (Extension Rule 2 from the project design rules).
- **Structured results**: Every tool returns a standardized `ToolResult` structure (Extension Rule 1).

Cross-reference: `architecture.md` extension-first design rules.

### Units Convention

All numeric values in CathodeScope artifacts follow these project-wide conventions:

| Quantity | Unit | Symbol |
|----------|------|--------|
| Energy | electronvolt | eV |
| Force | electronvolt per Angstrom | eV/Å |
| Length | Angstrom | Å |
| Angle | degree | ° |
| Volume | cubic Angstrom | Å³ |
| Deviation | percent | % (unless stated otherwise) |
| Time | seconds | s |
| Temperature | Kelvin | K |

These conventions apply to all JSON artifacts, reports, and internal data structures. Changing a unit convention requires a MAJOR schema version bump (e.g., 1.x.x → 2.0.0) and migration of all existing artifacts.

---

## 2. Core Data Records

### Notation

All records use the following pseudocode notation. This is intentionally implementation-agnostic; it describes shape, not code.

```
RecordName:
  field_name: type          # description
  field_name: type          # description
```

Type conventions used throughout this document:

| Notation | Meaning |
|----------|---------|
| `string` | UTF-8 text value |
| `integer` | Whole number |
| `float` | IEEE 754 double-precision number |
| `boolean` | `true` or `false` |
| `object` | JSON object (key-value map) |
| `list[T]` | Ordered JSON array of type T |
| `T \| null` | Value of type T, or JSON `null` |
| `SomeRecord` | Nested instance of another named record |

---

### 2.1 Canonical Material Record

The authoritative representation of a cathode material within CathodeScope. Every material that enters the system is resolved to exactly one `CanonicalMaterial`.

```
CanonicalMaterial:
  schema_version: string          # semver, e.g., "1.0.0"
  material_id: string             # UUID, internal to CathodeScope
  formula: string                 # e.g., "LiCoO2"
  reduced_formula: string         # e.g., "LiCoO2"
  family: string                  # enum: "layered_oxide" | "olivine_polyanion" | "spinel" | "other"
  structure: object               # pymatgen Structure serialized via as_dict()
  source: string                  # enum: "materials_project" | "user_upload" | "generated"
  mp_id: string | null            # e.g., "mp-22526", null if not from MP
  identifiers: object             # additional IDs: {"icsd": "...", "doi": "...", ...}
  benchmark_tags: list[string]    # e.g., ["phase1", "layered_oxide"]
  workflow_eligibility: object    # e.g., {"structural_analysis": true, "voltage_estimate": false}
  created_at: string              # ISO 8601 timestamp
  provenance: ProvenanceRecord    # nested (see Section 2.5)
```

**Notes:**

- The `material_id` is generated internally and is the primary key for all cross-references. No other record stores a formula as a foreign key; they store `material_id`.
- The `structure` field uses pymatgen's `as_dict()` serialization, which is a well-documented JSON-compatible format. This preserves lattice parameters, species, fractional coordinates, and site properties.
- The `family` field supports classification of cathode materials into the three benchmark families. `"other"` is a catch-all for materials outside the three benchmark families.
- The `workflow_eligibility` map is populated at material creation time based on available data (e.g., a material without a known structure cannot enter a relaxation workflow).
- The `identifiers` object is open-ended to accommodate future cross-database linking (ICSD, AFLOW, COD, DOI, etc.).
- **Phase 1 defaults:** `identifiers` defaults to `{}`, `workflow_eligibility` defaults to `{"structural_analysis": true}`, and `benchmark_tags` defaults to `[]`. These fields are optional in Phase 1 and will be fully populated as functionality expands.

Cross-reference: `architecture.md` Canonical Material Model component.

---

### 2.2 Workflow Result Record

Captures the full outcome of a single workflow execution against a single material.

```
WorkflowResult:
  schema_version: string
  workflow_run_id: string          # UUID for this specific run
  workflow_name: string            # e.g., "structural_analysis"
  workflow_version: string         # e.g., "1.0.0"
  material_id: string              # references CanonicalMaterial.material_id
  status: string                   # enum: "success" | "partial_success" | "soft_failure" | "hard_failure" | "infrastructure_failure"
  steps: list[StepResult]          # ordered list of step results
  started_at: string               # ISO 8601
  completed_at: string             # ISO 8601
  runtime_seconds: float           # wall-clock time
  config_snapshot: object          # full workflow configuration used
  provenance: ProvenanceRecord
```

```
StepResult:
  step_name: string                # e.g., "fetch_structure", "relax_structure", "compare_reference"
  step_index: integer              # 0-based position in workflow
  status: string                   # enum: "success" | "warning" | "failed" | "skipped"
  evidence_type: string | null     # from validity ladder: "A-retrieved" | "A-computed" | "A-compared" | "B-restricted" | "C-proxy" | null (for non-scientific steps like input resolution and report generation)
  data: object                     # step-specific output data (structure depends on step type)
  warnings: list[string]           # human-readable warning messages
  error: ErrorRecord | null        # null if no error
  artifacts: list[string]          # relative paths to artifact files produced by this step
  started_at: string               # ISO 8601
  completed_at: string             # ISO 8601
  provenance: ProvenanceRecord
```

```
ErrorRecord:
  error_type: string               # enum: "InputError" | "RetrievalError" | "ComputationError" | "ValidationError" | "ArtifactError"
  message: string                  # human-readable error description
  details: object | null           # structured error context (stack trace, parameters, etc.)
  recoverable: boolean             # whether the workflow can continue past this error
```

**Status definitions:**

| Status | Meaning |
|--------|---------|
| `success` | All checks passed, output is valid. |
| `partial_success` | Workflow completed but some metrics are outside ideal thresholds. The result is scientifically informative but carries caveats. |
| `soft_failure` | Workflow completed with warnings such as borderline convergence or minor symmetry breaks. Results should be treated with caution. |
| `hard_failure` | Workflow could not complete due to divergence, exception, or missing data. No usable result was produced. |
| `infrastructure_failure` | Workflow could not execute due to an environmental or system issue unrelated to the science (network timeout, disk full, missing dependency, OOM). Retryable once the infrastructure issue is resolved. |

**Error type definitions:**

| Error Type | Meaning |
|------------|---------|
| `InputError` | Invalid or unresolvable user input (bad formula, unknown MP ID). |
| `RetrievalError` | Failure to fetch data from an external source (MP API down, network timeout). |
| `ComputationError` | Failure during a computational step (MACE divergence, SCF non-convergence). |
| `ValidationError` | Computed result fails a physics sanity check (negative volume, impossible bond length). |
| `ArtifactError` | Failure to read or write an artifact file (disk full, permission denied, corrupt JSON). |

Cross-reference: `architecture.md` Workflow Engine, `benchmark_spec.md` success/failure categories.

---

### 2.3 Tool Result Record

The universal return type for all scientific tools. This is Extension Rule 1 in action: every tool in CathodeScope must return a `ToolResult`. No tool may return a raw dict, bare value, or unstructured text.

```
ToolResult:
  status: string                   # "success" | "warning" | "error"
  evidence_type: string            # from validity ladder
  data: object                     # tool-specific payload
  warnings: list[string]           # any warnings generated
  provenance: ProvenanceRecord
  artifacts: list[string]          # paths to files created by this tool
```

**Contract:**

- Every callable tool (structure fetcher, normalizer, relaxer, validator, comparator, reporter) wraps its output in a `ToolResult`.
- The `data` field is tool-specific but always a JSON object. Its schema is documented per-tool.
- The `evidence_type` field is mandatory and must be drawn from the validity ladder defined in `scientific_validity_matrix.md`.
- If `status` is `"error"`, the `data` field may be empty or partial, but `warnings` must contain at least one entry describing the failure.
- When reporting lattice parameter deviations, all values correspond to the conventional cell. The `cell_convention` field (`"primitive"` or `"conventional"`) is included in comparator output to confirm the cell type used.

Cross-reference: `architecture.md` extension-first rules, `scientific_validity_matrix.md` evidence types.

---

### 2.4 Report Record

The structured representation of a human-readable scientific report. Reports are generated from `WorkflowResult` data and are always reproducible from the underlying structured records.

```
ReportRecord:
  schema_version: string
  report_id: string                # UUID
  material_id: string              # references CanonicalMaterial.material_id
  workflow_result_id: string       # references WorkflowResult.workflow_run_id
  report_type: string              # e.g., "structural_analysis", "benchmark_summary"
  raw_user_input: string           # the original user input that initiated this workflow (e.g., "LiCoO2", "mp-22526")
  title: string                    # e.g., "Structural Analysis: LiCoO2"
  sections: list[ReportSection]    # ordered report sections
  evidence_summary: object         # count of evidence labels, e.g., {"A-computed": 3, "A-compared": 2}
  warnings: list[string]           # report-level warnings
  generated_at: string             # ISO 8601
  provenance: ProvenanceRecord
```

```
ReportSection:
  heading: string                  # section title
  content_markdown: string         # rendered Markdown for human reading
  data: object                     # structured data behind this section (machine-readable)
  evidence_labels: list[string]    # evidence level labels for claims in this section
```

**Notes:**

- The `data` field in each section holds the machine-readable values; `content_markdown` is derived from `data` and evidence labels. This ensures reports can be regenerated from structured data alone.
- The `evidence_summary` at the report level is an aggregate count across all sections, providing a quick overview of the strength of evidence in the report.
- Reports are always generated from a specific `WorkflowResult`. The `workflow_result_id` field establishes this link unambiguously.

Cross-reference: `architecture.md` Reporting Layer, `scientific_validity_matrix.md` for evidence label format.

---

### 2.5 Provenance Record

The audit trail record embedded in every other artifact. Provides a complete chain from any artifact back to its inputs, configuration, and software environment.

```
ProvenanceRecord:
  schema_version: string
  created_at: string               # ISO 8601
  created_by: string               # "cathodescope" | "user" | "agent"
  cathodescope_version: string     # software version string
  python_version: string           # e.g., "3.11.7"
  dependencies: object             # pinned versions: {"pymatgen": "2024.x.y", "mace-torch": "0.x.y", "ase": "3.x.y", ...}
  config_snapshot: object          # full configuration used for this operation
  input_hash: string               # SHA-256 hash of the input data for reproducibility verification
  parent_ids: list[string]         # IDs of artifacts this record was derived from (lineage chain)
  mace_checkpoint_hash: string | null  # SHA-256 hash of the MACE model checkpoint file used (null if step did not involve MACE)
  mace_model_name: string | null       # Human-readable MACE model variant name (e.g., 'MACE-MP-0-medium'), null if step did not involve MACE
  mp_database_version: string | null   # Materials Project database version string at retrieval time (null if no MP query)
  random_seeds: object | null      # Random seeds used for reproducibility (e.g., {'numpy': 42, 'torch': 42}), null if deterministic by default
  compute_device: string | null    # Compute device used (e.g., 'cpu', 'cuda:0', 'mps'), null if step did not involve ML computation
  platform: string                 # platform identifier, e.g., "Darwin-arm64" or "Linux-x86_64"
  git_commit: string | null        # Git commit hash at runtime for reproducibility (null if not in a git repo or dirty working tree)
  notes: string | null             # optional human-readable note
```

**Notes:**

- The `ProvenanceRecord` is nested inside every other record. It is not stored as a standalone top-level entity (though a convenience copy is written to `provenance.json` at the directory level).
- `parent_ids` forms a directed acyclic graph (DAG) of artifact lineage. For a relaxed structure, the parent is the normalized structure; for the normalized structure, the parent is the original structure; for the original structure, the parent is the canonical material.
- `input_hash` is computed over the serialized input to the operation. Two runs with identical inputs and identical configuration should produce identical `input_hash` values, enabling reproducibility verification.
- `dependencies` must include at minimum: `pymatgen`, `ase`, `mace-torch`, `mp-api`, and `numpy`. Additional dependencies are included as relevant.
- `config_snapshot` captures the full configuration at the moment the operation was executed, not a reference to a config file. This ensures the provenance is self-contained even if the config file is later modified.

---

### 2.6 Benchmark Row Record

A single row in a benchmark results table, representing one material's outcome in one workflow within a benchmark run.

```
BenchmarkRow:
  schema_version: string
  benchmark_run_id: string         # UUID for the overall benchmark run
  material_id: string              # references CanonicalMaterial.material_id
  formula: string                  # denormalized for readability in tables
  family: string                   # denormalized
  workflow_name: string
  workflow_version: string
  status: string                   # enum: "success" | "partial_success" | "soft_failure" | "hard_failure" | "infrastructure_failure"
  metrics: object                  # key-value pairs from benchmark metric table
  failure_category: string | null  # from benchmark failure taxonomy, null if success
  timestamp: string                # ISO 8601
  provenance: ProvenanceRecord
```

**Example `metrics` object** (for a structural analysis workflow):

```json
{
  "input_resolution": true,
  "structure_retrieval": true,
  "structure_normalization": true,
  "space_group_input": "R-3m",
  "relaxation_convergence": true,
  "relaxation_steps": 23,
  "final_fmax": 0.005,
  "final_energy": -42.156,
  "lattice_param_deviation_a_pct": 0.53,
  "lattice_param_deviation_b_pct": 0.53,
  "lattice_param_deviation_c_pct": 0.22,
  "volume_deviation_pct": 1.28,
  "angle_deviation_alpha": 0.0,
  "angle_deviation_beta": 0.0,
  "angle_deviation_gamma": 0.0,
  "symmetry_preserved": true,
  "space_group_output": "R-3m",
  "symprec_used": 0.1,
  "min_bond_length": 1.92,
  "max_bond_length": 2.11,
  "evidence_labeling_complete": true,
  "report_generated": true,
  "runtime_seconds": 12.3,
  "workflow_version": "1.0.0"
}
```

**Notes:**

- `formula` and `family` are denormalized (duplicated from `CanonicalMaterial`) to make benchmark tables self-contained and readable without joins.
- The `metrics` object schema varies by workflow type. The metric keys are defined in `benchmark_spec.md` for each workflow.
- `failure_category` is drawn from the failure taxonomy defined in `architecture.md` Section 4.8: `retrieval_failure`, `convergence_failure`, `validation_failure`, `artifact_failure`, `unknown_failure`. It is `null` when `status` is `"success"`.

Cross-reference: `architecture.md` Section 4.8 for failure taxonomy, `benchmark_spec.md` for metric definitions.

---

### 2.7 Benchmark Summary Record

Aggregates the results of an entire benchmark run across all materials.

```
BenchmarkSummary:
  schema_version: string
  benchmark_run_id: string         # UUID
  benchmark_name: string           # e.g., "phase1_structural_analysis"
  materials_count: integer         # total materials in this benchmark run
  status_counts: object            # e.g., {"success": 2, "partial_success": 1, "soft_failure": 0, "hard_failure": 0, "infrastructure_failure": 0}
  rows: list[string]               # list of BenchmarkRow file paths
  started_at: string               # ISO 8601
  completed_at: string             # ISO 8601
  runtime_seconds: float           # total benchmark runtime
  provenance: ProvenanceRecord
```

**Notes:**

- `status_counts` enumerates every status value even if the count is zero, ensuring consumers can rely on the keys being present.
- `rows` contains relative file paths (relative to the benchmark run directory) pointing to individual `BenchmarkRow` JSON files. This avoids embedding all rows in a single large file while maintaining a manifest.
- `materials_count` must equal the sum of all values in `status_counts` and the length of `rows`. Any mismatch indicates a pipeline bug.

---

## 3. Directory and File Conventions

All artifacts are organized under a root `artifacts/` directory. The layout is deterministic: given an ID, the file path is computable without a database lookup.

```
artifacts/
├── materials/
│   └── {material_id}/
│       ├── canonical.json              # CanonicalMaterial record
│       ├── structures/
│       │   ├── original.json           # as-retrieved structure (pymatgen dict)
│       │   ├── normalized.json         # after normalization
│       │   └── relaxed.json            # after MACE relaxation
│       └── provenance.json             # material-level provenance
├── workflows/
│   └── {workflow_run_id}/
│       ├── result.json                 # WorkflowResult record
│       ├── steps/
│       │   ├── 00_resolve.json         # StepResult for input resolution
│       │   ├── 01_fetch.json           # StepResult for MP retrieval
│       │   ├── 02_normalize.json       # StepResult for normalization
│       │   ├── 03_relax.json           # StepResult for relaxation
│       │   ├── 04_compare.json         # StepResult for reference comparison
│       │   └── 05_validate.json        # StepResult for physics validation
│       │   # Note: Report generation (Step 6) does not produce a step file under `steps/`.
│       │   # It produces report artifacts separately under `reports/{report_id}/`.
│       └── provenance.json             # workflow-level provenance
├── reports/
│   └── {report_id}/
│       ├── report.json                 # ReportRecord (machine-readable)
│       ├── report.md                   # Human-readable Markdown report
│       └── provenance.json
├── benchmarks/
│   └── {benchmark_run_id}/
│       ├── summary.json                # BenchmarkSummary record
│       ├── rows/
│       │   ├── {material_id}.json      # BenchmarkRow per material
│       │   └── ...
│       └── provenance.json
└── cache/
    └── mp/
        └── {mp_id}_{api_fields_hash}.json  # cached MP API responses
```

**Naming conventions:**

- All IDs are UUIDs (v4) formatted as lowercase hex with hyphens (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`).
- All timestamps are ISO 8601 in UTC with timezone designator (e.g., `2026-03-10T14:30:00Z`).
- Step files use zero-padded two-digit numeric prefixes for lexicographic sort order (e.g., `00_`, `01_`, ..., `99_`).
- JSON files use 2-space indentation for human readability.
- File names use lowercase with underscores as separators. No spaces, no uppercase.
- The `provenance.json` at each directory level is a convenience copy of the provenance embedded in the primary record. It exists to allow quick provenance inspection without parsing the full record.

---

## 4. Versioning Strategy

Every schema carries a `schema_version` field following semantic versioning (MAJOR.MINOR.PATCH).

| Version Component | When to Increment |
|-------------------|-------------------|
| **MAJOR** | Breaking change: field removed, field renamed, field type changed, required field semantics altered. |
| **MINOR** | Additive change: new optional field added, new enum value added to an existing field. |
| **PATCH** | Documentation or description change only. No structural change to the schema. |

**Rules:**

- At MVP launch, all schemas start at `"1.0.0"`.
- Schema version is checked at deserialization time. A version mismatch raises a clear error reporting the expected version versus the actual version found in the file.
- A schema migration guide must be written for any MAJOR version bump. The guide must include before/after examples and a mechanical transformation procedure.
- Schema versions are independent per record type. `CanonicalMaterial` may be at `1.2.0` while `WorkflowResult` is still at `1.0.0`.
- MINOR version bumps must be backward-compatible: code written for `1.0.0` must be able to read a `1.1.0` record (ignoring unknown fields). Code written for `1.1.0` must handle the absence of fields added in `1.1.0` (by using documented defaults).
- The `schema_version` field is always the first field in serialized JSON output for quick identification.

---

## 5. Caching Strategy

### What Is Cached

- **Materials Project API responses**: structures, metadata, energies, and any other data retrieved via the `mp-api` client.
- **Cache key format**: `{mp_id}_{api_fields_hash}` where `api_fields_hash` is the SHA-256 hex digest of the sorted, comma-separated list of field names requested from the API.

### Cache Rules

| Rule | Detail |
|------|--------|
| **Storage location** | `artifacts/cache/mp/` |
| **Default TTL** | 30 days (configurable via `cache.ttl_days` in project configuration) |
| **Invalidation** | Manual via `cathodescope cache clear` command, or automatic time-based expiry |
| **Provenance logging** | Cache hits are recorded in the `ProvenanceRecord` of the consuming operation, so downstream consumers know whether data was cached or freshly retrieved |
| **Concurrency** | Cache writes use atomic file operations (write to temp file, then rename) to avoid partial reads |

### What Is NOT Cached

| Data Type | Reason |
|-----------|--------|
| **MACE relaxation results** | Depend on MACE model version and relaxation configuration. Stored as immutable workflow artifacts with full provenance, which serves the same purpose as caching while maintaining reproducibility. |
| **Reports** | Always regenerated from underlying structured data. Caching would create a stale-report risk. |
| **Benchmark results** | Always represent fresh runs. Caching would undermine the purpose of benchmarking. |

### Why Cache MP but Not Relaxation

- MP API calls are network-dependent and subject to rate limits. The underlying data rarely changes for stable database entries.
- Relaxation results depend on the MACE model version, relaxation parameters (force threshold, max steps, optimizer), and input structure. Storing them as immutable workflow artifacts with full provenance captures all of these dependencies explicitly, which is superior to a cache-key approach for computational results.

---

## 6. Immutability Rules

| Rule | Description |
|------|-------------|
| **Artifacts are write-once** | Once a workflow run completes and artifacts are written, they are never modified. A new run creates entirely new artifacts with new IDs. |
| **Provenance is append-only** | `ProvenanceRecord` instances are never edited after creation. |
| **Config snapshots are frozen** | The `config_snapshot` in provenance captures the exact configuration at run time. Subsequent configuration changes do not affect stored artifacts. |
| **Benchmark history is append-only** | New benchmark runs create new `BenchmarkSummary` and `BenchmarkRow` records. Old runs are never overwritten. This enables regression tracking across software versions. |
| **Cache is the exception** | Cache entries may be invalidated (deleted) and re-fetched. Cache is explicitly not treated as an immutable artifact. It is a performance optimization only. |
| **Structure files are immutable** | `original.json`, `normalized.json`, and `relaxed.json` under a material directory are written once. A re-relaxation with different parameters creates a new workflow run with its own independent artifact set. |
| **Reports can be regenerated** | While stored reports are immutable once written, a new report can be generated from the same `WorkflowResult`. This creates a new `ReportRecord` with a new `report_id`, leaving the original report untouched. |

**Enforcement:**

- The artifact storage layer should set file permissions to read-only after writing.
- Any attempt to overwrite an existing artifact file must raise an `ArtifactError` rather than silently succeeding.
- Deletion of artifacts is an administrative operation that requires explicit confirmation and is logged.

---

## 7. What Must Be Stored (Completeness Checklist)

For every workflow run, the following must be persisted. Nothing is optional. Missing artifacts indicate a bug in the pipeline, not a design choice. For workflows that did not complete all steps (any status other than `success` or `partial_success`), the integrity check validates artifacts up to the last completed step only. Missing artifacts after the failure point are expected and do not indicate a pipeline bug.

- [ ] **Raw input** -- formula, MP ID, or structure file as provided by the user
- [ ] **Canonical material record** -- `CanonicalMaterial` JSON with resolved structure and metadata
- [ ] **All intermediate structures** -- `original.json`, `normalized.json`, `relaxed.json`
- [ ] **Full workflow result** -- `WorkflowResult` JSON with all `StepResult` entries
- [ ] **Provenance at every level** -- workflow-level, step-level, and material-level `ProvenanceRecord` instances
- [ ] **Configuration snapshot** -- MACE model version, relaxation parameters, convergence thresholds, comparison tolerances
- [ ] **Software versions** -- Python, pymatgen, ASE, MACE, mp-api, numpy, and any other dependency used in computation
- [ ] **Report** -- both `report.json` (machine-readable `ReportRecord`) and `report.md` (human-readable Markdown)
- [ ] **Benchmark row** -- `BenchmarkRow` JSON, if the run is part of a benchmark execution
- [ ] **All warnings and errors** -- captured in `StepResult.warnings`, `StepResult.error`, and `WorkflowResult.status`

**Verification:** A post-run integrity check should confirm that every item in this checklist — up to and including the last completed workflow step — has a corresponding file on disk. Artifacts for steps that never executed (i.e., steps after a failure point) are not expected and their absence does not constitute an integrity failure. If any artifact that should exist (given the steps that completed) is missing, the workflow status must be downgraded to `hard_failure` and the missing artifact must be logged as an `ArtifactError`.

Cross-reference: `architecture.md` Artifact/Provenance Store component.

---

## Cross-Reference Index

| Topic | Related Document |
|-------|-----------------|
| System architecture and component design | `architecture.md` |
| Extension-first design rules (ToolResult contract, no free-form deps) | `architecture.md` |
| Evidence types and validity ladder | `scientific_validity_matrix.md` |
| Benchmark metric definitions and failure categories | `benchmark_spec.md` |
| Canonical Material Model component | `architecture.md` |
| Workflow Engine design | `architecture.md` |
| Reporting Layer design | `architecture.md` |
| Artifact/Provenance Store component | `architecture.md` |
