# CathodeScope System Architecture

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active -- Thesis-Critical Document
**Cross-References**: `master_plan.md` (scope boundaries, phase roadmap), `artifact_schema.md` (data schemas), `scientific_validity_matrix.md` (evidence levels), `benchmark_spec.md` (benchmark specification)

---

## 1. System Purpose and Scope

CathodeScope is a reproducible scientific workflow platform for benchmarked Li-ion cathode screening, with agent orchestration layered on top of deterministic, benchmarked workflows. The system analyzes known cathode materials, runs atomistic workflows, compares results against known references, and produces disciplined, evidence-labeled reports. The architectural north star: **the architecture supports the whole roadmap from day one, even though only part of it is implemented first.** Every component, interface boundary, and data contract documented here is designed so that future capabilities -- agent orchestration, voltage estimation, stability proxies, candidate generation -- plug into the existing structure through defined extension points, never by rewriting the core. The architecture is the contract between what exists today and what the system will become.

Cross-reference: `master_plan.md` for scope boundaries, phased roadmap, and the distinction between thesis-core claims and future extensions.

---

## 2. MVP Boundaries

The MVP boundary is a hard line. Everything inside it must be built, tested, and benchmarked before any extension work begins. Everything outside it must have a defined interface contract but zero implementation code.

### MVP architecture must support

- **Input Resolver** -- accepts formula strings and Materials Project IDs, produces a normalized query object
- **Canonical Material Model** -- the central data object representing a material throughout the entire pipeline
- **Workflow Engine** -- a deterministic executor that runs a single predefined workflow (`structural_analysis`)
- **6 MVP scientific tools**:
  - `mp_client` -- retrieves structures and metadata from the Materials Project API
  - `structure_normalizer` -- converts structures to canonical conventional cell form
  - `structure_relaxer` -- performs MACE-based atomic relaxation
  - `reference_comparator` -- compares relaxed structures against MP references
  - `physics_validator` -- applies sanity checks and assigns evidence labels
  - `report_generator` -- produces JSON and Markdown reports
- **Validation Layer** -- structural sanity checks, convergence checks, family-specific checks, evidence labeling
- **Artifact/Provenance Store** -- local filesystem storage with immutable, provenance-tracked artifacts
- **Reporting Layer** -- JSON (machine-readable) and Markdown (human-readable) report generation
- **Benchmark Layer** -- runs workflows across the benchmark material set, tracks results and regressions

### MVP architecture must leave room for (but not implement)

- **Agent Orchestration Layer** -- LLM-driven workflow selection and tool routing (Phase 5)
- **Natural-language input and structure file input** -- CIF/POSCAR file upload, material name lookup, free-form queries
- **Voltage / Stability / Dynamics tools** -- restricted voltage estimation (Level B), stability proxy (Level C), dynamical stability proxy (Level C), transport proxy (Level C)
- **Multi-material parallel execution** -- concurrent processing of multiple materials in a single workflow run
- **Database-backed artifact store** -- replacing the local filesystem store with a queryable database
- **Web UI** -- browser-based interface for workflow execution, report viewing, and benchmark dashboards

These deferred capabilities are documented here as named interface contracts. Their absence from the MVP codebase is intentional and must not be treated as missing features.

Cross-reference: `master_plan.md` Section 2 (End goal vs MVP), Section 4 (Out of Scope with Rationale).

---

## 3. Whole-System Architecture

### Diagram 1: Layer Architecture

```
User Input / Query
    |
    v
Input Resolver
    |
    v
Canonical Material Model
    |
    v
Workflow Engine  <-- deterministic execution graph
    |
    v
Scientific Tools
    |-- MP Client
    |-- Structure Normalizer
    |-- Structure Relaxer (MACE)
    |-- Reference Comparator
    |-- Physics Validator
    |-- Report Generator
    +-- [PHASE 6] Voltage / Stability / Dynamics / Candidate Gen
    |
    v
Validation Layer
    |
    v
Artifacts + Provenance Store
    |
    v
Reporting Layer
    |
    v
Benchmark Layer
    |
    v
[PHASE 5 — NOT BEFORE PHASE 4 GATE] Agent Orchestration Layer
```

> **Note:** This diagram shows logical layers and their dependency relationships, not execution order. For the actual step execution sequence, see Section 4.3 (structural_analysis workflow).

Each layer depends only on the layer directly above it and the shared data models. The Workflow Engine calls Scientific Tools; it does not contain scientific logic. The Validation Layer checks outputs from Scientific Tools; it does not execute workflows. The Agent Orchestration Layer (future) wraps the Workflow Engine; it does not bypass Validation or Provenance.

---

### Diagram 2: Single-Material Data Flow (MVP)

This diagram shows the complete flow for processing one material from formula input to final report, including the specific data types produced at each boundary.

```
Formula "LiCoO2"
    |
    v
[Input Resolver]
    --> NormalizedQuery{formula, reduced_formula, mp_id, source_type, raw_input, timestamp}
    |
    v
[MP Client]
    --> ToolResult{data: {structure, metadata, formation_energy, mp_id, is_stable, warnings}}
    |
    v
[Structure Normalizer]
    --> ToolResult{data: {normalized_structure, space_group, wyckoff_positions, conventional_cell}}
    |
    v
[Structure Relaxer]
    --> ToolResult{data: {relaxed_structure, final_energy, final_forces, convergence_info, trajectory, steps}}
    |
    v
[Reference Comparator]
    --> ToolResult{data: {lattice_deviations, volume_deviation, bond_length_comparison, coordination_comparison, symmetry_check}}
    |
    v
[Physics Validator]
    --> ToolResult{data: {checks: [...], evidence_labels: [...], overall_sanity: bool, warnings: [...]}}
    |
    v
[Report Generator]
    --> ToolResult{data: {report_json: ReportRecord, report_markdown: string, evidence_summary: {...}}}
    |
    v
[Artifact Store]
    --> all artifacts persisted with provenance under artifacts/{material_id}/ and artifacts/workflows/{run_id}/
    |
    v
[Benchmark Runner]
    --> BenchmarkRow{material_id, formula, family, workflow_name, status, metrics, failure_category, timestamp}
```

**Key invariant:** Every arrow in this diagram represents a structured data contract. No module passes free-form text to the next. Every intermediate result is persisted as an immutable artifact before the next step begins.

---

### Diagram 3: Module Dependency Graph

This graph shows which modules depend on which others. Arrows point from the dependent module to the module it depends on.

```
models/material.py          <-- depended on by everything below
models/results.py           <-- depended on by everything below
models/provenance.py        <-- depended on by everything below
    |
    +----------------------------------------------+
    |                                              |
    v                                              v
config/settings.py                          config/defaults.py
    |
    v
tools/mp_client.py          depends on: models/*, config/*
    |
    v
tools/structure_normalizer.py   depends on: models/*
    |
    v
tools/structure_relaxer.py      depends on: models/*, config/* (MACE config)
    |
    v
tools/reference_comparator.py   depends on: models/*
    |
    v
tools/physics_validator.py      depends on: models/*, validation/*
    |
    v
tools/report_generator.py       depends on: models/*, reporting/*
    |
    +----------------------------------------------+
    |                                              |
    v                                              v
validation/structural.py                    validation/convergence.py
validation/family_specific.py               validation/evidence.py
    |                                              |
    +----------------------------------------------+
    |
    v
workflows/engine.py             depends on: models/*, tools/*, validation/*
workflows/structural_analysis.py    depends on: workflows/engine.py, tools/*
    |
    v
provenance/store.py             depends on: models/*
    |
    v
reporting/json_report.py        depends on: models/*
reporting/markdown_report.py     depends on: models/*, reporting/json_report.py
    |
    v
benchmark/runner.py             depends on: workflows/*, models/*, provenance/*
benchmark/registry.py           depends on: models/*

[PHASE 5 — NOT BEFORE PHASE 4 GATE] agent/   depends on: workflows/engine.py, models/*
                                does NOT depend on: tools/* directly
```

**Critical dependency rule:** The `agent/` module (future) depends on `workflows/engine.py` and `models/*`. It never imports from `tools/*` directly. The agent sequences workflows; it does not call scientific tools. This ensures the validation and provenance layers are never bypassed.

---

## 4. Component Specifications

### 4.1 Input Resolver

**Responsibility:** Accepts raw user input (formula string or Materials Project ID) and resolves it to a normalized, unambiguous query object.

**Input contract:**
- `formula: string` -- a chemical formula (e.g., `"LiCoO2"`, `"LiFePO4"`)
- `mp_id: string` -- a Materials Project identifier (e.g., `"mp-22526"`)
- Exactly one of `formula` or `mp_id` is required. Providing both is an error unless the `mp_id` is used as the authoritative source and the formula is used only for validation.

**Output contract:**
```
NormalizedQuery:
  formula: string              # resolved chemical formula
  reduced_formula: string      # reduced form (e.g., "LiCoO2")
  mp_id: string | null         # resolved MP ID, null if not yet resolved
  source_type: string          # "formula" | "mp_id"
  raw_input: string            # the original user-provided input, preserved verbatim
  timestamp: string            # ISO 8601 creation timestamp
```

**Error handling:**
- `InputError("unrecognized_formula")` -- formula cannot be parsed as a valid chemical composition
- `InputError("ambiguous_input")` -- formula matches multiple MP entries and no disambiguating information is provided
- `InputError("invalid_mp_id")` -- mp_id does not match the `mp-XXXXX` format
- `InputError("conflicting_input")` -- both formula and mp_id provided but they are inconsistent

**MVP scope:**
- Formula string input (parsed and validated as a chemical formula)
- MP ID string input (validated as `mp-XXXXX` format)
- Resolution of formula to MP ID via the Materials Project API

**Formula disambiguation algorithm:**
When a formula matches multiple MP entries:
1. Query MP for all entries matching the reduced formula.
2. Filter to entries with `is_stable == true`.
3. If exactly one stable entry remains, use it.
4. If multiple stable entries remain, select the one with lowest `energy_above_hull`.
5. If still ambiguous (tie in `energy_above_hull`), raise `InputError("ambiguous_input")` with the list of candidate MP IDs.
6. Log the selection rationale (number of candidates, filtering criteria, chosen entry) in provenance.

**Deferred:**
- Structure file input (CIF, POSCAR, XYZ)
- Material name lookup (e.g., "lithium cobalt oxide" to LiCoO2)
- Natural-language query parsing (e.g., "find me a layered oxide with high voltage")
- Batch input (multiple materials in a single query)

**Extension points:** New input types register as resolver plugins. Each plugin implements a `resolve(raw_input) -> NormalizedQuery` interface. The Input Resolver dispatches to the appropriate plugin based on input format detection. Adding a new input type (e.g., CIF file) requires writing one plugin class; no changes to the Input Resolver core.

---

### 4.2 Canonical Material Model

**Responsibility:** Serves as the central, immutable data object representing a single material throughout the entire pipeline -- from input resolution through benchmarking.

**Input contract:** Constructed from a `NormalizedQuery` and the data retrieved by the MP Client. Not created directly by users.

**Output contract:**
```
CanonicalMaterial:
  schema_version: string          # semver, e.g., "1.0.0"
  material_id: string             # UUID, internal to CathodeScope
  formula: string                 # e.g., "LiCoO2"
  reduced_formula: string         # e.g., "LiCoO2"
  family: string                  # enum: "layered_oxide" | "olivine_polyanion" | "spinel" | "other"
  structure: object               # pymatgen Structure serialized via as_dict()
  source: string                  # enum: "materials_project" | "user_upload" | "generated"
  mp_id: string | null            # e.g., "mp-22526"
  identifiers: object             # additional IDs: {"icsd": "...", "doi": "...", ...}
  benchmark_tags: list[string]    # e.g., ["phase1", "layered_oxide"]
  workflow_eligibility: object    # e.g., {"structural_analysis": true, "voltage_estimate": false}
  created_at: string              # ISO 8601
  provenance: ProvenanceRecord    # nested provenance
```

**Immutability rule:** Once a `CanonicalMaterial` is created and persisted, it is never mutated. If any field needs to change (e.g., additional identifiers discovered, family reclassification), a new `CanonicalMaterial` record is created with a new `material_id` and the `parent_ids` in its provenance link back to the original. This ensures that all downstream artifacts referencing the original `material_id` remain consistent.

**Error handling:**
- `ValidationError("invalid_structure")` -- the provided structure fails basic structural sanity checks (negative volume, overlapping atoms)
- `ValidationError("unknown_family")` -- the material does not match any known cathode family classification rules
- `ArtifactError("serialization_failure")` -- the pymatgen Structure cannot be serialized to JSON

**MVP scope:**
- Construction from MP-retrieved data
- Family classification for layered oxides, olivines, and spinels
- Workflow eligibility determination for `structural_analysis`

**Deferred:**
- Construction from user-uploaded structure files
- Construction from generated/hypothetical structures
- Extended family classification (e.g., disordered rock salt, tavorite, NASICON)
- Multi-polymorph handling (same formula, different structures)

**Family classification rules:**

```
R-3m + LiMO2 composition → layered_oxide
Pnma + LiMPO4 composition → olivine_polyanion
Fd-3m + LiM2O4 composition → spinel
otherwise → other
```

These rules are implemented in a `classify_family(space_group, formula)` function. The `other` category is a catch-all for materials outside the three benchmark families.

**Factory function:**

```
create_canonical_material(query: NormalizedQuery, mp_response: ToolResult) -> CanonicalMaterial
```

This factory is the sole construction point for `CanonicalMaterial`. It is defined in `models/material.py` and called by the workflow adapter between step 1 (fetch) and step 2 (normalize). Field mapping:
- `material_id` <- `uuid4()`
- `formula` <- `query.formula`
- `reduced_formula` <- `query.reduced_formula`
- `family` <- `classify_family(mp_response.data.structure.space_group, query.formula)`
- `structure` <- `mp_response.data.structure`
- `source` <- `"materials_project"`
- `mp_id` <- `query.mp_id`
- `benchmark_tags` <- derived from family and benchmark material registry
- `workflow_eligibility` <- `{"structural_analysis": true}` (MVP default)
- `created_at` <- current ISO 8601 timestamp
- `provenance` <- constructed from mp_response.provenance and query metadata

**Extension points:** Family classification is implemented as a registry of classifier functions. Each classifier takes a pymatgen Structure and returns a family label or `None`. Adding a new family requires registering one classifier function. Workflow eligibility is similarly extensible: each new workflow registers its eligibility criteria.

Cross-reference: `artifact_schema.md` Section 2.1 (CanonicalMaterial record).

---

### 4.3 Workflow Engine

**Responsibility:** Deterministic executor that runs predefined workflow graphs, sequencing tool invocations, collecting results, and managing workflow-level state -- without containing any scientific logic.

**Input contract:**
- `workflow_name: string` -- the name of the workflow to execute (e.g., `"structural_analysis"`)
- `material: CanonicalMaterial` -- the material to process
- `config: WorkflowConfig` -- workflow-specific configuration (convergence thresholds, model parameters, etc.)

**Output contract:**
```
WorkflowResult:
  schema_version: string
  workflow_run_id: string          # UUID for this specific run
  workflow_name: string            # e.g., "structural_analysis"
  workflow_version: string         # e.g., "1.0.0"
  material_id: string              # references CanonicalMaterial.material_id
  status: string                   # "success" | "partial_success" | "soft_failure" | "hard_failure" | "infrastructure_failure"
  steps: list[StepResult]          # ordered list of step results
  started_at: string               # ISO 8601
  completed_at: string             # ISO 8601
  runtime_seconds: float           # wall-clock time
  config_snapshot: object          # full workflow configuration used
  provenance: ProvenanceRecord
```

**Execution model (MVP):**
- Sequential execution: steps run one after another in a defined order
- No parallelism needed for single-material processing
- Each step receives the accumulated result context from all preceding steps and appends its own output
- The engine passes the result context as a read-only typed container; tools cannot modify results from previous steps

**State management:**
- The engine maintains a `WorkflowContext` typed `@dataclass` that accumulates step results via its `step_results: dict[str, StepResult]` field
- Each step function signature is `step(context: WorkflowContext, config: StepConfig) -> StepResult`
- The engine appends each `StepResult` to the context before invoking the next step
- If a step needs data from a previous step, it reads from the context by step name

**Versioning:**
- Each workflow has a version string following semver (e.g., `"1.0.0"`)
- Changing the step sequence, adding a step, or removing a step increments the version
- Changing step-internal parameters (e.g., fmax threshold) does NOT increment the workflow version; it is captured in the `config_snapshot`
- The workflow version is recorded in every `WorkflowResult` for reproducibility

**Error handling:**
- If any step fails with a non-recoverable error, the engine records the failure point, stores all partial artifacts generated so far, and returns a `WorkflowResult` with `status: "hard_failure"`
- If a step fails with a recoverable error (e.g., borderline convergence), the engine records a warning and continues, setting `status: "soft_failure"` or `"partial_success"` depending on the severity
- The engine classifies errors using the error taxonomy (Section 6) and records an `ErrorRecord` in the failing `StepResult`
- The engine NEVER swallows errors silently. Every exception is caught, classified, and stored.

**MVP workflow -- `structural_analysis` (version 1.0.0):**
```
Step 0: resolve_input     --> NormalizedQuery
Step 1: fetch_structure   --> ToolResult (MP Client)
Step 2: normalize         --> ToolResult (Structure Normalizer)
Step 3: relax             --> ToolResult (Structure Relaxer)
Step 4: compare_reference --> ToolResult (Reference Comparator)
Step 5: validate          --> ToolResult (Physics Validator)
Step 6: generate_report   --> ToolResult (Report Generator)
```

**Critical design rule:** The Workflow Engine NEVER contains scientific logic. It sequences tools, passes data between them, handles errors, and records results. All domain knowledge lives in the scientific tools and the validation layer.

**Extension points:** New workflows register through a `WorkflowRegistry`, not by modifying engine code. The registry maps workflow names to workflow definitions (ordered lists of step specifications). Adding a new workflow (e.g., `voltage_estimate`) requires writing one workflow definition module and registering it. The engine code does not change.

```
WorkflowRegistry:
  register(workflow_name, workflow_definition, version)
  get(workflow_name) -> WorkflowDefinition
  list() -> list[WorkflowDefinition]
```

**Phase 1 note:** All five registries in the system (`WorkflowRegistry`, `NormalizationStrategyRegistry`, `ComparisonMetricRegistry`, `FamilyValidatorRegistry`, `SectionRegistry`) use direct function references in Phase 1 — simple dictionaries mapping names to callables. Formal plugin discovery frameworks (entry points, plugin directories, dynamic loading) are deferred to Phase 4. Of the five, only `WorkflowRegistry` is implemented as an explicit registry object in Phase 1 (because the Workflow Engine needs it at startup). The other four (`NormalizationStrategyRegistry`, `ComparisonMetricRegistry`, `FamilyValidatorRegistry`, `SectionRegistry`) use direct function calls in Phase 1 — they are only promoted to formal registries in Phase 4 when a second implementation of each strategy/metric/validator/section exists and runtime selection is required.

**Formal `WorkflowContext` definition:**

`WorkflowContext` is a typed `@dataclass` — not a free-form dictionary or mutable dict. Tools receive it as a read-only container; only the engine mutates `step_results`.

```
@dataclass
class WorkflowContext:  # read-only from tools; only engine appends to step_results
  material: CanonicalMaterial            # the material being processed
  normalized_query: NormalizedQuery      # the resolved input query
  step_results: dict[string, StepResult] # keyed by step_name, accumulated as steps complete
  config: object                         # workflow-level configuration snapshot
  workflow_run_id: string                # UUID for this run
  started_at: string                     # ISO 8601
```

**Construction note:** The engine creates the `WorkflowContext` before step 0 with `normalized_query` set to `None`. Step 0 (`resolve_input`) produces the `NormalizedQuery` in its `StepResult`. The engine updates `context.normalized_query` after step 0 completes, before passing the context to step 1. This means step 0's adapter function does not read `context.normalized_query` (it is `None` at that point); all subsequent steps can safely read it.

The `WorkflowContext` is a typed container — not a free-form dictionary. Each step reads prior results from `step_results` by step name (e.g., `context.step_results["fetch_structure"]`) and the engine appends new results after each step completes. The context is read-only from the perspective of tools; only the engine mutates it.

**Adapter pattern:** Workflow definition modules (e.g., `structural_analysis.py`) contain per-step adapter functions that (1) extract inputs from `context.step_results` and `context.config`, (2) call the underlying tool function with typed arguments, and (3) wrap the tool's return value into a `StepResult` written back to the context by the engine. This is the primary integration seam: tools never import `WorkflowContext` and have no knowledge of the workflow graph. Every tool can be unit-tested with direct inputs. Every adapter can be tested by constructing a minimal `WorkflowContext` stub.

**Status determination rules:** The final `WorkflowResult.status` is determined by the worst step outcome, using the following precedence (highest severity first):

| Priority | Status | Trigger |
|----------|--------|---------|
| 1 | `infrastructure_failure` | Any step fails due to environmental/system issues (network, disk, OOM, missing dependency) |
| 2 | `hard_failure` | Any step produces a non-recoverable scientific error (divergence, NaN, structure collapse) |
| 3 | `soft_failure` | Any step produces warnings requiring human review (symmetry break, borderline convergence) |
| 4 | `partial_success` | All steps complete but one or more metrics are outside ideal thresholds |
| 5 | `success` | All steps complete and all metrics are within ideal thresholds |

A single step at a higher severity level overrides all lower-severity outcomes. For example, if five steps succeed and one triggers `soft_failure`, the overall status is `soft_failure`.

**Important distinction:** `WorkflowResult.status` reflects pipeline execution outcomes only (step completion, crashes, warnings). The `BenchmarkRow.status` field is determined independently by the benchmark runner applying the formal threshold table from `benchmark_spec.md` Section 5 to the recorded metrics. These two status values may differ — for example, a workflow may complete successfully (`WorkflowResult.status: success`) but produce lattice deviations exceeding 2%, resulting in `BenchmarkRow.status: partial_success`. The benchmark runner must call `classify_benchmark_status(metrics)` independently of the engine-assigned workflow status.

Cross-reference: `artifact_schema.md` Section 2.2 (WorkflowResult and StepResult records), `benchmark_spec.md` Section 5 (benchmark classification).

---

### 4.4 Scientific Tools (6 MVP Tools)

All scientific tools share a common contract: every tool returns a `ToolResult` (Extension Rule 1). No tool returns a raw dict, bare value, or unstructured text.

```
ToolResult:
  status: string                   # "success" | "warning" | "error"
  evidence_type: string            # from validity ladder: "A-retrieved" | "A-computed" | "A-compared" | "B-restricted" | "C-proxy"
  data: object                     # tool-specific payload (always a JSON-serializable object)
  warnings: list[string]           # any warnings generated during execution
  provenance: ProvenanceRecord     # full provenance for this tool invocation
  artifacts: list[string]          # relative paths to files created by this tool
```

---

#### 4.4.1 mp_client

**Responsibility:** Retrieves crystal structure and metadata from the Materials Project API for a given material.

**Input contract:**
- `mp_id: string` -- Materials Project identifier (e.g., `"mp-22526"`)
- OR `formula: string` -- chemical formula to search for (returns the most stable entry)
- `fields: list[string]` -- optional list of API fields to retrieve (default: structure, formation_energy, is_stable, symmetry, band_gap)

**Output contract:**
```
ToolResult{
  status: "success",
  evidence_type: "A-retrieved",
  data: {
    structure: object,           # pymatgen Structure as_dict()
    metadata: {
      mp_id: string,
      formula_pretty: string,
      formation_energy_per_atom: float,
      energy_above_hull: float,
      is_stable: boolean,
      symmetry: object,          # space group info
      volume: float,
      density: float,
      nsites: integer
    },
    warnings: list[string]       # MP-reported warnings about this entry
  }
}
```

**Error handling:**
- `RetrievalError("mp_not_found")` -- the MP ID does not exist in the database
- `RetrievalError("api_timeout")` -- the MP API did not respond within the configured timeout
- `RetrievalError("rate_limit")` -- the MP API rate limit was exceeded
- `RetrievalError("api_version_mismatch")` -- the API response format has changed

**MVP scope:** Retrieve structure and core metadata by mp_id or formula. Cache responses to minimize API calls.

**Deferred:** Batch retrieval, advanced query filters (by crystal system, element set, property range), handling of deprecated entries.

**Extension points:** The MP Client implements a `DataSource` interface. Future data sources (AFLOW, COD, ICSD) implement the same interface and register in a `DataSourceRegistry`.

---

#### 4.4.2 structure_normalizer

**Responsibility:** Converts a retrieved crystal structure to canonical form -- conventional standard cell with standardized setting -- to ensure consistent comparison across materials.

**Input contract:**
- `structure: pymatgen.Structure` -- the raw structure to normalize
- `symprec: float` -- symmetry tolerance in Angstrom (default: 0.1)

**Output contract:**
```
ToolResult{
  status: "success",
  evidence_type: "A-computed",
  data: {
    normalized_structure: object,  # pymatgen Structure as_dict() (conventional cell)
    space_group: {
      symbol: string,              # e.g., "R-3m"
      number: integer,             # e.g., 166
      crystal_system: string       # e.g., "trigonal"
    },
    wyckoff_positions: list[object] | null,  # list of {element, wyckoff_label, multiplicity, coordinates}; nullable. **Deferred to Phase 4**: returns null in Phase 1. Full Wyckoff extraction is implemented when symmetry-aware normalization strategies are added in Phase 4.
    transformation_matrix: object,    # the matrix used to convert primitive to conventional
    atom_count_before: integer,
    atom_count_after: integer
  }
}
```

**Error handling:**
- `ComputationError("normalization_failed")` -- pymatgen SpacegroupAnalyzer fails (degenerate cell, ambiguous symmetry)
- `ValidationError("atom_count_mismatch")` -- atom count changed unexpectedly during normalization (indicates a bug, not a material property)
- `ValidationError("space_group_changed")` -- space group differs between input and normalized output beyond the expected primitive-to-conventional transformation

**MVP scope:** Conventional cell standardization using pymatgen SpacegroupAnalyzer. Space group extraction. Wyckoff position extraction is deferred to Phase 4 (the field is present but returns null in Phase 1).

**Deferred:** Support for disordered structures, partial occupancy handling, magnetic ordering normalization.

**Extension points:** Normalization strategies are pluggable. The default strategy uses pymatgen's conventional cell algorithm. Alternative strategies (e.g., for specific crystal systems) register through a `NormalizationStrategyRegistry`.

---

#### 4.4.3 structure_relaxer

**Responsibility:** Performs MACE-based atomic relaxation of a crystal structure, optimizing atomic positions and lattice parameters to minimize total energy.

**Input contract:**
- `structure: pymatgen.Structure` -- the structure to relax (should be normalized)
- `relaxation_config: RelaxationConfig`:
  ```
  RelaxationConfig:
    fmax: float                # convergence threshold (default: 0.01 eV/Angstrom)
    max_steps: integer         # maximum optimizer iterations (default: 500)
    mace_model: string         # MACE model identifier (default: "MACE-MP-0")
    mace_model_path: string    # path to MACE model checkpoint
    optimizer: string          # ASE optimizer name (default: "FIRE")
    relax_cell: boolean        # whether to relax lattice parameters (default: true)
    filter_type: string        # ASE filter for cell relaxation (default: "FrechetCellFilter")
  ```

**Output contract:**
```
ToolResult{
  status: "success",
  evidence_type: "A-computed",
  data: {
    relaxed_structure: object,   # pymatgen Structure as_dict()
    final_energy: float,         # total energy in eV
    energy_per_atom: float,      # energy per atom in eV/atom
    final_forces: list[list[float]],  # forces on each atom [N x 3] in eV/Angstrom
    final_fmax: float,           # maximum force component on any atom
    convergence_info: {
      converged: boolean,        # whether fmax < threshold was achieved
      steps: integer,            # number of optimizer steps taken
      energy_history: list[float],  # energy at each step
      fmax_history: list[float]     # maximum force at each step
    },
    trajectory: list[object]     # optional: structure at each step (if trajectory logging enabled)
  }
}
```

**Error handling:**
- `ComputationError("mace_initialization_failed")` -- MACE model could not be loaded (missing checkpoint, incompatible version)
- `ComputationError("relaxation_diverged")` -- energy increased without bound or atoms moved to unphysical positions
- `ComputationError("non_convergence")` -- max_steps reached without achieving fmax threshold (status set to `"warning"`, not `"error"`, since partial results may be useful)
- `ComputationError("numerical_instability")` -- NaN or Inf in forces or energy
- `ValidationError("structure_collapse")` -- atoms overlap after relaxation (bond length < 1.0 Angstrom)
- `ValidationError("excessive_volume_change")` -- volume changed by more than 10% from initial structure

**MVP scope:** Full cell relaxation (positions + lattice) using MACE-MP-0 with ASE FIRE optimizer. Convergence tracking with energy and force histories.

**Deferred:** Fixed-cell relaxation (positions only), constrained relaxation (fix specific atoms), multi-model ensemble relaxation, GPU acceleration configuration.

**Extension points:** The relaxer implements a `Calculator` interface via ASE. Swapping the underlying potential (e.g., from MACE-MP-0 to a fine-tuned model, or to a different MLIP) requires only changing the calculator initialization. The relaxation workflow logic does not change.

---

#### 4.4.4 reference_comparator

**Responsibility:** Compares a relaxed structure against the Materials Project reference structure, quantifying deviations in lattice parameters, volume, bond lengths, coordination numbers, and symmetry.

**Input contract:**
- `relaxed_structure: pymatgen.Structure` -- the MACE-relaxed structure
- `reference_structure: pymatgen.Structure` -- the MP reference structure (normalized)
- `comparison_config: ComparisonConfig`:
  ```
  ComparisonConfig:
    lattice_tolerance_pct: float     # threshold for lattice parameter deviation (default: 2.0%)
    volume_tolerance_pct: float      # threshold for volume deviation (default: 5.0%)
    bond_cutoff: float               # neighbor-finding cutoff radius in Angstrom (default: 3.0)
    symprec: float                   # symmetry tolerance in Angstrom (default: 0.1)
  ```

**Output contract:**
```
ToolResult{
  status: "success",
  evidence_type: "A-compared",
  data: {
    lattice_deviations: {
      a_pct: float,                  # deviation in lattice parameter a (%)
      b_pct: float,                  # deviation in lattice parameter b (%)
      c_pct: float,                  # deviation in lattice parameter c (%)
      alpha_abs: float,              # deviation in angle alpha (degrees)
      beta_abs: float,               # deviation in angle beta (degrees)
      gamma_abs: float               # deviation in angle gamma (degrees)
    },
    volume_deviation: {
      relaxed_volume: float,         # in Angstrom^3
      reference_volume: float,       # in Angstrom^3
      deviation_pct: float           # percentage deviation
    },
    bond_length_comparison: list[{
      pair: string,                  # e.g., "Li-O", "Co-O"
      relaxed_mean: float,           # mean bond length in relaxed structure (Angstrom)
      reference_mean: float,         # mean bond length in reference structure (Angstrom)
      deviation_pct: float           # percentage deviation
    }],
    coordination_comparison: list[{  # deferred to Phase 4
      site: string,                  # e.g., "Li", "Co"
      relaxed_cn: float,             # coordination number in relaxed structure
      reference_cn: float,           # coordination number in reference structure
      match: boolean                 # whether coordination numbers agree
    }],
    symmetry_check: {
      relaxed_space_group: string,   # space group of relaxed structure
      reference_space_group: string, # space group of reference structure
      preserved: boolean,            # whether space group is preserved
      symprec_used: float            # tolerance used for symmetry detection
    }
  }
}
```

**Error handling:**
- `ComputationError("structure_mismatch")` -- relaxed and reference structures have incompatible compositions (different elements or stoichiometries)
- `ComputationError("neighbor_detection_failed")` -- bond length analysis failed due to empty neighbor lists (cutoff too small or structure severely distorted)
- `ValidationError("threshold_exceeded")` -- one or more deviations exceed the configured tolerance (recorded as a warning, not a fatal error -- the comparison still completes)

**MVP scope:** Lattice parameter deviation, volume deviation, aggregate bond length sanity check (mean M-O bond length comparison, not per-pair), space group preservation check. Coordination number comparison deferred to Phase 4. Per-pair bond length comparison (mapping individual bonds between relaxed and reference structures) is deferred to Phase 4.

**Deferred:** Coordination number comparison (deferred from MVP; no benchmark metric evaluates it), per-pair bond length comparison, atom-by-atom displacement analysis (mapping relaxed sites to reference sites), Rietveld-style profile comparison, angular distribution function comparison, detailed Wyckoff site analysis.

**Extension points:** Comparison metrics are implemented as a list of `ComparisonMetric` objects. Each metric has a `compute(relaxed, reference) -> MetricResult` method. Adding a new comparison metric (e.g., radial distribution function comparison) requires writing one metric class and registering it.

---

#### 4.4.5 physics_validator

**Responsibility:** Applies physical sanity checks to all preceding step results and assigns evidence labels from the scientific validity ladder.

**Input contract:**
- `workflow_context: WorkflowContext` -- the accumulated results from all preceding workflow steps
- `material: CanonicalMaterial` -- the material being analyzed
- `validation_config: ValidationConfig`:
  ```
  ValidationConfig:
    min_bond_length: float           # minimum allowed bond length in Angstrom (default: 1.0)
    max_bond_length: float           # maximum allowed bond length in Angstrom (default: 4.0)
    max_lattice_deviation_pct: float # maximum lattice param deviation for "pass" (default: 2.0)
    max_volume_deviation_pct: float  # maximum volume deviation for "pass" (default: 5.0)
    energy_monotonic_tolerance: float  # tolerance for energy monotonicity check in eV (default: 0.001)
  ```

**Output contract:**
```
ToolResult{
  status: "success",
  evidence_type: "A-compared",
  data: {
    checks: list[{
      check_name: string,           # e.g., "bond_length_sanity", "convergence_check", "symmetry_preservation"
      category: string,             # "structural" | "convergence" | "family_specific" | "comparison"
      passed: boolean,
      value: float | string | null, # the measured value
      threshold: float | string | null,  # the threshold it was checked against
      message: string               # human-readable description of the check result
    }],
    evidence_labels: list[{
      output_name: string,          # e.g., "relaxed_structure", "lattice_deviation_a"
      evidence_type: string,        # from validity ladder: "A-computed", "A-compared", etc.
      rationale: string             # why this evidence level was assigned
    }],
    overall_sanity: boolean,        # true if all critical checks passed
    sanity_flags: list[string]      # list of issues found (empty if all clean)
  }
}
```

**Error handling:**
- `ValidationError("critical_check_failed")` -- a non-negotiable sanity check failed (e.g., negative cell volume, bond length < 0.5 Angstrom)
- `ValidationError("evidence_label_conflict")` -- two labeling rules assign conflicting evidence types to the same output (indicates a bug in the labeling logic)

**MVP scope:** Structural checks (bond lengths, coordination numbers, atom overlap), convergence checks (fmax threshold, energy monotonicity), comparison threshold checks (lattice params, volume), evidence labeling for all Level A outputs.

**Deferred:** Family-specific checks (Li-layer spacing for layered oxides, tetrahedral site occupancy for spinels, channel blocking for olivines), cross-workflow consistency checks, statistical outlier detection across benchmark runs.

**Extension points:** Validation checks are implemented as a list of `ValidationCheck` objects. Each check has a `run(context, config) -> CheckResult` method. Family-specific checks register through a `FamilyValidatorRegistry` keyed by the `family` field of `CanonicalMaterial`. Adding a new check category requires writing one check class and registering it.

Cross-reference: `scientific_validity_matrix.md` for evidence level definitions and the decision flowchart.

---

#### 4.4.6 report_generator

**Responsibility:** Produces human-readable (Markdown) and machine-readable (JSON) reports from a completed workflow result and its associated canonical material.

**Input contract:**
- `workflow_result: WorkflowResult` -- the completed workflow result with all step results
- `material: CanonicalMaterial` -- the material that was analyzed
- `report_config: ReportConfig`:
  ```
  ReportConfig:
    include_trajectory: boolean      # whether to include relaxation trajectory in report (default: false)
    include_raw_data: boolean        # whether to embed raw data in Markdown report (default: false)
    evidence_label_format: string    # "inline" | "section_header" (default: "section_header")
  ```

**Output contract:**
```
ToolResult{
  status: "success",
  evidence_type: null,  # report generation is rendering, not scientific computation; no evidence label applies
  data: {
    report_json: ReportRecord,       # full structured report (see artifact_schema.md)
    report_markdown: string,         # rendered Markdown report text
    evidence_summary: {
      "A-retrieved": integer,        # count of Level A retrieved labels
      "A-computed": integer,         # count of Level A computed labels
      "A-compared": integer          # count of Level A compared labels
    }
  }
}
```

**Error handling:**
- `ArtifactError("template_rendering_failed")` -- Markdown template could not be rendered from the structured data
- `ArtifactError("schema_validation_failed")` -- the generated ReportRecord does not conform to the report schema
- `ComputationError("missing_step_data")` -- a required workflow step result is missing from the WorkflowResult

**MVP scope:** JSON report generation with all ReportRecord fields populated. Markdown report generation following the evidence label format defined in `scientific_validity_matrix.md` Section 5. Report sections: material summary, workflow steps, results, evidence labels, comparison tables, warnings, provenance summary.

**Deferred:** HTML report generation, PDF export, interactive visualizations, comparative multi-material reports, benchmark summary reports.

**Extension points:** Report sections are generated by `ReportSectionGenerator` objects. Each section generator produces one `ReportSection` from the workflow context. Adding a new report section (e.g., for a voltage workflow) requires writing one section generator and registering it in a `SectionRegistry`.

Cross-reference: `artifact_schema.md` Section 2.4 (ReportRecord), `scientific_validity_matrix.md` Section 5 (evidence label format in reports).

---

#### 4.4.7 Future Tools (Phase 5--6)

These tools are NOT implemented in the MVP. Detailed interface contracts will be specified during Phase 5--6 planning, based on the stable Phase 4 ToolResult contract.

- **voltage_workflow** (Phase 6): Computes energy difference between lithiated and delithiated structures; evidence Level B.
- **stability_workflow** (Phase 6): Estimates thermodynamic stability relative to competing phases using MP phase diagram data; evidence Level C.
- **dynamics_workflow** (Phase 6): Computes gamma-point phonon frequencies as a proxy for dynamical stability; evidence Level C.
- **candidate_generation_workflow** (Phase 6): Generates candidate materials matching family and composition constraints; evidence Level C.

---

### 4.5 Validation Layer

**Responsibility:** Applies sanity checks to all tool outputs and assigns evidence labels from the scientific validity ladder, ensuring no output leaves the system without explicit trustworthiness classification.

**Check categories:**

| Category | Checks | Thresholds |
|----------|--------|------------|
| **Structural** | Bond lengths within physical range, coordination numbers consistent with crystal chemistry, no atom overlap (minimum interatomic distance check) | No bonds < 1.0 Angstrom or > 4.0 Angstrom; overlap threshold 0.5 Angstrom |
| **Convergence** | fmax reached threshold, energy decreased monotonically (or within tolerance), relaxation completed within max_steps | fmax < configured threshold (default 0.01 eV/Angstrom); energy oscillation tolerance 0.001 eV |
| **Family-specific** | Layered oxide: Li-layer spacing within expected range, no Li/TM site mixing detected. Spinel: tetrahedral 8a site occupancy correct. Olivine: 1D channel geometry preserved, PO4 tetrahedra intact | Family-dependent; defined in validation configuration |
| **Comparison** | Lattice parameter deviation within threshold, volume deviation within threshold, space group preserved, bond lengths consistent with reference | Lattice params < 2%, volume < 5%, space group unchanged |

**Evidence labeling:** Every output passing through the validation layer receives a label from the validity ladder. The labeling rules are deterministic:

| Output Type | Evidence Label | Condition |
|-------------|---------------|-----------|
| Retrieved from MP | A-retrieved | MP API returned valid data |
| Normalized structure | A-computed | Normalization completed without errors |
| Relaxed structure | A-computed | Relaxation converged AND structural checks pass AND material belongs to a benchmarked cathode family (layered_oxide, olivine_polyanion, spinel). Non-benchmarked families receive B-restricted. |
| Lattice/volume deviation | A-compared | Comparison completed against valid reference |
| Sanity check result | A-compared | All checks executed with defined thresholds |
| Workflow summary | Inherits weakest | Contains only Level A constituents in MVP |

**Inheritance rule:** When multiple evidence levels contribute to a single summary or derived output, the output inherits the weakest constituent level. A summary combining Level A and Level B data is labeled Level B. A summary including any Level C data is labeled Level C.

Cross-reference: `scientific_validity_matrix.md` for the full property-by-property matrix and the evidence level decision flowchart.

---

### 4.6 Artifact/Provenance Store

**Responsibility:** Persists all inputs, outputs, configurations, and lineage metadata for every workflow run, ensuring full reproducibility and auditability.

**Storage backend (MVP):** Local filesystem under the `artifacts/` directory. The layout is deterministic: given an ID, the file path is computable without a database lookup.

```
artifacts/
  materials/{material_id}/
    canonical.json
    structures/
      original.json
      normalized.json
      relaxed.json
    provenance.json
  workflows/{workflow_run_id}/
    result.json
    steps/
      00_resolve.json
      01_fetch.json
      02_normalize.json
      03_relax.json
      04_compare.json
      05_validate.json
      # Note: Step 6 (generate_report) does NOT produce a step file here.
      # Report generation is a post-workflow assembly step; its artifacts
      # (report.json and report.md) are written to reports/{report_id}/ instead.
    provenance.json
  reports/{report_id}/
    report.json
    report.md
    provenance.json
  benchmarks/{benchmark_run_id}/
    summary.json
    rows/{material_id}.json
    provenance.json
  cache/mp/
    {mp_id}_{api_fields_hash}.json
```

**Immutability rules:**
- All artifacts are write-once. Once a workflow run completes and artifacts are written, they are never modified.
- The store sets file permissions to read-only after writing.
- Any attempt to overwrite an existing artifact raises an `ArtifactError`.
- Cache entries are the sole exception: they may be invalidated (deleted) and re-fetched.

**Provenance tracking:** Every artifact carries a nested `ProvenanceRecord` linking it to its inputs, configuration, software versions, parent artifacts, and the `git_commit` hash at runtime (null if not in a git repo or dirty working tree). The `parent_ids` field forms a directed acyclic graph (DAG) of artifact lineage.

**Error handling:**
- `ArtifactError("write_failure")` -- file write failed (disk full, permission denied)
- `ArtifactError("serialization_error")` -- data could not be serialized to JSON
- `ArtifactError("schema_version_mismatch")` -- attempting to read an artifact with an incompatible schema version
- `ArtifactError("integrity_check_failed")` -- post-run integrity check found missing artifacts

**MVP scope:** Local filesystem storage, JSON serialization, provenance tracking, post-run integrity verification.

**Deferred:** Database-backed storage (SQLite or PostgreSQL), artifact deduplication, remote storage (S3/GCS), artifact search and query API.

**Extension points:** The store implements a `StorageBackend` interface with `write(artifact_type, id, data)`, `read(artifact_type, id) -> data`, and `exists(artifact_type, id) -> bool` methods, where `artifact_type` is a `Literal["material", "workflow", "report", "benchmark", "cache"]` that determines the storage subdirectory. Swapping from filesystem to database requires implementing one backend class. All other code references the store through the interface.

Cross-reference: `artifact_schema.md` for complete schema definitions, directory layout, naming conventions, versioning strategy, caching strategy, and immutability rules.

---

### 4.7 Reporting Layer

**Responsibility:** Generates structured JSON reports (machine-readable, primary artifact) and Markdown reports (human-readable, derived from JSON) from completed workflow results.

**Report sections (MVP `structural_analysis` report):**

| Section | Content | Evidence Level |
|---------|---------|---------------|
| Material Summary | Formula, family, MP ID, source, identifiers | A-retrieved |
| Retrieved Reference Data | MP structure, lattice parameters, space group, formation energy | A-retrieved |
| Normalization Results | Conventional cell, space group confirmation, Wyckoff positions | A-computed |
| MACE Relaxation Results | Relaxed structure, convergence info, energy, forces | A-computed |
| Reference Comparison | Lattice deviations, volume deviation, bond lengths, coordination | A-compared |
| Physics Validation | Sanity checks, evidence labels, warnings | A-compared |
| Evidence Summary | Count of evidence labels by type, overall assessment | Inherits weakest |
| Provenance Summary | Software versions, configuration, timestamps, artifact paths | Metadata |

**Design rule:** The JSON report (`report.json`) is the primary artifact. It contains all structured data needed to reproduce the Markdown report. The Markdown report (`report.md`) is derived from the JSON report and adds formatting, section headers with evidence labels, and human-readable prose. If the two ever disagree, the JSON report is authoritative.

**Evidence label format in reports:** Every section header includes the evidence level in brackets (e.g., `[Level A -- computed]`). Every quantitative result includes its evidence type inline. The format follows the specification in `scientific_validity_matrix.md` Section 5.

**Note:** Report generation is a post-workflow assembly step, not a scientific computation step. It does not produce a `StepResult` file under `steps/`; the report artifacts (`report.json` and `report.md`) are written directly to the `reports/` directory. The report generator's `ToolResult` is used internally by the engine but is not persisted as a numbered step file. The step count in `WorkflowResult.steps` (7) exceeds the number of step files in the `steps/` directory (6). This is by design -- step 6 artifacts are stored under `reports/`, not `steps/`. The post-run integrity check must account for this difference.

Cross-reference: `artifact_schema.md` Section 2.4 (ReportRecord and ReportSection), `scientific_validity_matrix.md` Section 5 (evidence label formatting requirements).

---

### 4.8 Benchmark Layer

**Responsibility:** Runs workflows across the benchmark material set, tracks per-material results and aggregate statistics, and maintains regression history across software versions.

**Input contract:**
- `benchmark_name: string` -- the benchmark to run (e.g., `"phase1_structural_analysis"`)
- `material_set: list[CanonicalMaterial]` -- the materials to benchmark (from the benchmark registry)
- `workflow_name: string` -- the workflow to execute for each material
- `config: BenchmarkConfig` -- benchmark-specific configuration:
  ```
  BenchmarkConfig:
    workflow_config: object          # configuration passed to each workflow run
    parallel: boolean                # whether to run materials concurrently (default: false, MVP is sequential)
    continue_on_failure: boolean     # whether to continue to next material if one fails (default: true)
    output_dir: string               # directory for benchmark artifacts (default: "artifacts/benchmarks/")
    tags: list[string]               # tags for this benchmark run, e.g., ["phase1", "regression"]
  ```

**Output contract:**
```
BenchmarkSummary:
  schema_version: string
  benchmark_run_id: string
  benchmark_name: string
  materials_count: integer
  status_counts: object              # {"success": N, "partial_success": N, "soft_failure": N, "hard_failure": N, "infrastructure_failure": N}
  rows: list[string]                 # file paths to individual BenchmarkRow files
  started_at: string
  completed_at: string
  runtime_seconds: float
  provenance: ProvenanceRecord
```

**Benchmark material registry:** The set of benchmark materials is defined in a registry module, not hardcoded. Each material entry includes the material's formula, MP ID, expected family, and any benchmark-specific tags. The initial benchmark set is:

| Material | MP ID | Family | Phase |
|----------|-------|--------|-------|
| LiCoO2 | mp-22526 | layered_oxide | Phase 1 |
| LiFePO4 | mp-19017 | olivine_polyanion | Phase 1 |
| LiMn2O4 | mp-18767 | spinel | Phase 1 |

**Metrics tracked per material** (24 total, per `benchmark_spec.md` Section 4):
- Input resolution success/failure
- Structure retrieval success/failure
- Normalization success/failure
- Space group of input structure (informational)
- Relaxation convergence (yes/no, steps, final fmax, final energy)
- Lattice parameter deviations (a, b, c in %)
- Angle deviations (alpha, beta, gamma in degrees)
- Volume deviation (%)
- Symmetry preservation (yes/no, output space group)
- Symmetry tolerance used (`symprec_used`, informational)
- Bond length sanity (min/max bond length, pass/fail)
- Evidence labeling completeness
- Report generation success/failure
- Runtime in seconds (informational)
- Workflow version (informational)

**Failure classification:** Every non-success result is categorized:
- `retrieval_failure` -- MP API failure
- `convergence_failure` -- relaxation did not converge
- `validation_failure` -- physics checks failed
- `artifact_failure` -- artifact storage failed
- `unknown_failure` -- unclassified (indicates a gap in error handling)

**Regression tracking:** Benchmark results are append-only. New runs create new `BenchmarkSummary` records. Comparing summaries across runs reveals regressions (e.g., a material that previously succeeded now fails, or deviations that increased).

**Error handling:**
- Individual material failures do not abort the benchmark. Each material is processed independently; failures are recorded in the corresponding `BenchmarkRow`.
- The benchmark runner catches all exceptions per material, classifies them, and continues to the next material.
- A benchmark run with zero successes still completes and produces a `BenchmarkSummary` with all failures documented.

**MVP scope:** Sequential execution of one workflow across the benchmark set. Per-material result tracking. Aggregate summary generation.

**Deferred:** Parallel execution, statistical regression testing (automated pass/fail based on historical baselines), ablation studies, LLM-vs-scripted workflow comparison.

**Extension points:** New benchmark sets register through the `BenchmarkMaterialRegistry`. New workflows become available for benchmarking through the `WorkflowRegistry`. The benchmark runner code does not change when new materials or workflows are added.

Cross-reference: `benchmark_spec.md` for the full benchmark specification, metric definitions, and failure categories.

---

### 4.9 Agent Layer (Future -- Phase 5)

The Agent Layer will provide LLM-driven orchestration over the benchmarked workflow backend. Its design is deferred entirely to Phase 5, after the deterministic benchmark stack passes the Phase 4 gate. The core architectural constraint is that **the agent never owns scientific logic** — it selects and sequences workflows through the same Workflow Engine, Validation Layer, and Artifact Store that the deterministic pipeline uses. Detailed interface contracts, tool schemas, and interaction patterns will be specified in Phase 5 planning. No agent code or directory exists in the repository until Phase 5 begins.

Cross-reference: `master_plan.md` Phase 5 (Agent Orchestration).

---

## 5. I/O Contracts Summary Table

This table lists every inter-module boundary in the MVP, specifying the exact data types crossing each boundary.

| # | Source Module | Target Module | Input Type | Output Type | Error Type |
|---|---|---|---|---|---|
| 1 | User | Input Resolver | `string` (formula or mp_id) | `NormalizedQuery` | `InputError` |
| 2 | Input Resolver | MP Client | `NormalizedQuery` | `ToolResult{MPResponse}` | `RetrievalError` |
| 3 | MP Client | Structure Normalizer | `pymatgen.Structure` (from ToolResult.data) | `ToolResult{NormalizedStructure}` | `ComputationError`, `ValidationError` |
| 4 | Structure Normalizer | Structure Relaxer | `pymatgen.Structure` (normalized) + `RelaxationConfig` | `ToolResult{RelaxationResult}` | `ComputationError`, `ValidationError` |
| 5 | Structure Relaxer | Reference Comparator | `pymatgen.Structure` (relaxed) + `pymatgen.Structure` (reference) | `ToolResult{ComparisonResult}` | `ComputationError`, `ValidationError` |
| 6 | All preceding steps | Physics Validator | `WorkflowContext` + `CanonicalMaterial` | `ToolResult{ValidationResult}` | `ValidationError` |
| 7 | Physics Validator | Report Generator | `WorkflowResult` + `CanonicalMaterial` | `ToolResult{ReportRecord}` | `ArtifactError`, `ComputationError` |
| 8 | All tools | Artifact Store | `ToolResult` / `WorkflowResult` / `CanonicalMaterial` | File path (persisted artifact) | `ArtifactError` |
| 9 | Report Generator | Reporting Layer | `ReportRecord` | `report.json` + `report.md` (files) | `ArtifactError` |
| 10 | Workflow Engine | Benchmark Runner | `WorkflowResult` + `CanonicalMaterial` | `BenchmarkRow` | `ArtifactError` |
| 11 | Benchmark Runner | Artifact Store | `BenchmarkSummary` + `list[BenchmarkRow]` | File paths (persisted artifacts) | `ArtifactError` |

**Reading this table:** Row 4, for example, means that the Structure Normalizer produces a `ToolResult` containing a normalized `pymatgen.Structure`, which the Structure Relaxer accepts as input along with a `RelaxationConfig`. If the relaxer fails, it raises a `ComputationError` or `ValidationError`.

---

## 6. Error Handling Strategy

### Error Taxonomy

Every error in CathodeScope is classified into exactly one of five categories. These categories are exhaustive -- if an error does not fit, the taxonomy must be extended, not circumvented.

| Error Type | Scope | Examples |
|---|---|---|
| `InputError` | User-provided data is invalid or unresolvable | Unrecognized formula, malformed MP ID, ambiguous input, conflicting formula and mp_id |
| `RetrievalError` | External data source failure | MP API timeout, rate limit exceeded, MP ID not found, API response format changed, network failure |
| `ComputationError` | Scientific computation failure | Relaxation divergence, MACE model initialization failure, non-convergence, numerical instability (NaN/Inf), normalization failure |
| `ValidationError` | Computed result fails a sanity check | Bond length outside physical range, negative cell volume, evidence label conflict, threshold violation, structure collapse |
| `ArtifactError` | Storage or serialization failure | File write failure, JSON serialization error, schema version mismatch, read permission denied, integrity check failure |

### Error Record Structure

Every error is captured in an `ErrorRecord` (defined in `artifact_schema.md`):

```
ErrorRecord:
  error_type: string               # one of the five types above
  message: string                  # human-readable error description
  details: object | null           # structured error context (input data, config, stack trace)
  recoverable: boolean             # whether the workflow can continue past this error
```

### Error Handling Principles

**Principle 1: Every error must be classified and stored.** No error is swallowed silently. Every exception is caught at the Workflow Engine level, classified into the taxonomy, wrapped in an `ErrorRecord`, and stored in the corresponding `StepResult`. Unclassified exceptions are logged as `ComputationError` with the full stack trace in the `details` field, and an alert is recorded indicating a gap in error classification.

**Principle 2: Partial results are always saved.** The system does not discard work on failure. If a relaxation diverges at step 150, the 149 steps of trajectory data, the input structure, the configuration, and the partial forces are all persisted. The `WorkflowResult` records the failure point (`status: "hard_failure"`) with all completed steps intact.

**Principle 3: Errors are logged with full context.** Every `ErrorRecord` includes the input data that caused the error, the configuration in effect, and the complete stack trace. This enables post-hoc debugging without re-running the workflow.

**Principle 4: Error classification feeds into benchmark failure categories.** The benchmark runner uses the `error_type` field from `ErrorRecord` to populate the `failure_category` field of `BenchmarkRow`. This enables aggregate analysis of failure patterns across materials (e.g., "3 out of 5 spinel materials failed with `convergence_failure`").

**Principle 5: Recoverable vs. non-recoverable errors are explicit.** The `recoverable` field in `ErrorRecord` determines whether the Workflow Engine continues to the next step or terminates the workflow. Recoverable errors (e.g., borderline convergence) result in `"soft_failure"` or `"partial_success"` status. Non-recoverable errors (e.g., MACE initialization failure) result in `"hard_failure"` status.

Cross-reference: `artifact_schema.md` Section 2.2 (ErrorRecord definition, status definitions), `benchmark_spec.md` (failure category taxonomy).

---

## 7. Extension-First Design Rules

These five rules govern how CathodeScope grows. They are non-negotiable architectural constraints -- violations must be caught in code review and corrected before merging.

### Rule 1: Structured Result Objects

**Every tool returns a `ToolResult` with `status`, `evidence_type`, `data`, `warnings`, `provenance`, and `artifacts`.**

**Rationale:** A uniform result structure enables three critical capabilities:
1. **Uniform validation.** The Validation Layer can check any tool's output without tool-specific parsing logic. It reads `status`, inspects `data`, and assigns evidence labels -- all through the same interface.
2. **Uniform logging and provenance.** The Artifact Store persists every `ToolResult` identically. Provenance chains are built without tool-specific serialization.
3. **Agent consumption.** When the Agent Layer (Phase 5) is added, it receives `ToolResult` objects with a consistent schema. The agent does not need tool-specific parsing logic to understand results.

**Concrete guidance:**
- Every tool function must return a `ToolResult`, never a raw dict, bare value, tuple, or string.
- The `data` field is tool-specific but always a JSON-serializable dict. Its schema is documented in this architecture document (Section 4.4) and enforced by pydantic validation.
- The `evidence_type` field is mandatory and must be drawn from the validity ladder (`"A-retrieved"`, `"A-computed"`, `"A-compared"`, `"B-restricted"`, `"C-proxy"`).
- Tools that encounter errors return a `ToolResult` with `status: "error"` and an empty or partial `data` field, never by raising an unstructured exception.

Cross-reference: `artifact_schema.md` Section 2.3 (ToolResult record).

---

### Rule 2: No Free-Form Text Dependencies

**No downstream module parses free-form text from upstream. All inter-module communication uses structured data objects.**

**Rationale:** Free-form text dependencies create three categories of fragility:
1. **Brittle string-matching.** A module that parses "converged in 23 steps" from a log message breaks when the message format changes to "convergence achieved after 23 iterations."
2. **Undetectable breakage.** String-format changes do not produce type errors or schema validation failures -- they produce silent wrong answers.
3. **Agent incompatibility.** An LLM agent cannot reliably parse arbitrary free-form text from tools. Structured data objects give the agent machine-readable contracts.

**Concrete guidance:**
- Tool outputs are `ToolResult` objects with typed fields, not formatted strings.
- Log messages are for human debugging only. No module reads another module's log output to make decisions.
- Report text (Markdown) is derived from structured data (JSON report), never the other way around.
- If a developer is tempted to parse a string produced by another module, this is a signal that the producing module should expose that value as a typed field in its output contract.

---

### Rule 3: Named, Versioned Workflows

**Every workflow is a named graph with a version string. Changing the step sequence increments the version.**

**Rationale:** Named, versioned workflows enable three capabilities:
1. **Reproducibility.** Given a workflow name and version, the exact sequence of steps is deterministic. Re-running `structural_analysis` v1.0.0 on the same input with the same configuration produces the same result.
2. **Regression testing.** Benchmark results are tagged with the workflow version. When the workflow changes (new step added, step order modified), the version increments and benchmark results before and after the change are distinguishable.
3. **Provenance tracking.** Every `WorkflowResult` records the workflow name and version. This enables auditing: "this report was generated by `structural_analysis` v1.0.0, not v1.1.0."

**Concrete guidance:**
- Workflow definitions live in dedicated modules (e.g., `workflows/structural_analysis.py`), not inline in the engine.
- The workflow version follows semver: MAJOR for breaking changes (step removed, step order changed), MINOR for additive changes (optional step added), PATCH for documentation only.
- Changing configuration parameters (e.g., fmax threshold) does NOT increment the workflow version. Configuration changes are captured in the `config_snapshot` field of `WorkflowResult`.
- Every workflow is registered in the `WorkflowRegistry` by name and version. The engine retrieves the workflow definition from the registry at runtime.

---

### Rule 4: Plugin Interfaces for Extensions

**New workflows, tools, and input types plug in through registries and interfaces, not by modifying core logic.**

**Rationale:** CathodeScope will grow from 6 tools and 1 workflow (MVP) to potentially dozens of tools and multiple workflow families. If each addition requires modifying the Workflow Engine, Validation Layer, or Reporting Layer, core code will accumulate patches and special cases until it becomes unmaintainable. Plugin interfaces prevent this by defining stable contracts that extensions implement.

**Concrete guidance:**
- The `WorkflowRegistry` maps workflow names to workflow definitions. Adding a new workflow means writing one module and one registration call.
- The `DataSourceRegistry` maps source names to data retrieval implementations. Adding a new data source (e.g., AFLOW) means implementing the `DataSource` interface.
- The `FamilyValidatorRegistry` maps family names to family-specific validation logic. Adding a new cathode family means writing one validator class.
- The `ReportSectionRegistry` maps section types to section generators. Adding a new report section means writing one generator class.
- Core modules (engine, store, validation framework) have zero import dependencies on specific tools or workflows. They operate on interfaces and registries.

---

### Rule 5: Separate Workflow Families

**Unknown-material exploration is a separate workflow family, never mixed into the benchmark core.**

**Rationale:** The benchmark core's credibility depends on a clear trust boundary. Benchmark workflows process known materials with known references and produce Level A evidence. Exploration workflows process unknown or hypothetical materials where no reference exists and produce Level B or Level C evidence at best. Mixing these two families would contaminate the trust label: if the same workflow that produces benchmarked results also processes unknown materials, it becomes unclear which results carry which evidence level.

**Concrete guidance:**
- Benchmark workflows are registered with a `family: "benchmark"` tag. Exploration workflows are registered with `family: "exploration"`.
- The benchmark runner only executes workflows tagged `"benchmark"`. It never runs exploration workflows, even accidentally.
- Evidence labels for exploration workflows are capped at Level B (if the methodology has been benchmarked for the relevant property) or Level C (for novel methodologies).
- A workflow cannot be tagged as both `"benchmark"` and `"exploration"`. This is enforced at registration time.

**Phase 5 note:** When the Agent Layer is added, it must also respect family boundaries: an agent cannot promote an exploration result to Level A trust.

---

## 8. Technology Stack (MVP)

| Component | Technology | Version Constraint | Purpose |
|-----------|-----------|-------------------|---------|
| Language | Python | 3.11+ | Primary implementation language. Type hints mandatory throughout. |
| Structure manipulation | pymatgen | Latest stable | Crystal structure representation, symmetry analysis (SpacegroupAnalyzer), structure I/O, neighbor-finding. |
| Simulation interface | ASE (Atomic Simulation Environment) | Latest stable | Interface between pymatgen structures and the MACE calculator. Provides optimizers (FIRE, BFGS) and cell filters (FrechetCellFilter). |
| Interatomic potential | mace-torch (MACE-MP-0) | Pinned version (recorded in provenance) | Machine-learning interatomic potential for structure relaxation. Foundation model pre-trained on Materials Project DFT data. |
| Database access | mp-api | Latest stable | Materials Project REST API client. Retrieves structures, metadata, and energetics. |
| Data validation | pydantic | v2+ | Data model validation, serialization, and schema enforcement. All models defined as pydantic BaseModel subclasses. |
| Testing | pytest | Latest stable | Unit tests, integration tests, parameterized tests, fixtures. |
| Serialization | JSON | (standard library) | Artifact storage format. All artifacts are JSON files with 2-space indentation. |
| Reporting | Markdown | (string rendering) | Human-readable report format. Derived from JSON report data. |
| Configuration | pydantic v2+ models + JSON config files | (pydantic) | Configuration management. Defaults in code, overrides from JSON config files. |

**Version pinning:** All dependency versions are pinned in `pyproject.toml` and recorded in every `ProvenanceRecord`. The MACE model checkpoint version is especially critical: different checkpoints produce different energies and forces, making results non-reproducible if the checkpoint changes.

---

## 9. Repository Structure

```
cathodescope/
|
|-- docs/                                   # Project documentation (Phase 0 deliverables)
|   |-- subject_matter_expert_onboarding.md # Domain primer for engineers
|   |-- architecture.md                     # THIS DOCUMENT -- system blueprint
|   |-- master_plan.md                      # Phased roadmap, scope, success criteria
|   |-- scientific_validity_matrix.md       # Evidence levels, wording rules, validity ladder
|   |-- benchmark_spec.md                   # Benchmark materials, metrics, thresholds
|   +-- artifact_schema.md                  # Data schemas, directory layout, versioning
|
|-- cathodescope/                           # Main Python package
|   |-- __init__.py                         # Package initialization, version string
|   |
|   |-- config/                             # Configuration management
|   |   |-- __init__.py
|   |   |-- settings.py                     # Runtime configuration loading and validation
|   |   +-- defaults.py                     # Default parameter values for all tools and workflows
|   |
|   |-- models/                             # Pydantic data models (shared across all modules)
|   |   |-- __init__.py
|   |   |-- material.py                     # CanonicalMaterial, NormalizedQuery
|   |   |-- results.py                      # WorkflowResult, StepResult, ToolResult, ErrorRecord
|   |   |-- provenance.py                   # ProvenanceRecord
|   |   +-- reports.py                      # ReportRecord, ReportSection, BenchmarkRow, BenchmarkSummary
|   |
|   |-- workflows/                          # Workflow definitions and execution engine
|   |   |-- __init__.py
|   |   |-- engine.py                       # WorkflowEngine, WorkflowRegistry, WorkflowContext
|   |   |-- structural_analysis.py          # MVP workflow definition (step sequence)
|   |   +-- base.py                         # Base workflow interface (abstract class)
|   |
|   |-- tools/                              # Scientific tools (one module per tool)
|   |   |-- __init__.py
|   |   |-- mp_client.py                    # Materials Project API client with caching
|   |   |-- structure_normalizer.py         # Conventional cell normalization via pymatgen
|   |   |-- structure_relaxer.py            # MACE-based structure relaxation via ASE
|   |   |-- reference_comparator.py         # Relaxed-vs-reference structure comparison
|   |   |-- physics_validator.py            # Sanity checks and evidence labeling
|   |   +-- report_generator.py             # JSON and Markdown report generation
|   |
|   |-- validation/                         # Validation checks (used by physics_validator)
|   |   |-- __init__.py
|   |   |-- structural.py                   # Bond length, coordination, atom overlap checks
|   |   |-- convergence.py                  # fmax threshold, energy monotonicity checks
|   |   |-- family_specific.py              # Family-specific validators (layered, olivine, spinel)
|   |   +-- evidence.py                     # Evidence label assignment logic
|   |
|   |-- reporting/                          # Report rendering (used by report_generator)
|   |   |-- __init__.py
|   |   |-- json_report.py                  # ReportRecord construction from WorkflowResult
|   |   +-- markdown_report.py              # Markdown rendering from ReportRecord
|   |
|   |-- benchmark/                          # Benchmark execution and tracking
|   |   |-- __init__.py
|   |   |-- runner.py                       # Benchmark execution loop, failure handling
|   |   +-- registry.py                     # Benchmark material set definitions
|   |
|   |-- provenance/                         # Artifact storage and retrieval
|   |   |-- __init__.py
|   |   +-- store.py                        # Filesystem-backed artifact store (StorageBackend interface)
|   |
|   |   # agent/ — deferred to Phase 5; directory will be created at that time
|   |
|   +-- app/                                # CLI and application layer (added in Phase 3)
|                                           # Empty in MVP; directory exists for structure
|
|-- tests/                                  # Test suite
|   |-- unit/                               # Unit tests (one test file per source module)
|   |-- integration/                        # Integration tests (end-to-end workflow tests)
|   +-- fixtures/                           # Test fixtures (mock MP responses, reference structures, configs)
|
|-- scripts/                                # Utility scripts (benchmark runners, cache management)
|
|-- artifacts/                              # Runtime artifact storage (gitignored)
|                                           # Created at runtime; never committed to version control
|
+-- pyproject.toml                          # Project metadata, dependencies, build configuration
```

**Directory annotations:**

- **`docs/`** -- All Phase 0 documentation deliverables. These documents are written before any implementation code and serve as the authoritative specification.
- **`cathodescope/models/`** -- Shared data models used by every other module. This is the only package that every other package may import from. Models are pydantic BaseModel subclasses with strict validation.
- **`cathodescope/workflows/`** -- Contains the Workflow Engine (generic, tool-agnostic) and workflow definitions (tool-specific step sequences). The engine imports from `models/` only. Workflow definitions import from `tools/` to reference specific tool functions.
- **`cathodescope/tools/`** -- One module per scientific tool. Each tool is a standalone function or class that accepts typed inputs and returns a `ToolResult`. Tools import from `models/` and `config/` only; they do not import from each other.
- **`cathodescope/validation/`** -- Validation check implementations. These are pure functions that take data and return check results. They import from `models/` only.
- **`cathodescope/reporting/`** -- Report rendering logic. Separated from `tools/report_generator.py` to keep the tool module thin (the tool delegates to the reporting package).
- **`cathodescope/benchmark/`** -- Benchmark execution infrastructure. The runner iterates over materials, calls the Workflow Engine, collects results, and generates summaries.
- **`cathodescope/provenance/`** -- Artifact storage backend. In MVP, this is a filesystem implementation. The `StorageBackend` interface allows swapping to a database later.
- **`cathodescope/agent/`** -- Deferred to Phase 5. The directory will be created when agent implementation begins; it does not exist in the repository until then.
- **`cathodescope/app/`** -- Placeholder for Phase 3 (CLI/minimal application). Same rationale as `agent/`.
- **`tests/`** -- Test suite organized by scope. Unit tests mock all external dependencies (MP API, MACE). Integration tests run real workflows against fixture data. Fixtures include cached MP responses and pre-computed reference structures to enable offline testing.
- **`artifacts/`** -- Runtime storage for all workflow outputs. Gitignored because artifacts are large and regenerable. The directory structure within `artifacts/` follows the layout defined in `artifact_schema.md` Section 3.

---

## Cross-Reference Index

| Topic | Related Document | Section |
|-------|-----------------|---------|
| Project scope, phased roadmap, success criteria | `master_plan.md` | Sections 2, 7, 9 |
| Evidence levels, validity ladder, wording rules | `scientific_validity_matrix.md` | Sections 2, 3, 4 |
| Data record schemas, directory layout, versioning | `artifact_schema.md` | Sections 2, 3, 4 |
| Benchmark materials, metrics, failure categories | `benchmark_spec.md` | Full document |
| Domain primer for engineers | `subject_matter_expert_onboarding.md` | Full document |
| CanonicalMaterial schema | `artifact_schema.md` | Section 2.1 |
| WorkflowResult and StepResult schemas | `artifact_schema.md` | Section 2.2 |
| ToolResult schema | `artifact_schema.md` | Section 2.3 |
| ReportRecord schema | `artifact_schema.md` | Section 2.4 |
| ProvenanceRecord schema | `artifact_schema.md` | Section 2.5 |
| BenchmarkRow and BenchmarkSummary schemas | `artifact_schema.md` | Sections 2.6, 2.7 |
| Evidence label format in reports | `scientific_validity_matrix.md` | Section 5 |
| Caching strategy | `artifact_schema.md` | Section 5 |
| Immutability rules | `artifact_schema.md` | Section 6 |
| Error types and status definitions | `artifact_schema.md` | Section 2.2 |
| Risk register | `master_plan.md` | Section 10 |

---

*This document is the technical blueprint for CathodeScope. All implementation decisions must be consistent with the contracts, rules, and boundaries defined here. When a question arises during implementation that this document does not answer, the answer should be added here before proceeding with code.*
