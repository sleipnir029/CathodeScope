# CathodeScope — Task Board

**Version**: 1.0.0
**Last Updated**: 2026-03-11 (T-07 Done)
**Status**: Active — Project Management Document
**Cross-References**: `planning/tdd_task_breakdown.md` (authoritative source), `epic_board.md` (epic groupings), `task_sequence_summary.md` (execution order), `task_execution_rules.md` (how to work tasks)

---

## Preamble

### Status Legend

| Status | Meaning |
|--------|---------|
| **Todo** | Not started. Dependencies may or may not be met. |
| **In Progress** | Actively being worked on. |
| **Done** | All acceptance criteria met. Definition of Done satisfied. |
| **Blocked** | Cannot proceed due to external dependency or unresolved issue. |

### Priority Legend

| Priority | Meaning |
|----------|---------|
| **P0** | Critical path. Delays the entire MVP. Must be done first. |
| **P1** | High priority. Required for current phase gate but not on critical path. |
| **P2** | Medium priority. Required for a later phase or enables parallel work. |
| **P3** | Low priority. Nice to have within the current phase. |

### Size Legend

| Size | Estimated Hours | Meaning |
|------|-----------------|---------|
| **XS** | < 1 hour | Trivial — stub, placeholder, or minor addition |
| **S** | 1–2 hours | Small — single model, simple tool, or test-only task |
| **M** | 2–4 hours | Medium — tool with mocking, multi-file change |
| **L** | 4+ hours | Large — consider splitting per `task_execution_rules.md` Section 3 |

---

## Wave 0: Docs and Skeleton

---

### T-00: Project Scaffolding and Build Configuration

| Field | Value |
|-------|-------|
| **Task ID** | T-00 |
| **Epic** | E-01: Project Foundation |
| **Title** | Project Scaffolding and Build Configuration |
| **Description** | Create an installable Python package with all placeholder files, directories, test infrastructure, linting, and type checking. |
| **Why it exists** | Every subsequent task depends on an installable package and a working test runner. Nothing else can start without this. |
| **Dependencies** | None |
| **Size** | S |
| **Status** | Done |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `pyproject.toml`, `.gitignore`, `.pre-commit-config.yaml`, all `__init__.py` files, all empty placeholder source and test files, `tests/conftest.py`, `tests/test_import_rules.py` (placeholder) |
| **Tests required** | `test_package_importable()`, `test_all_subpackages_importable()` |
| **Acceptance criteria** | `pip install -e ".[dev]"` succeeds. `pytest tests/` discovers and runs tests (0 failures). `ruff check cathodescope/` passes. `mypy cathodescope/` passes. |
| **Scientific review** | No |
| **Completed** | 2026-03-11 |
| **Notes** | Skeleton created. `setuptools.build_meta` used (not `setuptools.backends.legacy` — not available in this environment). All 9 subpackages importable. 2/2 tests pass. ruff + mypy clean. |

---

## Wave 1: Core Models and Config

---

### T-01: ProvenanceRecord Model

| Field | Value |
|-------|-------|
| **Task ID** | T-01 |
| **Epic** | E-02: Data Model Layer |
| **Title** | ProvenanceRecord Model |
| **Description** | Implement the `ProvenanceRecord` pydantic model with all 17 fields per `artifact_schema.md` Section 2.5, plus a `create_provenance()` factory function. |
| **Why it exists** | `ProvenanceRecord` is embedded in every other data record. It must exist first so all other models can reference it. |
| **Dependencies** | T-00 |
| **Size** | S |
| **Status** | Done |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/models/provenance.py`, `tests/unit/test_models/test_provenance.py` |
| **Tests required** | 15 tests: creation, validation, serialization, deserialization, factory function, optional fields |
| **Acceptance criteria** | All 15 tests pass. `ProvenanceRecord.model_dump()` produces valid JSON. Round-trip via `model_validate()`. `create_provenance()` returns fully-populated record. |
| **Scientific review** | No |
| **Completed** | 2026-03-11 |
| **Notes** | 17 fields implemented: record_id, created_at, created_by, tool_name, tool_version, cathodescope_version, python_version, hostname, platform, workflow_run_id, step_name, elapsed_seconds, input_hash, output_hash, config_snapshot, notes, tags. `create_provenance()` auto-populates system fields. `sample_provenance` fixture added to conftest.py. ruff + mypy --strict clean. |

---

### T-02: ErrorRecord, ToolResult, StepResult, WorkflowResult Models

| Field | Value |
|-------|-------|
| **Task ID** | T-02 |
| **Epic** | E-02: Data Model Layer |
| **Title** | ErrorRecord, ToolResult, StepResult, WorkflowResult Models |
| **Description** | Implement the core result models: `ErrorRecord` (failure representation), `ToolResult` (universal tool return type), `StepResult` (workflow step record), and `WorkflowResult` (complete workflow execution record). |
| **Why it exists** | `ToolResult` is the universal return type for all tools. `ErrorRecord` is used by every failure path. All must exist before any tool is built. |
| **Dependencies** | T-01 |
| **Size** | M |
| **Status** | Done |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/models/results.py`, `tests/unit/test_models/test_results.py` |
| **Tests required** | 23 tests: ErrorRecord (5), ToolResult (9), StepResult (4), WorkflowResult (5) |
| **Acceptance criteria** | All 23 tests pass. Invalid enum values rejected. Full JSON round-trip for every model. |
| **Scientific review** | No |
| **Completed** | 2026-03-11 |
| **Notes** | ErrorRecord: 6 Literal error_types, details/source/traceback optional. ToolResult: status Literal["success","failure","partial"], embeds ProvenanceRecord, evidence_type str\|None for validity-matrix labels. StepResult: embeds ToolResult + timing. WorkflowResult: embeds list[StepResult] + top-level ProvenanceRecord, workflow_run_id auto UUID. All Literal enums via pydantic v2. No imports from tools/config. ruff + mypy --strict clean. |

---

### T-03: CanonicalMaterial and NormalizedQuery Models

| Field | Value |
|-------|-------|
| **Task ID** | T-03 |
| **Epic** | E-02: Data Model Layer |
| **Title** | CanonicalMaterial and NormalizedQuery Models |
| **Description** | Implement `CanonicalMaterial` (canonical material representation used by all pipeline tools) and `NormalizedQuery` (first object created in any pipeline run from user input). |
| **Why it exists** | Every tool and workflow depends on `CanonicalMaterial`. The `NormalizedQuery` is the first object in any pipeline run. Without these, no pipeline step can be written. |
| **Dependencies** | T-01 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/models/material.py`, `tests/unit/test_models/test_material.py` |
| **Tests required** | 16 tests: NormalizedQuery (6), CanonicalMaterial (10) |
| **Acceptance criteria** | All 16 tests pass. Invalid family/source values rejected. Pymatgen `as_dict()` structures round-trip through the model. |
| **Scientific review** | No |
| **Notes** | Store `structure` as `dict` with validator checking for `lattice` and `sites` keys. Do not create factory functions depending on MP client. |

---

### T-04: ReportRecord, ReportSection, BenchmarkRow, BenchmarkSummary Models

| Field | Value |
|-------|-------|
| **Task ID** | T-04 |
| **Epic** | E-02: Data Model Layer |
| **Title** | ReportRecord, ReportSection, BenchmarkRow, BenchmarkSummary Models |
| **Description** | Implement report and benchmark models to complete the full data model layer. `BenchmarkRow.metrics` must support all 24 metrics from `benchmark_spec.md` Section 4. |
| **Why it exists** | Completes the full model layer. Report and benchmark models are needed before the reporting and benchmark subsystems can be built. |
| **Dependencies** | T-01 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/models/reports.py`, `tests/unit/test_models/test_reports.py` |
| **Tests required** | 18 tests: ReportSection (3), ReportRecord (6), BenchmarkRow (4), BenchmarkSummary (5) |
| **Acceptance criteria** | All 18 tests pass. `BenchmarkSummary` rejects inconsistent `materials_count` / `status_counts` / `rows`. |
| **Scientific review** | No |
| **Notes** | Do not create rendering logic in models — models are pure data. `ReportRecord` includes `raw_user_input` field. |

---

### T-05: Configuration System

| Field | Value |
|-------|-------|
| **Task ID** | T-05 |
| **Epic** | E-03: Configuration System |
| **Title** | Configuration System |
| **Description** | Create pydantic config models (`RelaxationConfig`, `ComparisonConfig`, `ValidationConfig`, `ReportConfig`, `BenchmarkConfig`, `CacheConfig`), a top-level `CathodescopeSettings` model, defaults, JSON override merging, and environment variable handling. |
| **Why it exists** | Every tool needs configuration values (fmax thresholds, tolerances, API keys). Defaults must exist before any tool is written. |
| **Dependencies** | T-01 |
| **Size** | M |
| **Status** | Done |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/config/defaults.py`, `cathodescope/config/settings.py`, `tests/unit/test_config/test_defaults.py`, `tests/unit/test_config/test_settings.py`, `tests/fixtures/configs/default_config.json`, `tests/fixtures/configs/strict_config.json` |
| **Tests required** | 17 tests: defaults (8), settings (9) |
| **Acceptance criteria** | All 17 tests pass. Settings load defaults when no config file. JSON overrides merge. Missing MP_API_KEY raises clear error. |
| **Scientific review** | No |
| **Completed** | 2026-03-11 |
| **Notes** | Default values: fmax=0.01 eV/Å, max_steps=500, lattice_tolerance=2.0%, volume_tolerance=5.0%, min_bond=1.0 Å, max_bond=4.0 Å. MP_API_KEY from env var via CathodescopeSettings.load(). pydantic gt/ge constraints enforce validity. 6 sub-config models + CathodescopeSettings. strict_config.json fixture has fmax=0.005, lattice_tol=1.0%, vol_tol=2.0%. |

---

## Wave 2: Scientific Workflow Core

---

### T-06: Artifact / Provenance Store

| Field | Value |
|-------|-------|
| **Task ID** | T-06 |
| **Epic** | E-06: Artifact Storage |
| **Title** | Artifact / Provenance Store |
| **Description** | Implement `ArtifactStore` class with write/read/exists/verify_integrity methods. Directory layout per `artifact_schema.md` Section 3. File immutability enforcement. Cache exceptions. |
| **Why it exists** | The store must exist before integration testing so workflow results can be persisted. Required by the workflow engine and benchmark runner. |
| **Dependencies** | T-02, T-04, T-05 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/provenance/store.py`, `tests/unit/test_provenance/test_store.py` |
| **Tests required** | 17 tests: write/read for each artifact type, directory structure, read-only enforcement, overwrite rejection, integrity check, cache behavior |
| **Acceptance criteria** | All 17 tests pass. Directory structure matches schema. Artifact files read-only after write. Cache directory allows overwrites. JSON uses 2-space indent. |
| **Scientific review** | No |
| **Notes** | Do not import from `cathodescope.tools` or `cathodescope.workflows`. Integrity check validates artifacts up to last completed step for incomplete workflows. |

---

### T-07: MP Client and Fixture Capture

| Field | Value |
|-------|-------|
| **Task ID** | T-07 |
| **Epic** | E-04: Scientific Tools |
| **Title** | MP Client and Fixture Capture |
| **Description** | Implement `CathodescopeMPClient` wrapping `mp-api` `MPRester`. Capture JSON fixtures for 3 benchmark materials. Implement caching and error handling. |
| **Why it exists** | The MP client is the first external dependency. All downstream tools need a structure to work with. Fixture capture ensures offline development. |
| **Dependencies** | T-02, T-05 |
| **Size** | M |
| **Status** | Done |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/tools/mp_client.py`, `tests/unit/test_tools/test_mp_client.py`, `tests/fixtures/mp_responses/mp-22526.json`, `tests/fixtures/mp_responses/mp-19017.json`, `tests/fixtures/mp_responses/mp-18767.json`, `scripts/capture_fixtures.py` |
| **Tests required** | 16 tests: fetch by mp_id, fetch by formula, error handling (not found, timeout, rate limit), caching, provenance, fixture validation |
| **Acceptance criteria** | All 16 tests pass. Fixture files contain valid pymatgen `Structure.as_dict()` data. Cache hit returns same data as fresh fetch. Unit tests never hit live API. |
| **Scientific review** | No |
| **Completed** | 2026-03-11 |
| **Notes** | 22 tests implemented (fixture tests parameterized across 3 materials). `CathodescopeMPClient(api_key, cache_dir)` wraps MPRester with disk cache (SHA-256 filename keys). Returns `ToolResult` with `evidence_type="A-retrieved"`. Failure cases: not-found → InputError, TimeoutError → NetworkError, other → UnknownError. `mp_api` has no stubs; suppressed via `# type: ignore[import-untyped]`. Fixture JSONs use representative structures (run `scripts/capture_fixtures.py` with live API key to refresh). |

---

### T-08: Input Resolver

| Field | Value |
|-------|-------|
| **Task ID** | T-08 |
| **Epic** | E-04: Scientific Tools |
| **Title** | Input Resolver |
| **Description** | Implement `resolve(raw_input: str) -> ToolResult` that detects input type (formula vs mp-id), validates, creates `NormalizedQuery`. |
| **Why it exists** | The resolver is Step 0 of every workflow. It converts raw user input to a validated `NormalizedQuery`. |
| **Dependencies** | T-03, T-07 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/tools/input_resolver.py`, `tests/unit/test_tools/test_input_resolver.py` |
| **Tests required** | 12 tests: formula resolution, mp-id resolution, invalid inputs, raw input preservation, source type detection, reduced formula population |
| **Acceptance criteria** | All 12 tests pass. "LiCoO2" and "mp-22526" resolve correctly. Invalid inputs produce `InputError` with clear messages. |
| **Scientific review** | No |
| **Notes** | Mock MP client in unit tests. Detect mp-id via regex `mp-\d+`. Use pymatgen `Composition` for formula validation. |

---

### T-08b: Family Classification Function

| Field | Value |
|-------|-------|
| **Task ID** | T-08b |
| **Epic** | E-04: Scientific Tools |
| **Title** | Family Classification Function |
| **Description** | Implement `classify_family(space_group, formula) -> str` that assigns `layered_oxide`, `olivine_polyanion`, `spinel`, or `other` based on space group and composition. |
| **Why it exists** | `CanonicalMaterial.family` must be assigned programmatically. Family classification feeds evidence label assignment — non-benchmarked families receive Level B. |
| **Dependencies** | T-03 |
| **Size** | XS |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/models/material.py`, `tests/unit/test_models/test_material.py` |
| **Tests required** | 5 tests: layered oxide, olivine, spinel, unknown, case insensitivity |
| **Acceptance criteria** | All 5 tests pass. All 3 benchmark materials classified correctly. Unknown composition returns `other`. |
| **Scientific review** | No |
| **Notes** | Rules: R-3m + LiMO2 → `layered_oxide`; Pnma + LiMPO4 → `olivine_polyanion`; Fd-3m + LiM2O4 → `spinel`; else → `other`. |

---

### T-09: Structure Normalizer

| Field | Value |
|-------|-------|
| **Task ID** | T-09 |
| **Epic** | E-04: Scientific Tools |
| **Title** | Structure Normalizer |
| **Description** | Implement structure normalization using pymatgen `SpacegroupAnalyzer.get_conventional_standard_structure()`. Verify space group preservation for all 3 benchmark materials. |
| **Why it exists** | Normalization converts retrieved structures to conventional standard cells. Required before relaxation for consistent comparisons. |
| **Dependencies** | T-02, T-07 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/tools/structure_normalizer.py`, `tests/unit/test_tools/test_structure_normalizer.py`, `tests/fixtures/structures/licoo2_conventional.json`, `tests/fixtures/structures/lifepo4_conventional.json`, `tests/fixtures/structures/limn2o4_conventional.json` |
| **Tests required** | 14 tests: space group preservation (3 materials), conventional cell, atom counts, tool result format, evidence type, data fields, degenerate structure handling |
| **Acceptance criteria** | All 14 tests pass. LiCoO2: R-3m, 12 atoms. LiFePO4: Pnma, 28 atoms. LiMn2O4: Fd-3m, 56 atoms. |
| **Scientific review** | **Yes** — Space group preservation review. Verify against `scientific_validity_matrix.md` Row 2. |
| **Notes** | Do not import from other tools. Do not mock pymatgen — use real structures from fixtures. |

---

### T-10: Structure Relaxer (Unit Tests with Mock Calculator)

| Field | Value |
|-------|-------|
| **Task ID** | T-10 |
| **Epic** | E-04: Scientific Tools |
| **Title** | Structure Relaxer (Unit Tests with Mock Calculator) |
| **Description** | Implement the MACE-based structure relaxer with dependency-injected calculator. Unit tests use mock calculator to verify convergence logic, trajectory recording, and error handling. |
| **Why it exists** | The relaxer is the primary computation step. Unit tests verify workflow logic independently of the MACE model. |
| **Dependencies** | T-02, T-05, T-09 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/tools/structure_relaxer.py`, `tests/unit/test_tools/test_structure_relaxer.py` |
| **Tests required** | 19 tests: result format, evidence type, convergence info, non-convergence, divergence, NaN forces, volume change, structure collapse, config respect, cell relaxation, provenance |
| **Acceptance criteria** | All 19 tests pass with mock calculator. Convergence and non-convergence paths tested. Error paths (NaN, divergence, collapse) tested. |
| **Scientific review** | No (real MACE testing is T-20) |
| **Notes** | Accept calculator as parameter (dependency injection). Create `MockCalculator` in test file. Track energy and fmax at each step. Do not import from other tools. |

---

### T-11: Reference Comparator

| Field | Value |
|-------|-------|
| **Task ID** | T-11 |
| **Epic** | E-04: Scientific Tools |
| **Title** | Reference Comparator |
| **Description** | Implement comparison of relaxed structure against MP reference: lattice parameter deviations, angle deviations, volume deviation, symmetry preservation. |
| **Why it exists** | The comparator produces the scientific value of the pipeline — quantitative deviations between relaxed and reference structures. |
| **Dependencies** | T-02, T-09 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/tools/reference_comparator.py`, `tests/unit/test_tools/test_reference_comparator.py` |
| **Tests required** | 12 tests: identical structures, lattice deviations, angle deviations, volume deviation, symmetry check, tool result, evidence type, required fields, composition mismatch, deviation formula, hand-computed values |
| **Acceptance criteria** | All 12 tests pass. Hand-computed deviations match programmatic values to `pytest.approx(0.001)`. |
| **Scientific review** | No |
| **Notes** | Use "deviation" not "error" — per `scientific_validity_matrix.md` Rule 6. Deviation formula: `|relaxed - reference| / reference * 100`. |

---

### T-12: Validation Layer (Structural + Convergence Checks)

| Field | Value |
|-------|-------|
| **Task ID** | T-12 |
| **Epic** | E-05: Validation & Evidence |
| **Title** | Validation Layer (Structural + Convergence Checks) |
| **Description** | Implement structural checks (bond lengths, atom overlap, coordination) and convergence checks (fmax, energy monotonicity, step count). Pure validation functions with no tool dependencies. |
| **Why it exists** | Sanity checks must exist before the physics validator tool can use them. The validation layer contains pure logic. |
| **Dependencies** | T-02 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/validation/structural.py`, `cathodescope/validation/convergence.py`, `cathodescope/validation/family_specific.py` (stubs), `tests/unit/test_validation/test_structural.py`, `tests/unit/test_validation/test_convergence.py` |
| **Tests required** | 16 tests: structural (8), convergence (8) |
| **Acceptance criteria** | All 16 tests pass. Check results are structured dicts with `check_name`, `passed`, `value`, `threshold`, `message`. |
| **Scientific review** | No |
| **Notes** | Do not import from `cathodescope.tools` or `cathodescope.config`. `family_specific.py` returns empty check lists for MVP. |

---

### T-13: Evidence Label Assigner

| Field | Value |
|-------|-------|
| **Task ID** | T-13 |
| **Epic** | E-05: Validation & Evidence |
| **Title** | Evidence Label Assigner |
| **Description** | Implement evidence label assignment logic and summary evidence level computation. Single source of truth for all label logic. |
| **Why it exists** | Evidence labels are mandatory on all outputs. The assigner ensures labels are deterministic and consistent with `scientific_validity_matrix.md`. |
| **Dependencies** | T-02 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/validation/evidence.py`, `tests/unit/test_validation/test_evidence.py` |
| **Tests required** | 14 tests: label assignment per step, summary inheritance (all-A, mixed A+B, any-C), label dict structure, non-benchmarked family downgrade |
| **Acceptance criteria** | All 14 tests pass. Label assignment deterministic. Summary inheritance follows weakest-level rule. Non-benchmarked families receive B-restricted for relaxation. |
| **Scientific review** | **Yes** — Evidence label audit (SC-03). Verify all 8 MVP labels match `scientific_validity_matrix.md` Section 3 Part A. |
| **Notes** | Step-to-label mapping: fetch→A-retrieved, normalize→A-computed, relax→A-computed (if benchmarked family), compare→A-compared, validate→A-compared. |

---

### T-14: Physics Validator Tool

| Field | Value |
|-------|-------|
| **Task ID** | T-14 |
| **Epic** | E-05: Validation & Evidence |
| **Title** | Physics Validator Tool |
| **Description** | Implement the physics validator tool that wraps structural checks, convergence checks, and evidence labeling into a single `ToolResult`. |
| **Why it exists** | Combines validation and evidence labeling into a tool conforming to the universal `ToolResult` contract. |
| **Dependencies** | T-12, T-13, T-05 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/tools/physics_validator.py`, `tests/unit/test_tools/test_physics_validator.py` |
| **Tests required** | 12 tests: result format, checks list, evidence labels, overall sanity, valid data, bond length failure, convergence failure, symmetry break, warnings, critical failure |
| **Acceptance criteria** | All 12 tests pass. Valid data → `overall_sanity: True`. Invalid data → specific check failures with structured messages. |
| **Scientific review** | No |
| **Notes** | Delegate to `validation.structural`, `validation.convergence`, `validation.evidence`. Do not duplicate check logic. |

---

## Wave 3: Reporting and Provenance

---

### T-15: JSON Report Builder

| Field | Value |
|-------|-------|
| **Task ID** | T-15 |
| **Epic** | E-07: Reporting Layer |
| **Title** | JSON Report Builder |
| **Description** | Implement `build_json_report(workflow_result, material) -> ReportRecord` that creates one `ReportSection` per workflow step plus summary and provenance sections. |
| **Why it exists** | The JSON report is the primary machine-readable artifact. Markdown is derived from it. |
| **Dependencies** | T-04, T-02 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/reporting/json_report.py`, `tests/unit/test_reporting/test_json_report.py` |
| **Tests required** | 12 tests: return type, required sections (material summary, retrieved data, normalization, relaxation, comparison, validation, evidence summary, provenance), evidence counts, serialization |
| **Acceptance criteria** | All 12 tests pass. Sections follow order defined in `architecture.md` Section 4.7. |
| **Scientific review** | No |
| **Notes** | Do not import from `cathodescope.tools`. Report builder operates on model objects, not tool internals. |

---

### T-16: Markdown Report Renderer

| Field | Value |
|-------|-------|
| **Task ID** | T-16 |
| **Epic** | E-07: Reporting Layer |
| **Title** | Markdown Report Renderer |
| **Description** | Implement `render_markdown(report: ReportRecord) -> str` with inline evidence labels matching `scientific_validity_matrix.md` Section 5 format. Enforce all 10 wording rules. |
| **Why it exists** | Human-readable reports with inline evidence labels are a core thesis deliverable. |
| **Dependencies** | T-15 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/reporting/markdown_report.py`, `tests/unit/test_reporting/test_markdown_report.py` |
| **Tests required** | 13 tests: return type, title, section headers with evidence levels, MP ID, MACE version, convergence details, lattice deviations, assessment paragraph, no disallowed words, validity matrix format match |
| **Acceptance criteria** | All 13 tests pass. Section headers: `### ... [Level X -- sub-type]`. No "validated structure", "discovered", "proved stable", "accurate" without reference. |
| **Scientific review** | **Yes** — Report wording audit (SC-04). Compare output against mock excerpt in `scientific_validity_matrix.md` Section 5. |
| **Notes** | Do not parse JSON report as text — use structured `ReportRecord` object. Never use "good agreement" — always quantitative. |

---

### T-17: Report Generator Tool

| Field | Value |
|-------|-------|
| **Task ID** | T-17 |
| **Epic** | E-07: Reporting Layer |
| **Title** | Report Generator Tool |
| **Description** | Thin wrapper tool that delegates to JSON builder and Markdown renderer, wrapping both outputs in a `ToolResult`. |
| **Why it exists** | Conforms report generation to the universal tool contract (`ToolResult`). |
| **Dependencies** | T-15, T-16 |
| **Size** | XS |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/tools/report_generator.py`, `tests/unit/test_tools/test_report_generator.py` |
| **Tests required** | 7 tests: return type, evidence type (metadata), data contains JSON and Markdown, evidence summary, missing step handling, provenance |
| **Acceptance criteria** | All 7 tests pass. No business logic duplication — pure delegation. |
| **Scientific review** | No |
| **Notes** | `evidence_type` is `"metadata"` — excluded from evidence summary count. |

---

### T-18: Workflow Base Classes and Engine

| Field | Value |
|-------|-------|
| **Task ID** | T-18 |
| **Epic** | E-08: Workflow Engine & Integration |
| **Title** | Workflow Base Classes and Engine |
| **Description** | Implement `WorkflowRegistry`, `WorkflowDefinition`, `WorkflowContext`, and `WorkflowEngine.run()`. Tool-agnostic step sequencer with error handling and partial result preservation. |
| **Why it exists** | The engine sequences all tools into a pipeline. It must be tool-agnostic. |
| **Dependencies** | T-02, T-05 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/workflows/base.py`, `cathodescope/workflows/engine.py`, `tests/unit/test_workflows/test_engine.py` |
| **Tests required** | 17 tests: registry (3), context (2), engine (12 — step execution, context passing, result recording, timestamps, runtime, config snapshot, failure handling, partial results, classification, error non-swallowing, provenance) |
| **Acceptance criteria** | All 17 tests pass. Engine is tool-agnostic — no imports from `cathodescope.tools`. Partial results preserved on failure. |
| **Scientific review** | No |
| **Notes** | Use mock step functions in unit tests. `WorkflowContext` is a typed dataclass per `architecture.md` Section 4.3. |

---

### T-19: structural_analysis Workflow Definition

| Field | Value |
|-------|-------|
| **Task ID** | T-19 |
| **Epic** | E-08: Workflow Engine & Integration |
| **Title** | structural_analysis Workflow Definition |
| **Description** | Register the `structural_analysis` v1.0.0 workflow with 7 steps: resolve_input, fetch_structure, normalize, relax, compare_reference, validate, generate_report. |
| **Why it exists** | The only MVP workflow. Defines the step sequence for the single-material pipeline. |
| **Dependencies** | T-18, all tools T-07 through T-17 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `cathodescope/workflows/structural_analysis.py`, `tests/unit/test_workflows/test_structural_analysis.py` |
| **Tests required** | 7 tests: registry registration, step count, step order, step names, version, tool binding, context passing |
| **Acceptance criteria** | All 7 tests pass. Step names match `architecture.md` Section 4.3 and `artifact_schema.md` step file naming. |
| **Scientific review** | No |
| **Notes** | Each step is a thin wrapper extracting data from context and calling the corresponding tool. |

---

### T-20: Integration Test — LiCoO2 Single-Material Pipeline

| Field | Value |
|-------|-------|
| **Task ID** | T-20 |
| **Epic** | E-08: Workflow Engine & Integration |
| **Title** | Integration Test — LiCoO2 Single-Material Pipeline |
| **Description** | End-to-end integration test with real MACE-MP-0 for LiCoO2. The Phase 1 acceptance test. |
| **Why it exists** | Validates the entire pipeline end-to-end with real MACE. This is the first real scientific computation and the Phase 1 gate test. |
| **Dependencies** | T-00 through T-19 (all) |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `tests/integration/test_single_material_pipeline.py` |
| **Tests required** | 14 tests: workflow result, status success, all steps completed, lattice deviations a and c < 2%, volume < 5%, symmetry preserved, report generated, all Level A labels, artifacts stored, provenance complete, rerun reproducibility, offline completion, integrity check |
| **Acceptance criteria** | All 14 tests pass. Constitutes Phase 1 gate acceptance test. |
| **Scientific review** | **Yes** — MACE accuracy verification (SC-01, SC-02). Verify LiCoO2 lattice parameters within 2% of MP reference. |
| **Notes** | Uses cached MP fixture (no live API). Real MACE-MP-0 for relaxation. Mark tests with `@pytest.mark.integration`. Verify MACE installs before running. |

---

### T-21: Integration Test — LiFePO4 and LiMn2O4

| Field | Value |
|-------|-------|
| **Task ID** | T-21 |
| **Epic** | E-08: Workflow Engine & Integration |
| **Title** | Integration Test — LiFePO4 and LiMn2O4 |
| **Description** | Integration tests for the remaining 2 benchmark materials with real MACE. LiFePO4 targets Full Success; LiMn2O4 targets at least Partial Success. |
| **Why it exists** | Validates the pipeline generalizes beyond LiCoO2 to the other two benchmark families. |
| **Dependencies** | T-20 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 1 |
| **Files affected** | `tests/integration/test_single_material_pipeline.py` (extend) |
| **Tests required** | 8 tests: LiFePO4 (result, deviations, symmetry, report), LiMn2O4 (result, no hard failure, report, failure classification if partial) |
| **Acceptance criteria** | All 8 tests pass. At least 2 of 3 materials achieve Full Success. |
| **Scientific review** | No (covered by T-20 checkpoint) |
| **Notes** | LiMn2O4 Partial Success is acceptable and scientifically informative (Jahn-Teller effects). Use `pytest.mark.parametrize` where possible. |

---

## Wave 4: Benchmark

---

### T-22: Benchmark Registry

| Field | Value |
|-------|-------|
| **Task ID** | T-22 |
| **Epic** | E-09: Benchmark Suite |
| **Title** | Benchmark Registry |
| **Description** | Implement `BenchmarkMaterialRegistry` defining which materials belong to each benchmark set. Phase 1 set: LiCoO2, LiFePO4, LiMn2O4. |
| **Why it exists** | Separates material definitions from runner logic. Required by the benchmark runner. |
| **Dependencies** | T-03 |
| **Size** | XS |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 2 |
| **Files affected** | `cathodescope/benchmark/registry.py`, `tests/unit/test_benchmark/test_registry.py` |
| **Tests required** | 8 tests: 3 materials present, each entry correct, get by name, unknown benchmark error, families, benchmark tags |
| **Acceptance criteria** | All 8 tests pass. Phase 1 benchmark name: `"phase1_structural_analysis"`. |
| **Scientific review** | No |
| **Notes** | Do not hardcode material data in the runner. Three families: LiCoO2 (mp-22526, layered_oxide), LiFePO4 (mp-19017, olivine_polyanion), LiMn2O4 (mp-18767, spinel). |

---

### T-23: Benchmark Runner

| Field | Value |
|-------|-------|
| **Task ID** | T-23 |
| **Epic** | E-09: Benchmark Suite |
| **Title** | Benchmark Runner |
| **Description** | Implement `BenchmarkRunner.run()` that iterates registry materials, runs workflow engine for each, extracts all 24 metrics into `BenchmarkRow`, produces `BenchmarkSummary`. |
| **Why it exists** | The runner orchestrates the structural_analysis workflow across all benchmark materials with structured result collection and failure isolation. |
| **Dependencies** | T-18, T-22, T-04, T-06 |
| **Size** | M |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 2 |
| **Files affected** | `cathodescope/benchmark/runner.py`, `tests/unit/test_benchmark/test_runner.py` |
| **Tests required** | 13 tests: all materials processed, summary returned, materials count, status counts, row per material, all metrics, failure isolation, continue after failure, failure classification, artifact storage, timestamps, runtime, provenance |
| **Acceptance criteria** | All 13 tests pass. Single material failure does not abort benchmark. All 24 metrics from `benchmark_spec.md` present per `BenchmarkRow`. |
| **Scientific review** | No |
| **Notes** | Do not import from `cathodescope.tools` directly — go through workflow engine. Status classification per `benchmark_spec.md` Section 5. |

---

### T-24: Benchmark Runner Integration Test

| Field | Value |
|-------|-------|
| **Task ID** | T-24 |
| **Epic** | E-09: Benchmark Suite |
| **Title** | Benchmark Runner Integration Test |
| **Description** | Full benchmark suite with real MACE on all 3 materials. The Phase 2 gate test. |
| **Why it exists** | Validates the benchmark meets the 2/3 Full Success criterion with real MACE computations. |
| **Dependencies** | T-21, T-23 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P0 |
| **Phase** | 2 |
| **Files affected** | `tests/integration/test_benchmark_suite.py` |
| **Tests required** | 8 tests: all 3 materials run, at least 2 Full Success, no hard failures, summary generated, rows stored, metrics complete, reproducible on rerun, evidence labeling complete |
| **Acceptance criteria** | All 8 tests pass. Phase 2 gate criteria met. |
| **Scientific review** | **Yes** — Benchmark results review (SC-05). Reproducibility verification (SC-06). |
| **Notes** | Do not lower thresholds to make tests pass. Do not skip reproducibility check. Allow 0.1% lattice deviation between runs. |

---

### T-24b: Benchmark Regression Comparison Tool

| Field | Value |
|-------|-------|
| **Task ID** | T-24b |
| **Epic** | E-09: Benchmark Suite |
| **Title** | Benchmark Regression Comparison Tool |
| **Description** | Implement `compare_benchmarks(summary_a, summary_b) -> RegressionReport` that detects status changes, metric deltas, new failures, and new successes between benchmark runs. |
| **Why it exists** | Without regression comparison, code changes that degrade benchmark performance go undetected. Required for Phase 2 gate. |
| **Dependencies** | T-23, T-04 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P1 |
| **Phase** | 2 |
| **Files affected** | `cathodescope/benchmark/comparator.py`, `tests/unit/test_benchmark/test_comparator.py` |
| **Tests required** | 6 tests: status change detection, metric deltas, new failures, new successes, regression report format, missing material handling |
| **Acceptance criteria** | All 6 tests pass. Status changes between runs detected and reported. |
| **Scientific review** | No |
| **Notes** | Expose via CLI: `cathodescope benchmark compare <path_a> <path_b>`. |

---

## Wave 5: Demo

---

### T-25: CLI Interface

| Field | Value |
|-------|-------|
| **Task ID** | T-25 |
| **Epic** | E-10: CLI & Hardening |
| **Title** | CLI Interface |
| **Description** | Implement CLI with `analyze`, `benchmark`, `--version` commands using `argparse`. Phase 3 requires a 3-minute demo. |
| **Why it exists** | The CLI wraps the pipeline for non-programmatic usage and enables the 3-minute demo. |
| **Dependencies** | T-19, T-23 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P2 |
| **Phase** | 3 |
| **Files affected** | `cathodescope/app/cli.py`, `tests/integration/test_cli.py` |
| **Tests required** | 7 tests: analyze command exists, analyze produces report, invalid formula error, benchmark command exists, benchmark runs phase1, help shows usage, version shows version |
| **Acceptance criteria** | All 7 tests pass. `cathodescope analyze LiCoO2` produces report. 3-minute demo completable. |
| **Scientific review** | No |
| **Notes** | Entry point in `pyproject.toml`. Progress to stderr, report path to stdout. Zero extra dependencies (argparse is stdlib). |

---

## Wave 6: Thesis-Core Hardening

---

### T-26: Pre-commit and CI Configuration

| Field | Value |
|-------|-------|
| **Task ID** | T-26 |
| **Epic** | E-10: CLI & Hardening |
| **Title** | Pre-commit and CI Configuration |
| **Description** | Finalize `.pre-commit-config.yaml` and create `.github/workflows/ci.yml` with ruff, mypy, and pytest (unit tests only in CI). |
| **Why it exists** | Automated quality gates prevent regressions and enforce code standards. |
| **Dependencies** | T-00 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P2 |
| **Phase** | 4 |
| **Files affected** | `.pre-commit-config.yaml`, `.github/workflows/ci.yml` |
| **Tests required** | N/A (infrastructure task) |
| **Acceptance criteria** | `pre-commit run --all-files` passes. CI workflow is valid YAML. |
| **Scientific review** | No |
| **Notes** | Skip MACE integration tests in CI (`-m "not integration"`). CI uses cached MP fixtures. |

---

### T-27: Import Rule Enforcement Tests

| Field | Value |
|-------|-------|
| **Task ID** | T-27 |
| **Epic** | E-10: CLI & Hardening |
| **Title** | Import Rule Enforcement Tests |
| **Description** | Implement AST-based tests that verify each package only imports from allowed packages per `dependency_graph.md` Section 6. |
| **Why it exists** | The layered architecture must be enforced programmatically, not just by convention. |
| **Dependencies** | All previous tasks |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P2 |
| **Phase** | 4 |
| **Files affected** | `tests/test_import_rules.py` |
| **Tests required** | 10 tests: models isolation (2), tools isolation (1), validation isolation (2), reporting isolation (2), provenance isolation (1), benchmark isolation (1), agent directory (1) |
| **Acceptance criteria** | All 10 tests pass. Any import rule violation caught automatically. |
| **Scientific review** | No |
| **Notes** | Use `ast.parse()` to inspect import statements. Do not use runtime import checking. |

---

### T-28: Fixture Capture Script and Golden Output Generation

| Field | Value |
|-------|-------|
| **Task ID** | T-28 |
| **Epic** | E-10: CLI & Hardening |
| **Title** | Fixture Capture Script and Golden Output Generation |
| **Description** | Finalize `scripts/capture_fixtures.py`. Generate golden `WorkflowResult`, `ReportRecord`, and `BenchmarkSummary` JSON files for regression testing. |
| **Why it exists** | Golden outputs enable regression tests and ensure CI works offline. |
| **Dependencies** | T-20 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P2 |
| **Phase** | 4 |
| **Files affected** | `scripts/capture_fixtures.py`, `tests/fixtures/expected_outputs/licoo2_workflow_result.json`, `tests/fixtures/expected_outputs/licoo2_report.json`, `tests/fixtures/expected_outputs/benchmark_summary.json` |
| **Tests required** | N/A (tooling task — golden outputs consumed by T-29) |
| **Acceptance criteria** | All fixture files exist and contain valid JSON. Fixtures committed. Script has `--force` flag. |
| **Scientific review** | No |
| **Notes** | Script is idempotent. Golden outputs frozen after first generation. |

---

### T-29: Regression Tests

| Field | Value |
|-------|-------|
| **Task ID** | T-29 |
| **Epic** | E-10: CLI & Hardening |
| **Title** | Regression Tests |
| **Description** | Compare current pipeline output against golden outputs to catch unintended behavioral changes. |
| **Why it exists** | Regression tests detect unintended changes across refactors. |
| **Dependencies** | T-28 |
| **Size** | S |
| **Status** | Todo |
| **Priority** | P2 |
| **Phase** | 4 |
| **Files affected** | `tests/unit/test_regression.py` |
| **Tests required** | 4 tests: workflow result match, report sections match, evidence summary match, benchmark metrics match |
| **Acceptance criteria** | All 4 tests pass. Numerical comparisons use `pytest.approx(abs=0.01)`. UUIDs/timestamps excluded. |
| **Scientific review** | No |
| **Notes** | Use mock MACE (deterministic forces) for regression runs. String fields compared exactly. |

---

## Wave 7: Agent Layer

---

### T-30: Agent Scaffolding (Empty Stubs)

| Field | Value |
|-------|-------|
| **Task ID** | T-30 |
| **Epic** | E-10: CLI & Hardening |
| **Title** | Agent Scaffolding (Empty Stubs) |
| **Description** | Create `cathodescope/agent/__init__.py` with docstring, `__all__ = []`, and no functionality. Ensures Phase 5 starts with correct dependency boundaries. |
| **Why it exists** | The `agent/` directory must have correct interfaces so Phase 5 starts cleanly. |
| **Dependencies** | T-18 |
| **Size** | XS |
| **Status** | Todo |
| **Priority** | P3 |
| **Phase** | 4 |
| **Files affected** | `cathodescope/agent/__init__.py` |
| **Tests required** | 2 tests: module importable, directory contains only `__init__.py` |
| **Acceptance criteria** | All 2 tests pass. No actual agent functionality. |
| **Scientific review** | No |
| **Notes** | Do not implement any agent functionality. Do not add dependency on `cathodescope.tools`. |

---

## Task Summary Table

| Task | Epic | Title | Size | Priority | Phase | Status | Critical Path | Sci Review |
|------|------|-------|------|----------|-------|--------|---------------|------------|
| T-00 | E-01 | Project Scaffolding | S | P0 | 1 | Done | Yes | No |
| T-01 | E-02 | ProvenanceRecord Model | S | P0 | 1 | Done | Yes | No |
| T-02 | E-02 | ErrorRecord, ToolResult, StepResult, WorkflowResult | M | P0 | 1 | Done | Yes | No |
| T-03 | E-02 | CanonicalMaterial, NormalizedQuery | M | P1 | 1 | Todo | No | No |
| T-04 | E-02 | ReportRecord, BenchmarkRow, BenchmarkSummary | S | P1 | 1 | Todo | No | No |
| T-05 | E-03 | Configuration System | M | P0 | 1 | Done | Yes | No |
| T-06 | E-06 | Artifact / Provenance Store | M | P1 | 1 | Todo | No | No |
| T-07 | E-04 | MP Client and Fixture Capture | M | P0 | 1 | Done | Yes | No |
| T-08 | E-04 | Input Resolver | S | P1 | 1 | Todo | No | No |
| T-08b | E-04 | Family Classification Function | XS | P1 | 1 | Todo | No | No |
| T-09 | E-04 | Structure Normalizer | M | P0 | 1 | Todo | Yes | **Yes** |
| T-10 | E-04 | Structure Relaxer (Mock) | M | P0 | 1 | Todo | Yes | No |
| T-11 | E-04 | Reference Comparator | M | P1 | 1 | Todo | No | No |
| T-12 | E-05 | Validation Layer | M | P1 | 1 | Todo | No | No |
| T-13 | E-05 | Evidence Label Assigner | S | P1 | 1 | Todo | No | **Yes** |
| T-14 | E-05 | Physics Validator Tool | S | P1 | 1 | Todo | No | No |
| T-15 | E-07 | JSON Report Builder | M | P1 | 1 | Todo | No | No |
| T-16 | E-07 | Markdown Report Renderer | M | P1 | 1 | Todo | No | **Yes** |
| T-17 | E-07 | Report Generator Tool | XS | P1 | 1 | Todo | No | No |
| T-18 | E-08 | Workflow Engine | M | P0 | 1 | Todo | Yes | No |
| T-19 | E-08 | structural_analysis Workflow | S | P0 | 1 | Todo | Yes | No |
| T-20 | E-08 | Integration — LiCoO2 Pipeline | M | P0 | 1 | Todo | Yes | **Yes** |
| T-21 | E-08 | Integration — LiFePO4, LiMn2O4 | S | P0 | 1 | Todo | Yes | No |
| T-22 | E-09 | Benchmark Registry | XS | P1 | 2 | Todo | No | No |
| T-23 | E-09 | Benchmark Runner | M | P0 | 2 | Todo | Yes | No |
| T-24 | E-09 | Benchmark Integration Test | S | P0 | 2 | Todo | Yes | **Yes** |
| T-24b | E-09 | Benchmark Regression Comparator | S | P1 | 2 | Todo | No | No |
| T-25 | E-10 | CLI Interface | S | P2 | 3 | Todo | No | No |
| T-26 | E-10 | Pre-commit and CI | S | P2 | 4 | Todo | No | No |
| T-27 | E-10 | Import Rule Enforcement | S | P2 | 4 | Todo | No | No |
| T-28 | E-10 | Golden Output Generation | S | P2 | 4 | Todo | No | No |
| T-29 | E-10 | Regression Tests | S | P2 | 4 | Todo | No | No |
| T-30 | E-10 | Agent Scaffolding | XS | P3 | 4 | Todo | No | No |

**Total**: 32 tasks | 13 on critical path | 5 require scientific review

---

*This is the authoritative task board for CathodeScope implementation. Update task statuses here as work progresses. All task definitions are derived from `planning/tdd_task_breakdown.md`.*
