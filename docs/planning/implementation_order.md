# CathodeScope Implementation Order

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active — Implementation Planning Document
**Cross-References**: `master_plan.md` (Section 11, phase roadmap), `architecture.md` (Diagram 3, Section 9), `artifact_schema.md` (data records), `benchmark_spec.md` (benchmark criteria)

---

## 1. Guiding Principle

The implementation order follows the data flow of the system. Each step depends on the previous ones being complete. This is not an arbitrary ordering — it is dictated by information dependencies.

```
Input --> Process --> Validate --> Store --> Report --> Benchmark --> Orchestrate --> Extend
```

Cross-reference: `master_plan.md` Section 11.

---

## 2. Strict Build Order

### Step 1: Project Scaffolding and Models

**Phase**: 1 (MVP-0)
**Files**:
```
pyproject.toml
cathodescope/__init__.py
cathodescope/config/__init__.py
cathodescope/config/defaults.py
cathodescope/config/settings.py
cathodescope/models/__init__.py
cathodescope/models/material.py        # CanonicalMaterial, NormalizedQuery
cathodescope/models/results.py         # WorkflowResult, StepResult, ToolResult, ErrorRecord
cathodescope/models/provenance.py      # ProvenanceRecord
cathodescope/models/reports.py         # ReportRecord, ReportSection
tests/unit/test_models.py
```

**Rationale**: Every subsequent module depends on having standard data models (`architecture.md` Diagram 3: "models/material.py <-- depended on by everything below"). Without pydantic models for `CanonicalMaterial`, `ToolResult`, `WorkflowResult`, `ProvenanceRecord`, and `ErrorRecord`, no tool can return structured results and no artifact can be stored.

**What to mock**: Nothing — these are pure data definitions.

**Acceptance**: All model classes instantiate with valid data, reject invalid data, and serialize to/from JSON correctly. Tests pass.

**Dependencies**: None. This is the foundation.

---

### Step 2: Configuration System

**Phase**: 1
**Files**:
```
cathodescope/config/defaults.py        # Default parameter values
cathodescope/config/settings.py        # Config loading and validation
tests/unit/test_config.py
tests/fixtures/test_config.json
```

**Rationale**: Tools need configuration (fmax thresholds, tolerances, model paths) before they can execute. Defaults must be defined before any tool is written (`architecture.md` Sections 4.4.3, 4.4.4, 4.4.5).

**What to mock**: Nothing.

**Acceptance**: Config loads defaults, merges JSON overrides, validates with pydantic. Missing MP API key raises a clear error.

**Dependencies**: Step 1 (models for config validation).

---

### Step 3: MP Client and Structure Retrieval

**Phase**: 1
**Files**:
```
cathodescope/tools/__init__.py
cathodescope/tools/mp_client.py
tests/unit/test_mp_client.py
tests/fixtures/mp_responses/
  mp-22526.json                        # Cached LiCoO2 response
  mp-19017.json                        # Cached LiFePO4 response
  mp-18767.json                        # Cached LiMn2O4 response
```

**Rationale**: You need a structure to work with. Materials Project is the source. The client must exist before any processing can begin (`master_plan.md` Section 11, Step 3).

**What to mock**: MP API responses. Cache real responses as JSON fixtures for offline testing. Unit tests never hit the live API.

**Acceptance**: Client retrieves LiCoO2 structure by mp-id and by formula. Returns a `ToolResult` with `evidence_type: "A-retrieved"`. Cached responses work offline. Rate limiting and error handling tested with mock failures.

**Dependencies**: Steps 1-2 (models, config for API key and cache settings).

---

### Step 4: Input Resolver

**Phase**: 1
**Files**:
```
cathodescope/tools/input_resolver.py   # (or inline in workflow)
tests/unit/test_input_resolver.py
```

**Rationale**: The resolver converts raw user input (formula or mp-id) to a `NormalizedQuery`. This is Step 0 in the workflow (`architecture.md` Section 4.3: "Step 0: resolve_input --> NormalizedQuery").

**What to mock**: MP Client (for formula-to-mp_id resolution).

**Acceptance**: "LiCoO2" resolves to `NormalizedQuery` with formula, reduced_formula, and mp_id. "mp-22526" resolves similarly. Invalid inputs raise `InputError` with clear messages.

**Dependencies**: Steps 1-3 (models, config, mp_client for resolution).

---

### Step 5: Structure Normalizer

**Phase**: 1
**Files**:
```
cathodescope/tools/structure_normalizer.py
tests/unit/test_structure_normalizer.py
```

**Rationale**: The retrieved structure must be in canonical form before relaxation. Different MP entries may have different cell conventions (`master_plan.md` Section 11, Step 4).

**What to mock**: Nothing — pymatgen's `SpacegroupAnalyzer` is deterministic and fast. Use fixture structures from Step 3.

**Acceptance**: LiCoO2 structure normalizes to conventional cell with R-3m space group preserved. Atom count consistency checked. Returns `ToolResult` with `evidence_type: "A-computed"`.

**Dependencies**: Steps 1, 3 (models, structure from MP client fixture).

---

### Step 6: Structure Relaxer

**Phase**: 1
**Files**:
```
cathodescope/tools/structure_relaxer.py
tests/unit/test_structure_relaxer.py
tests/fixtures/mace/                   # Mock MACE responses or small model for testing
```

**Rationale**: This is the primary computation. It requires a canonical, normalized structure to relax (`master_plan.md` Section 11, Step 5).

**What to mock for unit tests**: The MACE calculator. Create a mock calculator that returns pre-computed energies and forces for fixture structures. This allows testing the relaxation workflow logic (convergence checking, trajectory recording) without requiring a MACE model.

**What to use for integration tests**: Real MACE-MP-0 model with the LiCoO2 fixture structure. This validates that the MACE integration actually works.

**Acceptance (unit)**: Mock relaxation converges, trajectory recorded, `ToolResult` with convergence_info returned. Non-convergence scenario handled correctly (status: "warning").

**Acceptance (integration)**: LiCoO2 relaxes with MACE-MP-0 in < 100 steps, fmax < 0.01 eV/A, lattice parameters within 2% of MP reference.

**Dependencies**: Steps 1-2, 5 (models, config for MACE params, normalized structure).

---

### Step 7: Reference Comparator

**Phase**: 1
**Files**:
```
cathodescope/tools/reference_comparator.py
tests/unit/test_reference_comparator.py
```

**Rationale**: You need both a relaxed structure (Step 6) and a reference (Step 3) to compare. This is where scientific value is generated (`master_plan.md` Section 11, Step 6).

**What to mock**: Use fixture structures (one "relaxed" with small deviations, one "reference" from MP). No external dependencies to mock.

**Acceptance**: Lattice parameter deviations computed correctly. Volume deviation computed. Bond length comparison works for Li-O and Co-O pairs. Space group preservation check works. Returns `ToolResult` with `evidence_type: "A-compared"`.

**Dependencies**: Steps 1, 3, 6 (models, reference structure, relaxed structure).

---

### Step 8: Validation Layer

**Phase**: 1
**Files**:
```
cathodescope/validation/__init__.py
cathodescope/validation/structural.py
cathodescope/validation/convergence.py
cathodescope/validation/family_specific.py  # Stubs for MVP, expanded Phase 4
cathodescope/validation/evidence.py
cathodescope/tools/physics_validator.py
tests/unit/test_validation.py
tests/unit/test_physics_validator.py
```

**Rationale**: Now that comparison results exist, apply sanity checks and assign evidence labels. The validation layer checks outputs from scientific tools — it does not execute workflows (`architecture.md` Section 4.5).

**What to mock**: Use fixture comparison results. No external dependencies.

**Acceptance**: Bond length checks pass for valid structures and fail for collapsed structures. Evidence labels assigned correctly per `scientific_validity_matrix.md`. Returns `ToolResult` with checks list and evidence_labels.

**Dependencies**: Steps 1, 7 (models, comparison results to validate).

---

### Step 9: Artifact/Provenance Store

**Phase**: 1
**Files**:
```
cathodescope/provenance/__init__.py
cathodescope/provenance/store.py
tests/unit/test_store.py
```

**Rationale**: Now that you have outputs to store, build the storage layer. Storing artifacts retroactively is error-prone (`master_plan.md` Section 11, Step 7).

**What to mock**: Filesystem operations (use `tmp_path` pytest fixture for test isolation).

**Acceptance**: Artifacts written to correct directory structure per `artifact_schema.md` Section 3. Files are read-only after write. Overwrite attempts raise `ArtifactError`. Post-run integrity check confirms all expected files exist. Provenance records embedded correctly.

**Dependencies**: Steps 1 (models for all record types).

---

### Step 10: Report Generator

**Phase**: 1
**Files**:
```
cathodescope/tools/report_generator.py
cathodescope/reporting/__init__.py
cathodescope/reporting/json_report.py
cathodescope/reporting/markdown_report.py
tests/unit/test_report_generator.py
```

**Rationale**: With stored, reference-compared results, generate human-readable output. Reports consume artifacts; they do not produce them (`master_plan.md` Section 11, Step 8).

**What to mock**: Use fixture `WorkflowResult` and `CanonicalMaterial` objects.

**Acceptance**: JSON report contains all `ReportRecord` fields per `artifact_schema.md` Section 2.4. Markdown report follows evidence label format from `scientific_validity_matrix.md` Section 5. Section headers include `[Level A -- computed]` labels. Assessment paragraph summarizes evidence levels.

**Dependencies**: Steps 1, 8 (models, reference-compared workflow results).

---

### Step 11: Workflow Engine and structural_analysis Workflow

**Phase**: 1
**Files**:
```
cathodescope/workflows/__init__.py
cathodescope/workflows/base.py
cathodescope/workflows/engine.py
cathodescope/workflows/structural_analysis.py
tests/unit/test_engine.py
tests/integration/test_structural_analysis.py
```

**Rationale**: The engine sequences all the tools built in Steps 3-10. It is the orchestrator of the single-material pipeline. The `structural_analysis` workflow defines the MVP step sequence (`architecture.md` Section 4.3).

**What to mock (unit tests)**: All tools — test engine logic (step sequencing, error propagation, context passing) independently of tool implementations.

**What to use (integration test)**: Real tools with cached MP data and real MACE model. This is the LiCoO2 end-to-end acceptance test from `master_plan.md` Section 3.

**Acceptance**: LiCoO2 processes end-to-end: formula -> NormalizedQuery -> structure -> normalization -> relaxation -> comparison -> validation -> report -> artifacts. All artifacts stored per `artifact_schema.md`. Report has expected evidence labels per `scientific_validity_matrix.md`. No manual intervention required. Rerun produces same result category.

**Dependencies**: All previous steps (1-10).

---

### Step 12: Benchmark Runner

**Phase**: 2 (MVP-1)
**Files**:
```
cathodescope/benchmark/__init__.py
cathodescope/benchmark/registry.py
cathodescope/benchmark/runner.py
tests/unit/test_benchmark_runner.py
tests/integration/test_benchmark.py
```

**Rationale**: With a working single-material pipeline, run it across the benchmark set. The runner orchestrates existing pipeline components, it is not new science (`master_plan.md` Section 11, Step 9).

**What to mock (unit)**: Workflow engine — test runner logic (iteration, failure isolation, summary generation) independently.

**What to use (integration)**: Full pipeline for LiCoO2, LiFePO4, LiMn2O4.

**Acceptance**: 3 materials processed. At least 2/3 Full Success. Third at least Partial Success. `BenchmarkSummary` generated per `artifact_schema.md` Section 2.7. Per-material `BenchmarkRow` records stored. Failures classified per `benchmark_spec.md` categories.

**Sub-items**:
- **Benchmark regression comparison tool** (`benchmark/comparator.py`): Compares two `BenchmarkSummary` JSON files and reports status changes and metric deltas. Referenced as T-24b in `tdd_task_breakdown.md`. Required for Phase 2 gate criterion "Regression comparison possible."

**Dependencies**: Step 11 (working single-material pipeline).

---

### Step 13: CLI Interface

**Phase**: 3 (MVP-2)
**Files**:
```
cathodescope/app/__init__.py
cathodescope/app/cli.py
tests/unit/test_cli.py
```

**Rationale**: Wrap the pipeline in a usable command-line interface. The interface is a thin layer over existing components (`master_plan.md` Section 11, Step 10).

**What to mock**: Workflow engine for unit tests.

**Acceptance**: `cathodescope analyze LiCoO2` runs the structural_analysis workflow and produces a report. `cathodescope benchmark` runs the Phase 1 benchmark. Usage documented. 3-minute demo possible (`master_plan.md` Phase 3 gate).

**Dependencies**: Steps 11-12 (working pipeline and benchmark).

---

### Step 14: Phase 4 Hardening

**Phase**: 4 (Thesis-Core)
**Files**: All existing modules — enhanced, not new.
```
tests/                                 # Expanded test coverage
tests/test_import_rules.py            # Import-rule enforcement tests per dependency_graph.md Section 6
cathodescope/validation/family_specific.py  # Expanded family checks
docs/reproducibility_checklist.md      # New document
```

**Rationale**: Make the system thesis-worthy. "It works" becomes "it is defensible" (`master_plan.md` Phase 4).

**Acceptance**: Test coverage > 80% for core modules. Regression benchmark runs automatically. External reviewer can reproduce benchmark from documentation. All validity matrix wording rules enforced. Import-rule enforcement tests pass (`tests/test_import_rules.py` per `dependency_graph.md` Section 6).

**Dependencies**: Steps 1-13.

---

### Step 15: Agent Orchestration (DO NOT BUILD YET)

**Phase**: 5
**Dependencies**: Phase 4 gate passed. Deterministic stack hardened and benchmarked.

### Step 16: Advanced Extensions (DO NOT BUILD YET)

**Phase**: 6
**Dependencies**: Phase 4 or 5 complete.

---

## 3. Module Dependencies (from architecture.md Diagram 3)

```
models/*                       <-- everything depends on this
config/*                       <-- tools and workflows depend on this
    |
    v
tools/mp_client.py             depends on: models/*, config/*
tools/structure_normalizer.py  depends on: models/*
tools/structure_relaxer.py     depends on: models/*, config/*
tools/reference_comparator.py  depends on: models/*
tools/physics_validator.py     depends on: models/*, validation/*
tools/report_generator.py      depends on: models/*, reporting/*
    |
    v
validation/*                   depends on: models/*
reporting/*                    depends on: models/*
    |
    v
workflows/engine.py            depends on: models/*, tools/*, validation/*
workflows/structural_analysis  depends on: workflows/engine.py, tools/*
    |
    v
provenance/store.py            depends on: models/*
    |
    v
benchmark/runner.py            depends on: workflows/*, models/*, provenance/*
benchmark/registry.py          depends on: models/*
benchmark/comparator.py        depends on: models/*
    |
    v
app/cli.py                     depends on: workflows/*, benchmark/*
    |
    v
[future] agent/                depends on: workflows/engine.py, models/*
                               does NOT depend on: tools/* directly
```

**Critical rule**: `agent/` never imports from `tools/*` directly. The agent sequences workflows; it does not call scientific tools (`architecture.md` Diagram 3 annotation).

---

## 4. What to Mock First

| Mock Target | Purpose | When Real Implementation Used |
|-------------|---------|-------------------------------|
| MP API responses | Enable offline development and testing. Avoid rate limits. | Integration tests may optionally hit live API; all CI uses cached fixtures. |
| MACE calculator | Enable unit testing of relaxation workflow logic without a model. | Integration tests use real MACE-MP-0. |
| Filesystem (for store tests) | Isolate tests using `tmp_path`. | All real runs use the actual `artifacts/` directory. |
| Workflow engine (for benchmark runner tests) | Test runner logic independently of tools. | Integration tests use real engine. |

---

## 5. Scientific Verification Before Integration

The following must be scientifically verified before being wired into the workflow engine:

| Component | Validation Required | Reference |
|-----------|-------------------|-----------|
| Structure normalizer | Space group preserved, atom count consistent | pymatgen conventions |
| Structure relaxer | LiCoO2 lattice params within 2% of MP | `benchmark_spec.md` Section 4 |
| Reference comparator | Deviation calculations verified against hand-computed values | Unit test with known inputs/outputs |
| Physics validator | Evidence labels match `scientific_validity_matrix.md` | Manual audit of label assignment |
| Report generator | Evidence label format matches `scientific_validity_matrix.md` Section 5 | Manual review of generated Markdown |

---

## 6. Do Not Build Yet

The following components are explicitly deferred per `master_plan.md` Section 4:

| Component | Earliest Phase | Reason for Deferral |
|-----------|---------------|---------------------|
| Agent orchestration | Phase 5 | Deterministic stack must pass Phase 4 gate first |
| Voltage estimation workflow | Phase 6 | Requires delithiated structure workflow |
| Stability proxy workflow | Phase 6 | Requires phase diagram data and energy referencing |
| Transport proxy workflow | Phase 6 | Requires NEB or equivalent, computationally expensive |
| Dynamical stability proxy | Phase 6 | Gamma-point phonon check is only a proxy |
| Candidate generation | Phase 6+ | Requires benchmarked known-material pipeline first |
| Web UI / API server | Phase 3 (minimal), Phase 7 (polish) | Core value is the pipeline, not the interface |
| Database-backed storage | Post-MVP | Local filesystem sufficient for 3 benchmark materials |
| Multi-agent planner/critic | Phase 5+ | Needs proven single-agent first |

**If you are tempted to build any of these early, re-read the identity test in `master_plan.md` Section 1.**

---

## Cross-Reference Index

| Topic | Related Document | Section |
|-------|-----------------|---------|
| Implementation order rationale | `master_plan.md` | Section 11 |
| Module dependency graph | `architecture.md` | Diagram 3 |
| Repository structure | `architecture.md` | Section 9 |
| MVP definition and acceptance test | `master_plan.md` | Section 3 |
| Phase gate criteria | `master_plan.md` | Sections 5-6 |
| Benchmark success criteria | `benchmark_spec.md` | Section 6 |
| Artifact directory layout | `artifact_schema.md` | Section 3 |

---

*Every step in this order traces back to `master_plan.md` Section 11. Skipping or reordering steps creates hidden dependencies and untested assumptions. Build in order. Test before moving on.*
