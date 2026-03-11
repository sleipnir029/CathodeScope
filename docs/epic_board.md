# CathodeScope — Epic Board

**Version**: 1.0.0
**Last Updated**: 2026-03-11
**Status**: Active — Project Management Document
**Cross-References**: `planning/tdd_task_breakdown.md` (task definitions), `planning/master_plan.md` (phase definitions), `task_board.md` (task cards)

---

## Overview

Epics group the 32 implementation tasks (T-00 through T-30, plus T-08b and T-24b) into 10 logical units. Each epic represents a coherent deliverable or capability. Epics are ordered by dependency, not by priority — earlier epics must complete before later ones can start.

---

## E-01: Project Foundation

| Field | Value |
|-------|-------|
| **Epic ID** | E-01 |
| **Title** | Project Foundation |
| **Goal** | Establish an installable Python package with a working test runner, linting, and type checking. Create all placeholder files and directories per the repository skeleton. |
| **Why it matters** | Every subsequent task depends on having an importable package and a functioning test infrastructure. Without this, no code can be written or tested. |
| **Tasks** | T-00 |
| **Dependencies** | None (starting point) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | `pip install -e ".[dev]"` succeeds. `pytest` discovers tests. `ruff check` and `mypy` pass on all files. All placeholder directories exist. |

---

## E-02: Data Model Layer

| Field | Value |
|-------|-------|
| **Epic ID** | E-02 |
| **Title** | Data Model Layer |
| **Goal** | Define all pydantic data models that every other module depends on: provenance records, error/result types, material representations, report and benchmark schemas. |
| **Why it matters** | Models are the foundation layer — every tool, workflow, validation module, and storage module imports from `models/*`. Without stable, tested models, no downstream module can be written. |
| **Tasks** | T-01, T-02, T-03, T-04 |
| **Dependencies** | E-01 (project skeleton must exist) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | All 71 model unit tests pass. Every model serializes to JSON and deserializes back correctly. Invalid data is rejected by pydantic validation. No model imports from any other `cathodescope` package. |

---

## E-03: Configuration System

| Field | Value |
|-------|-------|
| **Epic ID** | E-03 |
| **Title** | Configuration System |
| **Goal** | Create the configuration infrastructure: default parameter values, JSON override loading, environment variable handling, and config validation. |
| **Why it matters** | Every scientific tool needs configuration (fmax thresholds, tolerances, API keys, model paths). Defaults must be defined before any tool can be written. |
| **Tasks** | T-05 |
| **Dependencies** | E-02 (T-01 for ProvenanceRecord used in config_snapshot) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | All 17 config tests pass. Settings load defaults when no file exists. JSON overrides merge correctly. Missing MP_API_KEY raises a clear error. Config snapshot can be embedded in provenance records. |

---

## E-04: Scientific Tools

| Field | Value |
|-------|-------|
| **Epic ID** | E-04 |
| **Title** | Scientific Tools |
| **Goal** | Build all scientific tools in the pipeline: MP client, input resolver, family classifier, structure normalizer, structure relaxer, and reference comparator. Each tool returns a `ToolResult` with evidence labeling. |
| **Why it matters** | These tools perform the actual scientific work — retrieving structures, normalizing cells, running MACE relaxations, and computing deviations. They are the core value of CathodeScope. |
| **Tasks** | T-07, T-08, T-08b, T-09, T-10, T-11 |
| **Dependencies** | E-02 (models), E-03 (config) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | All ~87 tool unit tests pass. MP fixtures captured for 3 benchmark materials. Normalizer preserves R-3m, Pnma, Fd-3m. Relaxer handles convergence, non-convergence, and error paths with mock calculator. Comparator computes correct deviations for hand-computed test cases. Family classifier correctly identifies all 3 benchmark families. Scientific review checkpoint passed for normalizer (T-09). |

---

## E-05: Validation & Evidence

| Field | Value |
|-------|-------|
| **Epic ID** | E-05 |
| **Title** | Validation & Evidence |
| **Goal** | Build the validation layer (structural checks, convergence checks, evidence label assignment) and the physics validator tool that wraps them into a `ToolResult`. |
| **Why it matters** | Evidence labels are mandatory on all outputs per the scientific validity matrix. The validation layer ensures results are physically plausible and correctly labeled. Without this, reports cannot carry evidence levels and the thesis claim of "evidence-labeled outputs" fails. |
| **Tasks** | T-12, T-13, T-14 |
| **Dependencies** | E-02 (models for check result types), E-03 (ValidationConfig) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | All 42 validation/evidence tests pass. Bond length checks detect collapsed and exploded structures. Convergence checks flag non-convergent relaxations. All 8 MVP evidence labels match `scientific_validity_matrix.md` exactly. Summary inheritance follows weakest-level rule. Physics validator combines all checks into a single `ToolResult`. Scientific review checkpoint passed for evidence labels (T-13). |

---

## E-06: Artifact Storage

| Field | Value |
|-------|-------|
| **Epic ID** | E-06 |
| **Title** | Artifact Storage |
| **Goal** | Build the artifact/provenance store: write/read artifacts, enforce directory layout per `artifact_schema.md`, ensure immutability, and provide integrity checking. |
| **Why it matters** | Reproducibility requires storing all inputs, outputs, parameters, and metadata. Without the store, provenance chains are broken and results cannot be audited or reproduced. |
| **Tasks** | T-06 |
| **Dependencies** | E-02 (all model types for serialization), E-03 (config for cache settings) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | All 17 store tests pass. Directory structure matches `artifact_schema.md` Section 3 exactly. Files are read-only after write. Overwrite attempts raise `ArtifactError`. Cache directory allows overwrites. Integrity check verifies all expected files exist. |

---

## E-07: Reporting Layer

| Field | Value |
|-------|-------|
| **Epic ID** | E-07 |
| **Title** | Reporting Layer |
| **Goal** | Build JSON report construction, Markdown rendering with inline evidence labels, and the report generator tool wrapper. |
| **Why it matters** | Evidence-labeled reports are a core thesis deliverable. The JSON report is the machine-readable artifact; Markdown is the human-readable output. Both must match the format specified in `scientific_validity_matrix.md` Section 5. |
| **Tasks** | T-15, T-16, T-17 |
| **Dependencies** | E-02 (ReportRecord, WorkflowResult), E-05 (evidence labels populated in validator output) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | All 32 reporting tests pass. JSON report contains all required sections with evidence labels. Markdown section headers include `[Level X -- sub-type]` format. No disallowed wording present. Report format matches `scientific_validity_matrix.md` Section 5 mock excerpt. Scientific review checkpoint passed for report wording (T-16). |

---

## E-08: Workflow Engine & Integration

| Field | Value |
|-------|-------|
| **Epic ID** | E-08 |
| **Title** | Workflow Engine & Integration |
| **Goal** | Build the workflow engine (tool-agnostic step sequencer), define the structural_analysis workflow, and run end-to-end integration tests on all 3 benchmark materials with real MACE. |
| **Why it matters** | The engine is the orchestrator that connects all tools into a pipeline. Integration tests with real MACE are the first real scientific computations and constitute the Phase 1 acceptance test. Without this, there is no pipeline — only disconnected tools. |
| **Tasks** | T-18, T-19, T-20, T-21 |
| **Dependencies** | E-04 (all scientific tools), E-05 (validation), E-06 (store), E-07 (reporting) |
| **Label** | MVP (Phase 1) |
| **Exit criteria** | All 46 engine/workflow/integration tests pass. LiCoO2 processes end-to-end without manual intervention. Lattice deviations < 2% for LiCoO2. At least 2 of 3 materials achieve Full Success. Artifacts stored correctly. Reports have expected evidence labels. Rerun produces same result category. Scientific review checkpoints passed for MACE accuracy (T-20) and pipeline completeness (T-20). |

---

## E-09: Benchmark Suite

| Field | Value |
|-------|-------|
| **Epic ID** | E-09 |
| **Title** | Benchmark Suite |
| **Goal** | Build the benchmark registry, runner, integration tests, and regression comparison tool. Run the full Phase 1 benchmark and verify it meets the 2/3 Full Success criterion. |
| **Why it matters** | Benchmarks are the foundation of trust. Without benchmarks, CathodeScope is just a script with no evidence that outputs mean anything. The benchmark runner produces the structured result table needed for thesis methodology. |
| **Tasks** | T-22, T-23, T-24, T-24b |
| **Dependencies** | E-08 (workflow engine and integration tests must pass), E-02 (BenchmarkRow, BenchmarkSummary models) |
| **Label** | MVP (Phase 2) |
| **Exit criteria** | All 35 benchmark tests pass. 2/3 materials achieve Full Success. Third at least Partial Success. All 24 metrics from `benchmark_spec.md` populated per material. Benchmark reproducible on rerun. Regression comparison tool detects status changes between runs. Scientific review checkpoint passed for benchmark results (T-24). |

---

## E-10: CLI & Hardening

| Field | Value |
|-------|-------|
| **Epic ID** | E-10 |
| **Title** | CLI & Hardening |
| **Goal** | Build the CLI interface, set up CI/pre-commit, enforce import rules, generate golden test outputs, create regression tests, and scaffold the agent module. Harden the system to thesis-core quality. |
| **Why it matters** | The CLI enables the 3-minute demo required by Phase 3. CI, import enforcement, and regression tests are required for Phase 4 thesis-core hardening. The agent scaffold ensures Phase 5 starts cleanly. |
| **Tasks** | T-25, T-26, T-27, T-28, T-29, T-30 |
| **Dependencies** | E-08 (workflow engine for CLI), E-09 (benchmark runner for CLI), all previous epics for hardening tasks |
| **Label** | MVP (Phase 3) / Thesis-Core (Phase 4) |
| **Exit criteria** | All 30 CLI/hardening tests pass. `cathodescope analyze LiCoO2` produces a report. `cathodescope benchmark` produces a summary. 3-minute demo completable. CI passes on push. Import rules enforced via AST inspection. Regression tests pass against golden outputs. `pytest --cov` shows >80% coverage for core modules. Agent module importable with no functionality. |

---

## Epic Dependency Graph

```
E-01 ──> E-02 ──> E-03
           │        │
           │        v
           ├──> E-04 (Scientific Tools)
           │        │
           ├──> E-05 (Validation & Evidence)
           │        │
           ├──> E-06 (Artifact Storage)
           │        │
           └──> E-07 (Reporting Layer)
                    │
                    v
               E-08 (Workflow Engine & Integration)
                    │
                    v
               E-09 (Benchmark Suite)
                    │
                    v
               E-10 (CLI & Hardening)
```

---

## Epic Status Summary

| Epic | Tasks | Status | Phase |
|------|-------|--------|-------|
| E-01 | 1 | Todo | 1 |
| E-02 | 4 | Todo | 1 |
| E-03 | 1 | Todo | 1 |
| E-04 | 6 | Todo | 1 |
| E-05 | 3 | Todo | 1 |
| E-06 | 1 | Todo | 1 |
| E-07 | 3 | Todo | 1 |
| E-08 | 4 | Todo | 1 |
| E-09 | 4 | Todo | 2 |
| E-10 | 6 | Todo | 3–4 |

---

*Each epic maps to a coherent deliverable. Complete epics in dependency order. For individual task details, see `task_board.md`.*
