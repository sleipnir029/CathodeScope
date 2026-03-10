# CathodeScope — Claude Code Execution Prompts

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Source**: `tdd_task_breakdown.md` (authoritative task definitions)
**Total Prompts**: 33 (P-00 through P-30, plus P-08b and P-24b)

---

## How to Use This Document

### Execution Model

Each prompt below is a self-contained instruction for one TDD task. Copy the prompt into Claude Code and execute it. Do not combine prompts or skip prompts.

### Sequencing Rules

1. **Execute prompts in order within each wave.** Prerequisites are listed in each prompt's ORIENTATION section.
2. **Do not start a wave until the previous wave's gate criterion is met.**
3. **Do not skip prompts.** Each prompt builds on the previous one.
4. **If a prompt fails, fix the failure before proceeding.** Do not move to the next prompt with failing tests.

### Pre-Flight Checks (Before Every Prompt)

Before pasting any prompt, verify:
- `git status` shows a clean working tree (all previous work committed)
- `pytest` passes (all existing tests green)
- `ruff check cathodescope/ tests/` passes
- `mypy cathodescope/` passes

### Post-Flight Checks (After Every Prompt)

After each prompt completes, verify:
- All new tests pass
- All previously passing tests still pass
- `ruff check` and `mypy` still pass
- Changes are committed with the suggested commit message

### Scientific Review Gates

Implementation **must pause** for manual scientific review at these prompts:
- **P-09** — Space group preservation for 3 benchmark materials
- **P-13** — Evidence labels match validity matrix
- **P-16** — Report wording matches mock excerpt format
- **P-20** — LiCoO2 lattice parameters within 2% of MP reference
- **P-24** — Benchmark meets 2/3 Full Success criterion

Do not proceed past a scientific review gate until the review is completed and documented.

---

## Prompt Conventions

### Variables

| Variable | Meaning |
|---|---|
| `{PROJECT_ROOT}` | Repository root directory |
| `{SRC}` | `cathodescope/` package directory |
| `{TESTS}` | `tests/` directory |

### Commit Message Prefixes

| Prefix | When to Use |
|---|---|
| `test:` | RED phase — writing failing tests |
| `feat:` | GREEN phase — making tests pass with production code |
| `fix:` | GREEN phase — fixing a bug to make tests pass |
| `refactor:` | REFACTOR phase — cleanup with tests green |
| `chore:` | Infrastructure tasks (CI, pre-commit, fixtures) |

### Fencing

All prompts use `~~~text` fencing to avoid Markdown nesting conflicts.

---

## Wave 0: Docs and Skeleton

---

### P-00: Project Scaffolding and Build Configuration

~~~text
TASK: P-00 — Project Scaffolding and Build Configuration
PREREQUISITES: None
WAVE: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read the following files to understand the project structure:
- docs/tdd_task_breakdown.md — Section 2 (Repo Skeleton)
- docs/dependency_graph.md — Section 6 (Import Rules)
- docs/artifact_schema.md — Section 3 (Directory Conventions)

Run:
  git log --oneline -5
  ls -la

This is the first task. No existing code should exist yet.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

Create file: tests/unit/test_scaffold.py

Tests to write:
- test_package_importable()
    → `import cathodescope` succeeds and `cathodescope.__version__` exists
- test_all_subpackages_importable()
    → every subpackage (cathodescope.models, cathodescope.config, cathodescope.tools,
      cathodescope.validation, cathodescope.reporting, cathodescope.workflows,
      cathodescope.provenance, cathodescope.benchmark, cathodescope.app) imports without error

Run: pytest tests/unit/test_scaffold.py — expect FAILURES (modules don't exist yet)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Create Project Structure

Create pyproject.toml:
- Project name: cathodescope
- Python: >=3.11
- Dependencies: pymatgen, ase, mace-torch, mp-api, pydantic>=2.0, numpy
- Dev dependencies: pytest, pytest-cov, ruff, mypy, pre-commit, freezegun
- Entry point: cathodescope = "cathodescope.app.cli:main"
- Ruff and mypy configuration sections

Create .gitignore:
- artifacts/, __pycache__/, .venv/, *.egg-info/, .mypy_cache/, .ruff_cache/, .env, .pytest_cache/

Create .pre-commit-config.yaml:
- Hooks for ruff check, ruff format --check, mypy

Create cathodescope/__init__.py:
- __version__ = "0.1.0"

Create ALL __init__.py files for subpackages:
- cathodescope/models/__init__.py
- cathodescope/config/__init__.py
- cathodescope/tools/__init__.py
- cathodescope/validation/__init__.py
- cathodescope/reporting/__init__.py
- cathodescope/workflows/__init__.py
- cathodescope/provenance/__init__.py
- cathodescope/benchmark/__init__.py
- cathodescope/app/__init__.py

Create ALL empty placeholder source files (module docstring only):
- cathodescope/models/material.py
- cathodescope/models/results.py
- cathodescope/models/provenance.py
- cathodescope/models/reports.py
- cathodescope/config/defaults.py
- cathodescope/config/settings.py
- cathodescope/tools/mp_client.py
- cathodescope/tools/input_resolver.py
- cathodescope/tools/structure_normalizer.py
- cathodescope/tools/structure_relaxer.py
- cathodescope/tools/reference_comparator.py
- cathodescope/tools/physics_validator.py
- cathodescope/tools/report_generator.py
- cathodescope/validation/structural.py
- cathodescope/validation/convergence.py
- cathodescope/validation/family_specific.py
- cathodescope/validation/evidence.py
- cathodescope/reporting/json_report.py
- cathodescope/reporting/markdown_report.py
- cathodescope/workflows/base.py
- cathodescope/workflows/engine.py
- cathodescope/workflows/structural_analysis.py
- cathodescope/provenance/store.py
- cathodescope/benchmark/runner.py
- cathodescope/benchmark/registry.py
- cathodescope/app/cli.py

Create ALL empty test files:
- tests/__init__.py
- tests/unit/__init__.py
- tests/unit/test_models/__init__.py
- tests/unit/test_models/test_material.py
- tests/unit/test_models/test_results.py
- tests/unit/test_models/test_provenance.py
- tests/unit/test_models/test_reports.py
- tests/unit/test_config/__init__.py
- tests/unit/test_config/test_defaults.py
- tests/unit/test_config/test_settings.py
- tests/unit/test_tools/__init__.py
- tests/unit/test_tools/test_mp_client.py
- tests/unit/test_tools/test_input_resolver.py
- tests/unit/test_tools/test_structure_normalizer.py
- tests/unit/test_tools/test_structure_relaxer.py
- tests/unit/test_tools/test_reference_comparator.py
- tests/unit/test_tools/test_physics_validator.py
- tests/unit/test_tools/test_report_generator.py
- tests/unit/test_validation/__init__.py
- tests/unit/test_validation/test_structural.py
- tests/unit/test_validation/test_convergence.py
- tests/unit/test_validation/test_evidence.py
- tests/unit/test_reporting/__init__.py
- tests/unit/test_reporting/test_json_report.py
- tests/unit/test_reporting/test_markdown_report.py
- tests/unit/test_workflows/__init__.py
- tests/unit/test_workflows/test_engine.py
- tests/unit/test_workflows/test_structural_analysis.py
- tests/unit/test_provenance/__init__.py
- tests/unit/test_provenance/test_store.py
- tests/unit/test_benchmark/__init__.py
- tests/unit/test_benchmark/test_runner.py
- tests/unit/test_benchmark/test_registry.py
- tests/integration/__init__.py
- tests/integration/test_single_material_pipeline.py
- tests/integration/test_benchmark_suite.py
- tests/integration/test_cli.py
- tests/test_import_rules.py (placeholder — full implementation in T-27)

Create tests/conftest.py:
- Shared fixtures: frozen_time (freezegun to 2026-01-01T00:00:00Z),
  deterministic_uuid (factory returning sequential UUIDs),
  sample_provenance (returns a minimal valid ProvenanceRecord dict)

Create fixture directories:
- tests/fixtures/mp_responses/
- tests/fixtures/structures/
- tests/fixtures/configs/
- tests/fixtures/expected_outputs/

Create scripts/capture_fixtures.py (placeholder with docstring)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None needed for scaffolding.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT add any business logic in this task
- Do NOT create any pydantic models yet
- Do NOT create fixture data yet
- Do NOT implement any functions — only module docstrings in placeholder files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pip install -e ".[dev]"           → must succeed
  pytest tests/                      → 0 failures, 2 tests pass
  ruff check cathodescope/           → no errors
  mypy cathodescope/                 → no errors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add scaffold import tests (P-00 RED)
  feat: create project skeleton with all placeholder files (P-00 GREEN)
~~~

---

## Wave 1: Core Models and Config

---

### P-01: ProvenanceRecord Model

~~~text
TASK: P-01 — ProvenanceRecord Model
PREREQUISITES: P-00 (project scaffold exists)
WAVE: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/artifact_schema.md — Section 2.5 (ProvenanceRecord schema)
- cathodescope/models/provenance.py (currently empty placeholder)
- tests/unit/test_models/test_provenance.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_models/test_provenance.py

Tests to write (14 total):
- test_provenance_record_creation_with_valid_data()
    → ProvenanceRecord instantiates with all 16 fields populated
- test_provenance_record_rejects_missing_required_fields()
    → ValidationError raised when required fields omitted
- test_provenance_record_serializes_to_json()
    → model_dump_json() produces valid JSON string
- test_provenance_record_deserializes_from_json()
    → model_validate_json() round-trips correctly
- test_provenance_record_schema_version_is_string()
    → schema_version field accepts "1.0.0"
- test_provenance_record_created_at_is_iso8601()
    → created_at validates ISO 8601 format
- test_provenance_record_input_hash_is_sha256_hex()
    → input_hash validates as 64-char hex string
- test_provenance_record_parent_ids_is_list_of_strings()
    → parent_ids accepts list[str], rejects non-list
- test_provenance_record_dependencies_captures_versions()
    → dependencies dict has pymatgen, ase, mace-torch keys
- test_provenance_record_config_snapshot_is_dict()
    → config_snapshot accepts arbitrary dict
- test_create_provenance_helper_function()
    → create_provenance() returns fully-populated record without arguments
- test_provenance_record_mace_checkpoint_hash_is_optional()
    → mace_checkpoint_hash accepts string or None
- test_provenance_record_mp_database_version_is_optional()
    → mp_database_version accepts string or None
- test_provenance_record_platform_is_string()
    → platform field is a non-empty string

Run: pytest tests/unit/test_models/test_provenance.py — expect 14 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement ProvenanceRecord

File: cathodescope/models/provenance.py

Implementation:
- Define ProvenanceRecord as a pydantic BaseModel with 16 fields per artifact_schema.md Section 2.5:
  schema_version: str (default "1.0.0")
  created_at: str (ISO 8601)
  created_by: Literal["cathodescope", "user", "agent"]
  cathodescope_version: str
  python_version: str
  dependencies: dict[str, str]
  config_snapshot: dict[str, Any]
  input_hash: str (SHA-256 hex, 64 chars)
  parent_ids: list[str]
  mace_checkpoint_hash: str | None (default None)
  mp_database_version: str | None (default None)
  platform: str
  mace_model_name: str | None (default None)
  random_seeds: dict[str, Any] | None (default None)
  compute_device: str | None (default None)
  notes: str | None (default None)

- Define create_provenance() factory function:
  Auto-populates cathodescope_version from cathodescope.__version__,
  python_version from sys.version, created_at from datetime.utcnow().isoformat() + "Z",
  platform from platform.system() + "-" + platform.machine(),
  dependencies from importlib.metadata.version() for pymatgen, ase, mace-torch, mp-api, numpy, pydantic.
  Remaining fields use sensible defaults (empty dict for config_snapshot, empty string for input_hash, etc.).

Constraints:
- created_by uses Literal type (pydantic v2 pattern)
- input_hash validator: must be empty string or 64-char hex
- Do NOT import from any other cathodescope module

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Ensure model_config has json_schema_extra with an example if helpful
- Clean up any redundant imports

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from any other cathodescope module
- Do NOT add tool-specific fields to ProvenanceRecord
- Do NOT modify any files outside provenance.py and test_provenance.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_models/test_provenance.py -v   → 14 pass
  pytest tests/                                          → 0 failures
  ruff check cathodescope/models/provenance.py           → clean
  mypy --strict cathodescope/models/provenance.py        → clean

Expected: ProvenanceRecord.model_dump() produces valid JSON.
Expected: ProvenanceRecord.model_validate(json_data) round-trips correctly.
Expected: create_provenance() returns a fully-populated record without any arguments.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 14 ProvenanceRecord tests (P-01 RED)
  feat: implement ProvenanceRecord model and create_provenance() (P-01 GREEN)
~~~

---

### P-02: ErrorRecord, ToolResult, StepResult, WorkflowResult Models

~~~text
TASK: P-02 — ErrorRecord, ToolResult, StepResult, WorkflowResult Models
PREREQUISITES: P-01 (ProvenanceRecord exists)
WAVE: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/artifact_schema.md — Sections 2.2 (WorkflowResult, StepResult, ErrorRecord) and 2.3 (ToolResult)
- cathodescope/models/provenance.py (ProvenanceRecord — you'll import this)
- cathodescope/models/results.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_models/test_results.py

Tests to write (23 total):

ErrorRecord tests:
- test_error_record_creation_with_valid_data()
- test_error_record_error_type_validates_enum()
    → accepts: InputError, RetrievalError, ComputationError, ValidationError, ArtifactError
- test_error_record_rejects_unknown_error_type()
- test_error_record_recoverable_is_boolean()
- test_error_record_serializes_to_json()

ToolResult tests:
- test_tool_result_creation_success()
- test_tool_result_creation_warning()
- test_tool_result_creation_error()
- test_tool_result_status_validates_enum()
    → accepts: success, warning, error
- test_tool_result_evidence_type_validates_enum()
    → accepts: A-retrieved, A-computed, A-compared, B-restricted, C-proxy
- test_tool_result_data_must_be_dict()
- test_tool_result_warnings_is_list_of_strings()
- test_tool_result_serializes_to_json()
- test_tool_result_deserializes_from_json()

StepResult tests:
- test_step_result_creation_with_all_fields()
- test_step_result_error_field_is_optional()
- test_step_result_evidence_type_validates_enum()
- test_step_result_serializes_to_json()

WorkflowResult tests:
- test_workflow_result_creation_with_all_fields()
- test_workflow_result_status_validates_enum()
    → accepts: success, partial_success, soft_failure, hard_failure, infrastructure_failure
- test_workflow_result_steps_is_ordered_list()
- test_workflow_result_serializes_to_json()
- test_workflow_result_deserializes_from_json()

Run: pytest tests/unit/test_models/test_results.py — expect 23 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Models

File: cathodescope/models/results.py

ErrorRecord fields (artifact_schema.md Section 2.2):
  error_type: Literal["InputError", "RetrievalError", "ComputationError", "ValidationError", "ArtifactError"]
  message: str
  details: dict[str, Any] | None = None
  recoverable: bool

ToolResult fields (artifact_schema.md Section 2.3):
  status: Literal["success", "warning", "error"]
  evidence_type: Literal["A-retrieved", "A-computed", "A-compared", "B-restricted", "C-proxy"]
  data: dict[str, Any]
  warnings: list[str] = []
  provenance: ProvenanceRecord
  artifacts: list[str] = []

StepResult fields (artifact_schema.md Section 2.2):
  step_name: str
  step_index: int
  status: Literal["success", "warning", "failed", "skipped"]
  evidence_type: Literal["A-retrieved", "A-computed", "A-compared", "B-restricted", "C-proxy"]
  data: dict[str, Any]
  warnings: list[str] = []
  error: ErrorRecord | None = None
  artifacts: list[str] = []
  started_at: str
  completed_at: str
  provenance: ProvenanceRecord

WorkflowResult fields (artifact_schema.md Section 2.2):
  schema_version: str = "1.0.0"
  workflow_run_id: str
  workflow_name: str
  workflow_version: str
  material_id: str
  status: Literal["success", "partial_success", "soft_failure", "hard_failure", "infrastructure_failure"]
  steps: list[StepResult]
  started_at: str
  completed_at: str
  runtime_seconds: float
  config_snapshot: dict[str, Any]
  provenance: ProvenanceRecord

Constraints:
- Use Literal types for all enums (pydantic v2 pattern)
- Import ProvenanceRecord from cathodescope.models.provenance
- Do NOT import from cathodescope.tools or cathodescope.config
- Keep ToolResult.data as dict[str, Any] — no workflow-specific shapes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract shared Literal types to module-level constants if repeated
- Ensure all models have clear docstrings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from cathodescope.tools or cathodescope.config
- Do NOT add workflow-specific data shapes inside ToolResult.data
- Do NOT modify provenance.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_models/test_results.py -v   → 23 pass
  pytest tests/                                       → 0 failures
  ruff check cathodescope/models/results.py           → clean
  mypy --strict cathodescope/models/results.py        → clean

Expected: Invalid enum values rejected by pydantic validation.
Expected: Full JSON round-trip for every model.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 23 result model tests (P-02 RED)
  feat: implement ErrorRecord, ToolResult, StepResult, WorkflowResult (P-02 GREEN)
~~~

---

### P-03: CanonicalMaterial and NormalizedQuery Models

~~~text
TASK: P-03 — CanonicalMaterial and NormalizedQuery Models
PREREQUISITES: P-01 (ProvenanceRecord exists)
WAVE: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/artifact_schema.md — Section 2.1 (CanonicalMaterial schema)
- docs/tdd_task_breakdown.md — T-03 section
- cathodescope/models/material.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_models/test_material.py

Tests to write (16 total):
- test_normalized_query_creation_from_formula()
- test_normalized_query_creation_from_mp_id()
- test_normalized_query_rejects_empty_input()
- test_normalized_query_source_type_validates_enum()
    → accepts: formula, mp_id
- test_normalized_query_preserves_raw_input()
- test_normalized_query_serializes_to_json()
- test_canonical_material_creation_with_valid_data()
- test_canonical_material_rejects_missing_structure()
- test_canonical_material_family_validates_enum()
    → accepts: layered_oxide, olivine_polyanion, spinel, other
- test_canonical_material_source_validates_enum()
    → accepts: materials_project, user_upload, generated
- test_canonical_material_material_id_is_uuid_format()
- test_canonical_material_workflow_eligibility_is_dict()
- test_canonical_material_benchmark_tags_is_list()
- test_canonical_material_serializes_to_json()
- test_canonical_material_deserializes_from_json()
- test_canonical_material_structure_field_accepts_pymatgen_dict()
    → structure dict must have keys "lattice" and "sites"

Run: pytest tests/unit/test_models/test_material.py — expect 16 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Models

File: cathodescope/models/material.py

NormalizedQuery fields:
  formula: str
  reduced_formula: str
  mp_id: str | None = None
  source_type: Literal["formula", "mp_id"]
  raw_input: str
  timestamp: str (ISO 8601)

CanonicalMaterial fields (artifact_schema.md Section 2.1):
  schema_version: str = "1.0.0"
  material_id: str (UUID format)
  formula: str
  reduced_formula: str
  family: Literal["layered_oxide", "olivine_polyanion", "spinel", "other"]
  structure: dict[str, Any] (validator checks for "lattice" and "sites" keys)
  source: Literal["materials_project", "user_upload", "generated"]
  mp_id: str | None = None
  identifiers: dict[str, str] = {}
  benchmark_tags: list[str] = []
  workflow_eligibility: dict[str, bool] = {"structural_analysis": True}
  created_at: str (ISO 8601)
  provenance: ProvenanceRecord

Constraints:
- Do NOT import pymatgen.Structure as a type annotation — use dict with a validator
- Do NOT create factory functions that depend on the MP client
- Import ProvenanceRecord from cathodescope.models.provenance only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import pymatgen.Structure as a type — use dict
- Do NOT create factory functions depending on MP client
- Do NOT modify provenance.py or results.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_models/test_material.py -v   → 16 pass
  pytest tests/                                        → 0 failures
  ruff check cathodescope/models/material.py           → clean
  mypy --strict cathodescope/models/material.py        → clean

Expected: Invalid family or source values rejected.
Expected: Structures from pymatgen as_dict() round-trip through the model.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 16 material model tests (P-03 RED)
  feat: implement CanonicalMaterial and NormalizedQuery (P-03 GREEN)
~~~

---

### P-04: ReportRecord, ReportSection, BenchmarkRow, BenchmarkSummary Models

~~~text
TASK: P-04 — ReportRecord, ReportSection, BenchmarkRow, BenchmarkSummary Models
PREREQUISITES: P-01 (ProvenanceRecord exists)
WAVE: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/artifact_schema.md — Sections 2.4 (ReportRecord), 2.6 (BenchmarkRow), 2.7 (BenchmarkSummary)
- cathodescope/models/reports.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_models/test_reports.py

Tests to write (18 total):
- test_report_section_creation()
- test_report_section_evidence_labels_is_list()
- test_report_section_data_is_dict()
- test_report_record_creation_with_all_fields()
- test_report_record_sections_is_ordered_list()
- test_report_record_evidence_summary_is_dict()
- test_report_record_serializes_to_json()
- test_report_record_deserializes_from_json()
- test_report_record_has_raw_user_input()
- test_benchmark_row_creation()
- test_benchmark_row_metrics_is_dict()
- test_benchmark_row_failure_category_is_optional()
- test_benchmark_row_status_validates_enum()
    → accepts: success, partial_success, soft_failure, hard_failure, infrastructure_failure
- test_benchmark_row_serializes_to_json()
- test_benchmark_summary_creation()
- test_benchmark_summary_status_counts_is_dict()
- test_benchmark_summary_materials_count_matches_rows()
    → model_validator checks materials_count == sum(status_counts.values()) == len(rows)
- test_benchmark_summary_serializes_to_json()

Run: pytest tests/unit/test_models/test_reports.py — expect 18 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Models

File: cathodescope/models/reports.py

ReportSection fields (artifact_schema.md Section 2.4):
  heading: str
  content_markdown: str
  data: dict[str, Any]
  evidence_labels: list[str]

ReportRecord fields (artifact_schema.md Section 2.4):
  schema_version: str = "1.0.0"
  report_id: str
  material_id: str
  workflow_result_id: str
  report_type: str
  raw_user_input: str
  title: str
  sections: list[ReportSection]
  evidence_summary: dict[str, int]
  warnings: list[str] = []
  generated_at: str
  provenance: ProvenanceRecord

BenchmarkRow fields (artifact_schema.md Section 2.6):
  schema_version: str = "1.0.0"
  benchmark_run_id: str
  material_id: str
  formula: str
  family: str
  workflow_name: str
  workflow_version: str
  status: Literal["success", "partial_success", "soft_failure", "hard_failure", "infrastructure_failure"]
  metrics: dict[str, Any]
  failure_category: str | None = None
  timestamp: str
  provenance: ProvenanceRecord

BenchmarkSummary fields (artifact_schema.md Section 2.7):
  schema_version: str = "1.0.0"
  benchmark_run_id: str
  benchmark_name: str
  materials_count: int
  status_counts: dict[str, int]
  rows: list[str]
  started_at: str
  completed_at: str
  runtime_seconds: float
  provenance: ProvenanceRecord

Add model_validator to BenchmarkSummary:
  materials_count == sum(status_counts.values()) == len(rows)

Constraints:
- Models are pure data — no rendering logic
- Import only from cathodescope.models.provenance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT create rendering logic in models
- Do NOT import from tools, config, or workflows
- Do NOT modify other model files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_models/test_reports.py -v   → 18 pass
  pytest tests/                                       → 0 failures
  ruff check cathodescope/models/reports.py           → clean
  mypy --strict cathodescope/models/reports.py        → clean

Expected: BenchmarkSummary rejects inconsistent materials_count / status_counts / rows.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 18 report and benchmark model tests (P-04 RED)
  feat: implement ReportRecord, BenchmarkRow, BenchmarkSummary (P-04 GREEN)
~~~

---

### P-05: Configuration System

~~~text
TASK: P-05 — Configuration System
PREREQUISITES: P-01 (ProvenanceRecord for config_snapshot)
WAVE: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-05 section
- docs/benchmark_spec.md — Section 4 (threshold values for defaults)
- cathodescope/config/defaults.py (currently empty)
- cathodescope/config/settings.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_config/test_defaults.py

Tests (8):
- test_default_relaxation_config_has_fmax()         → 0.01 eV/Å
- test_default_relaxation_config_has_max_steps()     → 500
- test_default_relaxation_config_has_mace_model()    → "MACE-MP-0"
- test_default_comparison_config_has_lattice_tolerance()  → 2.0%
- test_default_comparison_config_has_volume_tolerance()   → 5.0%
- test_default_validation_config_has_bond_length_bounds() → min 1.0, max 4.0
- test_default_report_config_exists()
- test_default_benchmark_config_exists()

File: tests/unit/test_config/test_settings.py

Tests (9):
- test_settings_loads_defaults_when_no_file()
- test_settings_merges_json_overrides()
- test_settings_validates_types()
- test_settings_rejects_negative_fmax()
- test_settings_rejects_zero_max_steps()
- test_settings_mp_api_key_from_environment()
- test_settings_missing_api_key_raises_clear_error()
- test_settings_config_snapshot_returns_dict()
- test_settings_creates_valid_provenance_config_snapshot()

Create fixture files:
- tests/fixtures/configs/default_config.json
- tests/fixtures/configs/strict_config.json

Run: pytest tests/unit/test_config/ — expect 17 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Configuration

File: cathodescope/config/defaults.py

Define pydantic config models:
- RelaxationConfig: fmax=0.01, max_steps=500, mace_model="MACE-MP-0",
  optimizer="FIRE", relax_cell=True, filter_type="FrechetCellFilter"
- ComparisonConfig: lattice_tolerance_pct=2.0, volume_tolerance_pct=5.0,
  bond_cutoff=3.0, symprec=0.1
- ValidationConfig: min_bond_length=1.0, max_bond_length=4.0,
  max_lattice_deviation_pct=2.0, max_volume_deviation_pct=5.0
- ReportConfig (minimal for MVP)
- BenchmarkConfig (benchmark_name default, materials list)
- CacheConfig: ttl_days=30

File: cathodescope/config/settings.py

- CathodescopeSettings top-level model containing all sub-configs
- Loads from JSON file (path from CATHODESCOPE_CONFIG env var or default)
- Merges JSON overrides with defaults
- MP_API_KEY read from MP_API_KEY environment variable, never hardcoded
- get_settings() function: creates and returns settings instance
- config_snapshot() method: returns full config as dict for provenance

Constraints:
- Do NOT hardcode the MP API key anywhere
- Do NOT import from cathodescope.tools
- fmax must be positive, max_steps must be >= 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Ensure all config models have clear docstrings
- Extract validation logic if repeated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT hardcode API keys
- Do NOT import from cathodescope.tools
- Do NOT modify model files from P-01 through P-04

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_config/ -v              → 17 pass
  pytest tests/                                   → 0 failures
  ruff check cathodescope/config/                 → clean
  mypy cathodescope/config/                       → clean

Expected: Settings loaded without a config file use all defaults.
Expected: JSON override file changes specific values while keeping defaults for the rest.
Expected: Missing MP_API_KEY raises a clear, actionable error message.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 17 configuration tests (P-05 RED)
  feat: implement config defaults and settings loader (P-05 GREEN)
~~~

---

## Wave 2: Scientific Workflow Core

---

### P-06: Artifact / Provenance Store

~~~text
TASK: P-06 — Artifact / Provenance Store
PREREQUISITES: P-02 (result models), P-04 (report/benchmark models), P-05 (config)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/artifact_schema.md — Section 3 (Directory Layout), Section 6 (Immutability Rules), Section 7 (Completeness Checklist)
- docs/dependency_graph.md — Section 6 (provenance imports only from models)
- cathodescope/provenance/store.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_provenance/test_store.py

Tests to write (17 total):
- test_store_write_canonical_material(tmp_path)
- test_store_read_canonical_material(tmp_path)
- test_store_write_workflow_result(tmp_path)
- test_store_read_workflow_result(tmp_path)
- test_store_write_step_results(tmp_path)
- test_store_write_report(tmp_path)
- test_store_write_benchmark_row(tmp_path)
- test_store_write_benchmark_summary(tmp_path)
- test_store_directory_structure_matches_schema(tmp_path)
    → verify paths: materials/{id}/canonical.json, workflows/{id}/result.json, etc.
- test_store_files_are_read_only_after_write(tmp_path)
    → file permissions set to 0o444
- test_store_overwrite_raises_artifact_error(tmp_path)
    → second write to same path raises error
- test_store_write_provenance_json_convenience_copy(tmp_path)
    → provenance.json written alongside primary record
- test_store_integrity_check_passes_when_complete(tmp_path)
- test_store_integrity_check_fails_when_file_missing(tmp_path)
- test_store_json_uses_2_space_indent(tmp_path)
- test_store_cache_write_and_read(tmp_path)
- test_store_cache_overwrite_is_allowed(tmp_path)
    → cache is exception to immutability

Run: pytest tests/unit/test_provenance/test_store.py — expect 17 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement ArtifactStore

File: cathodescope/provenance/store.py

Implement ArtifactStore class:
- __init__(self, root_dir: Path)
- write(artifact_type, id, data) — writes JSON to correct path per artifact_schema.md Section 3
- read(artifact_type, id) — reads and returns parsed JSON
- exists(artifact_type, id) — checks if file exists
- verify_integrity(workflow_run_id) — checks all expected files exist per Section 7 checklist

Directory layout per artifact_schema.md Section 3:
  artifacts/
  ├── materials/{material_id}/canonical.json, structures/original.json, normalized.json, relaxed.json
  ├── workflows/{workflow_run_id}/result.json, steps/00_resolve.json, ...
  ├── reports/{report_id}/report.json, report.md
  ├── benchmarks/{benchmark_run_id}/summary.json, rows/{material_id}.json
  └── cache/mp/{mp_id}_{fields_hash}.json

Rules:
- Set file permissions to read-only after write: os.chmod(path, 0o444)
- Cache directory is exception: overwrites allowed
- JSON serialization uses json.dumps(data, indent=2)
- Attempting to overwrite non-cache artifact raises ArtifactError
- Write provenance.json convenience copy at each directory level

Constraints:
- Do NOT import from cathodescope.tools or cathodescope.workflows
- Import only from cathodescope.models

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract path-building logic into private helper methods
- Ensure consistent error messages for all failure modes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from cathodescope.tools or cathodescope.workflows
- Do NOT modify any model files
- Do NOT change the directory layout from artifact_schema.md Section 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_provenance/test_store.py -v   → 17 pass
  pytest tests/                                         → 0 failures
  ruff check cathodescope/provenance/store.py           → clean
  mypy cathodescope/provenance/store.py                 → clean

Expected: Directory structure matches artifact_schema.md Section 3 exactly.
Expected: Overwrite attempt on non-cache artifact raises ArtifactError.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 17 artifact store tests (P-06 RED)
  feat: implement ArtifactStore with immutability and integrity checks (P-06 GREEN)
~~~

---

### P-07: MP Client and Fixture Capture

~~~text
TASK: P-07 — MP Client and Fixture Capture
PREREQUISITES: P-02 (ToolResult), P-05 (config for API key, cache settings)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-07 section
- docs/artifact_schema.md — Section 5 (Caching Strategy)
- docs/benchmark_spec.md — Section 3 (materials: mp-22526, mp-19017, mp-18767)
- cathodescope/tools/mp_client.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_tools/test_mp_client.py

Tests to write (16 total) — all mock MPRester, never hit live API:
- test_mp_client_fetch_by_mp_id_returns_tool_result()
- test_mp_client_fetch_by_mp_id_evidence_type_is_a_retrieved()
- test_mp_client_fetch_by_formula_returns_tool_result()
- test_mp_client_data_contains_structure_dict()
    → data["structure"] has keys "lattice" and "sites"
- test_mp_client_data_contains_metadata()
- test_mp_client_metadata_has_required_fields()
    → mp_id, formula, space_group, energy_per_atom, formation_energy_per_atom, band_gap
- test_mp_client_handles_not_found_error()
    → returns ToolResult with status "error" and RetrievalError
- test_mp_client_handles_api_timeout()
- test_mp_client_handles_rate_limit()
- test_mp_client_uses_cache_when_available()
- test_mp_client_writes_cache_after_fetch()
- test_mp_client_cache_key_format()
    → {mp_id}_{fields_hash}.json
- test_mp_client_provenance_records_api_version()
- test_mp_client_licoo2_fixture_loads_correctly()
- test_mp_client_lifepo4_fixture_loads_correctly()
- test_mp_client_limn2o4_fixture_loads_correctly()

Run: pytest tests/unit/test_tools/test_mp_client.py — expect 16 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement MP Client

File: cathodescope/tools/mp_client.py

Implement CathodescopeMPClient class:
- __init__(self, api_key: str, cache_dir: Path | None = None)
- fetch_by_mp_id(mp_id: str) -> ToolResult
- fetch_by_formula(formula: str) -> ToolResult

Behavior:
- Use mp-api MPRester for real retrieval
- Check cache first (cache_dir / f"{mp_id}_{fields_hash}.json")
- On cache miss: fetch from API, write to cache, return result
- On cache hit: load from cache, return result
- Return ToolResult with evidence_type "A-retrieved"
- data dict contains: structure (pymatgen as_dict), metadata (mp_id, formula, space_group, etc.)
- Error handling: not found → RetrievalError, timeout → RetrievalError, rate limit → RetrievalError

File: scripts/capture_fixtures.py
- Script to capture real MP responses for 3 benchmark materials
- Run once with live API key, store results in tests/fixtures/mp_responses/
- Creates: mp-22526.json, mp-19017.json, mp-18767.json

Create fixture files (from live API or hand-craft valid structures):
- tests/fixtures/mp_responses/mp-22526.json (LiCoO2)
- tests/fixtures/mp_responses/mp-19017.json (LiFePO4)
- tests/fixtures/mp_responses/mp-18767.json (LiMn2O4)

Constraints:
- Unit tests must NEVER hit the live MP API — mock MPRester
- Do NOT import from other tools
- Return ToolResult for all code paths (success, error, cache hit)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract cache logic into private methods
- Ensure consistent error messages

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from other cathodescope.tools modules
- Do NOT hardcode API keys
- Do NOT modify model files or config files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_tools/test_mp_client.py -v   → 16 pass
  pytest tests/                                        → 0 failures
  ruff check cathodescope/tools/mp_client.py           → clean
  mypy cathodescope/tools/mp_client.py                 → clean

Expected: Fixture files contain valid pymatgen Structure.as_dict() data for all 3 benchmark materials.
Expected: Cache hit returns same data as fresh fetch.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 16 MP client tests (P-07 RED)
  feat: implement MP client with caching and fixture capture (P-07 GREEN)
  chore: add MP fixture files for 3 benchmark materials
~~~

---

### P-08: Input Resolver

~~~text
TASK: P-08 — Input Resolver
PREREQUISITES: P-03 (NormalizedQuery model), P-07 (MP client)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-08 section
- cathodescope/models/material.py (NormalizedQuery)
- cathodescope/tools/mp_client.py (fetch functions)
- cathodescope/tools/input_resolver.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_tools/test_input_resolver.py

Tests to write (12 total) — all mock MP client:
- test_resolve_formula_licoo2_returns_normalized_query()
- test_resolve_formula_lifepo4_returns_normalized_query()
- test_resolve_mp_id_returns_normalized_query()
- test_resolve_invalid_formula_raises_input_error()
- test_resolve_empty_string_raises_input_error()
- test_resolve_invalid_mp_id_format_raises_input_error()
- test_resolve_preserves_raw_input()
- test_resolve_source_type_is_formula_for_formula_input()
- test_resolve_source_type_is_mp_id_for_mp_id_input()
- test_resolve_populates_reduced_formula()
- test_resolve_uses_mp_client_for_formula_lookup()
- test_resolve_returns_tool_result_wrapper()

Run: pytest tests/unit/test_tools/test_input_resolver.py — expect 12 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Input Resolver

File: cathodescope/tools/input_resolver.py

Implement resolve(raw_input: str, mp_client) -> ToolResult:
- Detect input type: mp-id (regex r"mp-\d+") vs formula
- For formula: validate with pymatgen Composition, call mp_client to resolve to mp_id
- For mp_id: validate format
- Create NormalizedQuery with all fields populated
- Return ToolResult with NormalizedQuery.model_dump() in data field
- Invalid input → ToolResult with status "error" and InputError details

Constraints:
- Do NOT import from other tools besides mp_client (injected as parameter)
- Mock MP client in all unit tests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from other tools besides mp_client
- Do NOT modify model files or mp_client.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_tools/test_input_resolver.py -v   → 12 pass
  pytest tests/                                             → 0 failures
  ruff check cathodescope/tools/input_resolver.py           → clean
  mypy cathodescope/tools/input_resolver.py                 → clean

Expected: "LiCoO2" resolves correctly.
Expected: "mp-22526" resolves correctly.
Expected: Invalid inputs produce InputError with clear, actionable messages.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 12 input resolver tests (P-08 RED)
  feat: implement input resolver for formula and mp-id (P-08 GREEN)
~~~

---

### P-08b: Family Classification Function

~~~text
TASK: P-08b — Family Classification Function
PREREQUISITES: P-03 (CanonicalMaterial model)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-08b section
- docs/benchmark_spec.md — Section 2 (cathode families: R-3m layered, Pnma olivine, Fd-3m spinel)
- cathodescope/models/material.py (CanonicalMaterial with family field)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_models/test_material.py (extend existing file)

Tests to add (5 total):
- test_classify_family_layered_oxide_r3m_limio2()
    → R-3m + LiMO2 composition → "layered_oxide"
- test_classify_family_olivine_pnma_limpo4()
    → Pnma + LiMPO4 → "olivine_polyanion"
- test_classify_family_spinel_fd3m_lim2o4()
    → Fd-3m + LiM2O4 → "spinel"
- test_classify_family_unknown_returns_other()
    → unrecognized combination → "other"
- test_classify_family_case_insensitive()

Run: pytest tests/unit/test_models/test_material.py — new tests FAIL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement classify_family

File: cathodescope/models/material.py (add function to existing file)

Implement classify_family(space_group: str, formula: str) -> str:
- Rules:
  - R-3m + LiMO2 pattern → "layered_oxide"
  - Pnma + LiMPO4 pattern → "olivine_polyanion"
  - Fd-3m + LiM2O4 pattern → "spinel"
  - Everything else → "other"
- Case-insensitive matching for space group strings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT modify other model files
- Do NOT import from tools or config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_models/test_material.py -v   → all pass (16 + 5 = 21)
  pytest tests/                                        → 0 failures
  ruff check cathodescope/models/material.py           → clean
  mypy --strict cathodescope/models/material.py        → clean

Expected: All 3 benchmark materials classified correctly.
Expected: Unknown composition returns "other".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 5 family classification tests (P-08b RED)
  feat: implement classify_family function (P-08b GREEN)
~~~

---

### P-09: Structure Normalizer

~~~text
TASK: P-09 — Structure Normalizer
PREREQUISITES: P-02 (ToolResult), P-07 (fixture structures to normalize)
WAVE: 2
⚠️  SCIENTIFIC REVIEW CHECKPOINT after this prompt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-09 section
- docs/scientific_validity_matrix.md — Row 2 (Normalized Crystal Structure)
  Allowed wording: "Structure normalized to conventional standard setting using pymatgen"
  Disallowed wording: "Optimized structure", "Corrected structure"
- tests/fixtures/mp_responses/ (fixture structures from P-07)
- cathodescope/tools/structure_normalizer.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_tools/test_structure_normalizer.py

Tests to write (14 total) — use real pymatgen, not mocks:
- test_normalize_licoo2_preserves_space_group()   → R-3m preserved
- test_normalize_licoo2_returns_conventional_cell()
- test_normalize_licoo2_atom_count_is_12()
- test_normalize_lifepo4_preserves_space_group()  → Pnma preserved
- test_normalize_lifepo4_atom_count_is_28()
- test_normalize_limn2o4_preserves_space_group()  → Fd-3m preserved
- test_normalize_limn2o4_atom_count_is_56()
- test_normalize_returns_tool_result()
- test_normalize_evidence_type_is_a_computed()
- test_normalize_data_contains_space_group_info()
- test_normalize_data_contains_wyckoff_positions()
- test_normalize_data_contains_transformation_matrix()
- test_normalize_data_contains_atom_counts_before_after()
- test_normalize_degenerate_structure_raises_computation_error()

Run: pytest tests/unit/test_tools/test_structure_normalizer.py — expect 14 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Structure Normalizer

File: cathodescope/tools/structure_normalizer.py

Implement normalize(structure_dict: dict, symprec: float = 0.1) -> ToolResult:
- Convert structure_dict to pymatgen Structure via Structure.from_dict()
- Use pymatgen.symmetry.analyzer.SpacegroupAnalyzer(structure, symprec=symprec)
- Call get_conventional_standard_structure()
- Verify atom count consistency
- Return ToolResult with evidence_type "A-computed"
- data dict contains:
  - structure: conventional structure as_dict()
  - space_group_before: original space group symbol
  - space_group_after: conventional cell space group symbol
  - space_group_number: international number
  - wyckoff_positions: list of wyckoff symbols
  - transformation_matrix: 3x3 matrix as list of lists
  - atom_count_before: int
  - atom_count_after: int

Create normalized structure fixture files:
- tests/fixtures/structures/licoo2_conventional.json
- tests/fixtures/structures/lifepo4_conventional.json
- tests/fixtures/structures/limn2o4_conventional.json

Scientific wording constraint (validity_matrix.md Row 2):
- In any output strings, use "normalized to conventional standard setting"
- Never use "optimized" or "corrected"

Constraints:
- Do NOT import from other tools
- Do NOT mock pymatgen — use real structures from fixtures

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract space group analysis into a helper if repeated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from other tools
- Do NOT mock pymatgen — use real structures
- Do NOT modify fixture files from P-07

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_tools/test_structure_normalizer.py -v   → 14 pass
  pytest tests/                                                   → 0 failures
  ruff check cathodescope/tools/structure_normalizer.py           → clean
  mypy cathodescope/tools/structure_normalizer.py                 → clean

Expected: LiCoO2: R-3m preserved, 12 atoms in conventional cell.
Expected: LiFePO4: Pnma preserved, 28 atoms.
Expected: LiMn2O4: Fd-3m preserved, 56 atoms.

⚠️  SCIENTIFIC REVIEW CHECKPOINT:
Verify space group preservation logic against scientific_validity_matrix.md Row 2.
Confirm all 3 benchmark materials produce correct space groups.
Do NOT proceed to P-10 until this review is complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 14 structure normalizer tests (P-09 RED)
  feat: implement structure normalizer with pymatgen (P-09 GREEN)
  chore: add normalized structure fixtures for 3 benchmark materials
~~~

---

### P-10: Structure Relaxer (Unit Tests with Mock Calculator)

~~~text
TASK: P-10 — Structure Relaxer (Unit Tests with Mock Calculator)
PREREQUISITES: P-02 (ToolResult), P-05 (RelaxationConfig), P-09 (normalized structures)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-10 section
- docs/scientific_validity_matrix.md — Row 3 (Relaxed Crystal Structure)
  Allowed wording: "Structure relaxed using MACE-MP-0 with convergence threshold fmax = X eV/Angstrom"
  Disallowed wording: "DFT-relaxed", "Experimentally validated", "Ground-state", "Optimized" (without method)
- cathodescope/config/defaults.py (RelaxationConfig)
- cathodescope/tools/structure_relaxer.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_tools/test_structure_relaxer.py

All tests use a MockCalculator (defined in the test file) — NEVER real MACE.

Tests to write (19 total):
- test_relax_returns_tool_result()
- test_relax_evidence_type_is_a_computed()
- test_relax_data_contains_relaxed_structure()
- test_relax_data_contains_final_energy()
- test_relax_data_contains_final_fmax()
- test_relax_data_contains_convergence_info()
- test_relax_convergence_info_has_converged_flag()
- test_relax_convergence_info_has_steps_count()
- test_relax_convergence_info_has_energy_history()
- test_relax_convergence_info_has_fmax_history()
- test_relax_non_convergence_returns_warning_status()
- test_relax_divergence_raises_computation_error()
- test_relax_nan_forces_raises_computation_error()
- test_relax_excessive_volume_change_raises_validation_error()
    → volume change > 50% triggers error
- test_relax_structure_collapse_raises_validation_error()
    → bond length < 0.5 Å triggers error
- test_relax_respects_fmax_config()
- test_relax_respects_max_steps_config()
- test_relax_with_cell_relaxation_enabled()
- test_relax_provenance_records_mace_model_version()

Define MockCalculator in the test file:
- Returns pre-defined energies and forces
- Supports convergence scenario (decreasing forces)
- Supports non-convergence scenario (forces stay high)
- Supports divergence scenario (NaN forces)

Run: pytest tests/unit/test_tools/test_structure_relaxer.py — expect 19 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Structure Relaxer

File: cathodescope/tools/structure_relaxer.py

Implement relax(structure_dict: dict, config: RelaxationConfig, calculator=None) -> ToolResult:
- CRITICAL: Accept calculator as parameter (dependency injection) for testing
- In production, if calculator is None, create MACE calculator from config
- Convert pymatgen Structure to ASE Atoms
- Attach calculator
- Run ASE FIRE optimizer with FrechetCellFilter (if relax_cell=True)
- Track energy and fmax at each step for convergence history
- Convert back to pymatgen Structure
- Return ToolResult with evidence_type "A-computed"
- data dict contains:
  - relaxed_structure: as_dict()
  - final_energy: float (eV)
  - final_fmax: float (eV/Å)
  - convergence: {converged: bool, steps: int, energy_history: list, fmax_history: list}
  - volume_change_pct: float

Error handling:
- Non-convergence (max_steps reached): return ToolResult with status "warning"
- NaN forces: raise ComputationError
- Divergence: raise ComputationError
- Volume change > 50%: raise ValidationError
- Bond length < 0.5 Å: raise ValidationError

Scientific wording constraint (validity_matrix.md Row 3):
- Use "relaxed using MACE-MP-0" in any output strings
- Never use "DFT-relaxed" or "ground-state"

Constraints:
- Do NOT import from other tools
- Do NOT test with real MACE — that is P-20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract convergence tracking into a helper class/function
- Clean up ASE ↔ pymatgen conversion code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT test with real MACE in this task
- Do NOT import from other tools
- Do NOT modify config or model files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_tools/test_structure_relaxer.py -v   → 19 pass
  pytest tests/                                                → 0 failures
  ruff check cathodescope/tools/structure_relaxer.py           → clean
  mypy cathodescope/tools/structure_relaxer.py                 → clean

Expected: Convergence and non-convergence paths both tested.
Expected: Error paths (NaN forces, divergence, collapse) all tested.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 19 structure relaxer tests with mock calculator (P-10 RED)
  feat: implement structure relaxer with dependency-injected calculator (P-10 GREEN)
~~~

---

### P-11: Reference Comparator

~~~text
TASK: P-11 — Reference Comparator
PREREQUISITES: P-02 (ToolResult), P-09 (normalized structures for fixtures)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-11 section
- docs/scientific_validity_matrix.md — Row 6 (Lattice Parameter Deviation)
  Allowed wording: "Lattice parameter a deviates by X% from MP reference value (mp-XXXXX)"
  Disallowed wording: "Error in lattice parameter", "Lattice parameter matches experiment"
- docs/benchmark_spec.md — Section 4 (deviation formulas and thresholds)
- cathodescope/tools/reference_comparator.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

IMPORTANT: Use the word "deviation" throughout, NEVER "error" — per scientific_validity_matrix.md Rule 6.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_tools/test_reference_comparator.py

Tests to write (12 total):
- test_compare_identical_structures_zero_deviation()
- test_compare_lattice_deviations_a_b_c()
- test_compare_lattice_deviations_angles()
- test_compare_volume_deviation()
- test_compare_symmetry_preserved_when_same()
- test_compare_symmetry_broken_when_different()
- test_compare_returns_tool_result()
- test_compare_evidence_type_is_a_compared()
- test_compare_data_contains_all_required_fields()
    → lattice_deviations, volume_deviation, symmetry_preserved, bond_length_stats
- test_compare_mismatched_compositions_raises_error()
- test_compare_deviation_formula_is_correct()
    → |relaxed - reference| / reference * 100
- test_compare_known_deviation_hand_computed()
    → Create two structures with known 1% lattice stretch, verify comparator returns 1.0%

Run: pytest tests/unit/test_tools/test_reference_comparator.py — expect 12 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Reference Comparator

File: cathodescope/tools/reference_comparator.py

Implement compare(relaxed_dict: dict, reference_dict: dict, config: ComparisonConfig) -> ToolResult:
- Convert dicts to pymatgen Structure objects
- Lattice deviation: |relaxed - reference| / reference * 100 per parameter (a, b, c)
- Angle deviation: |relaxed_angle - reference_angle| in degrees (α, β, γ)
- Volume deviation: |V_relaxed - V_reference| / V_reference * 100
- Symmetry: SpacegroupAnalyzer on both, compare space group symbols
- Bond lengths: compute min and max interatomic distances in relaxed structure
- Return ToolResult with evidence_type "A-compared"
- data dict contains:
  - lattice_deviations: {a_pct: float, b_pct: float, c_pct: float}
  - angle_deviations: {alpha_deg: float, beta_deg: float, gamma_deg: float}
  - volume_deviation_pct: float
  - symmetry_preserved: bool
  - space_group_relaxed: str
  - space_group_reference: str
  - min_bond_length: float
  - max_bond_length: float

CRITICAL: Use "deviation" in ALL variable names, data keys, and output strings.
NEVER use "error" for numerical differences.

Constraints:
- Do NOT import from other tools
- Do NOT use "error" for deviations in any variable name or data key

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract lattice comparison into a helper if code is lengthy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from other tools
- Do NOT use "error" for deviations — always "deviation"
- Do NOT modify normalizer or relaxer files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_tools/test_reference_comparator.py -v   → 12 pass
  pytest tests/                                                   → 0 failures
  ruff check cathodescope/tools/reference_comparator.py           → clean
  mypy cathodescope/tools/reference_comparator.py                 → clean

Expected: Hand-computed deviation values match programmatic values to within pytest.approx(0.001).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 12 reference comparator tests (P-11 RED)
  feat: implement reference comparator with deviation calculations (P-11 GREEN)
~~~

---

### P-12: Validation Layer (Structural + Convergence Checks)

~~~text
TASK: P-12 — Validation Layer (Structural + Convergence Checks)
PREREQUISITES: P-02 (ToolResult for check result types)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-12 section
- docs/dependency_graph.md — Section 6 (validation imports only from models, not from tools)
- docs/benchmark_spec.md — Section 4 (threshold values)
- cathodescope/validation/structural.py (currently empty)
- cathodescope/validation/convergence.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_validation/test_structural.py

Tests (8):
- test_bond_length_check_passes_normal_structure()
- test_bond_length_check_fails_collapsed_structure()   → bond < 1.0 Å
- test_bond_length_check_fails_exploded_structure()    → bond > 4.0 Å
- test_min_bond_length_threshold_is_configurable()
- test_max_bond_length_threshold_is_configurable()
- test_atom_overlap_check_detects_overlapping_atoms()
- test_coordination_check_returns_coordination_numbers()
- test_structural_checks_return_check_result_list()

File: tests/unit/test_validation/test_convergence.py

Tests (8):
- test_fmax_check_passes_when_below_threshold()
- test_fmax_check_fails_when_above_threshold()
- test_energy_monotonicity_passes_decreasing_energy()
- test_energy_monotonicity_fails_oscillating_energy()
- test_energy_monotonicity_tolerance_is_configurable()
- test_step_count_check_passes_within_limit()
- test_step_count_check_warns_near_limit()         → steps > 0.8 * max_steps
- test_convergence_checks_return_check_result_list()

Run: pytest tests/unit/test_validation/ — expect 16 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Validation Functions

File: cathodescope/validation/structural.py

Each check function returns a CheckResult dict:
  {"check_name": str, "category": str, "passed": bool, "value": Any,
   "threshold": Any, "message": str}

Functions:
- check_bond_lengths(structure_dict, min_bond=1.0, max_bond=4.0) -> list[CheckResult]
- check_atom_overlaps(structure_dict, overlap_threshold=0.5) -> list[CheckResult]
- check_coordination(structure_dict, cutoff=3.0) -> list[CheckResult]
- run_structural_checks(structure_dict, config) -> list[CheckResult]

File: cathodescope/validation/convergence.py

Functions:
- check_fmax(final_fmax, threshold) -> CheckResult
- check_energy_monotonicity(energy_history, tolerance=1e-4) -> CheckResult
- check_step_count(steps, max_steps) -> CheckResult
- run_convergence_checks(convergence_data, config) -> list[CheckResult]

File: cathodescope/validation/family_specific.py

Stubs only:
- run_family_checks(material_family, data) -> list[CheckResult]
  Returns empty list for MVP. Mark with comment: # EXPAND IN PHASE 4

Constraints:
- Validation functions depend ONLY on cathodescope.models — pure functions on data
- Do NOT import from cathodescope.tools or cathodescope.config
- All results are structured dicts, NOT free-form strings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract common CheckResult construction into a helper

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from cathodescope.tools or cathodescope.config
- Do NOT produce free-form text — all results are structured
- Do NOT implement family-specific checks beyond stubs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_validation/test_structural.py -v    → 8 pass
  pytest tests/unit/test_validation/test_convergence.py -v   → 8 pass
  pytest tests/                                               → 0 failures
  ruff check cathodescope/validation/                         → clean
  mypy cathodescope/validation/                               → clean

Expected: Check results are structured dicts, not free-form strings.
Expected: Every check has a human-readable message field.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 16 validation layer tests (P-12 RED)
  feat: implement structural and convergence validation checks (P-12 GREEN)
~~~

---

### P-13: Evidence Label Assigner

~~~text
TASK: P-13 — Evidence Label Assigner
PREREQUISITES: P-02 (ToolResult for evidence_type enum values)
WAVE: 2
⚠️  SCIENTIFIC REVIEW CHECKPOINT after this prompt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/scientific_validity_matrix.md — Section 2 (Evidence Level Definitions), Section 3 Part A (all 14 rows)
- docs/tdd_task_breakdown.md — T-13 section
- cathodescope/validation/evidence.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

CRITICAL: This module is the single source of truth for evidence label assignment.
No tool should assign its own labels — all label logic lives here.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_validation/test_evidence.py

Tests to write (14 total):
- test_label_retrieved_data_as_a_retrieved()
    → step "fetch_structure" → "A-retrieved"
- test_label_normalized_structure_as_a_computed()
    → step "normalize" → "A-computed"
- test_label_relaxed_structure_as_a_computed()
    → step "relax" → "A-computed"
- test_label_comparison_result_as_a_compared()
    → step "compare_reference" → "A-compared"
- test_label_validation_result_as_a_compared()
    → step "validate" → "A-compared"
- test_label_summary_inherits_weakest_level()
- test_label_summary_all_level_a_returns_level_a()
- test_label_summary_mixed_a_and_b_returns_level_b()
- test_label_summary_any_level_c_returns_level_c()
- test_assign_evidence_labels_returns_list_of_label_dicts()
- test_evidence_label_dict_has_output_name()
- test_evidence_label_dict_has_evidence_type()
- test_evidence_label_dict_has_rationale()
- test_label_relaxed_structure_as_b_restricted_for_non_benchmarked_family()
    → non-benchmarked family → "B-restricted" instead of "A-computed"

Run: pytest tests/unit/test_validation/test_evidence.py — expect 14 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Evidence Label Assigner

File: cathodescope/validation/evidence.py

Functions:
- assign_evidence_label(output_name: str, step_name: str,
    material_family: str = "", is_benchmarked_family: bool = True) -> dict
  Returns: {"output_name": ..., "evidence_type": ..., "rationale": ...}

- compute_summary_evidence_level(labels: list[str]) -> str
  Returns the weakest level present.

Step-to-label mapping:
  fetch_structure      → A-retrieved
  normalize            → A-computed
  relax                → A-computed (if benchmarked family) or B-restricted (if not)
  compare_reference    → A-compared
  validate             → A-compared

Level hierarchy: A-retrieved = A-computed = A-compared > B-restricted > C-proxy

Benchmarked families: layered_oxide, olivine_polyanion, spinel
Non-benchmarked families: everything else → B-restricted for relax step

Constraints:
- Do NOT hardcode labels inside tool implementations
- All label logic MUST live in this module
- Do NOT import from cathodescope.tools

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT put label logic in tool implementations
- Do NOT import from cathodescope.tools
- Do NOT modify other validation files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_validation/test_evidence.py -v   → 14 pass
  pytest tests/                                            → 0 failures
  ruff check cathodescope/validation/evidence.py           → clean
  mypy cathodescope/validation/evidence.py                 → clean

Expected: Label assignment is deterministic given step name and material family.
Expected: Summary inheritance follows weakest-level rule.

⚠️  SCIENTIFIC REVIEW CHECKPOINT:
Verify ALL labels match scientific_validity_matrix.md Section 3 Part A rows 1–8:
  Row 1: Crystal Structure Retrieved → A-retrieved
  Row 2: Normalized Structure → A-computed
  Row 3: Relaxed Structure (MACE) → A-computed
  Row 4: Relaxed Lattice Parameters → A-computed
  Row 5: Convergence Metadata → A-computed
  Row 6: Lattice Parameter Deviation → A-compared
  Row 7: Bond Length Comparison → A-compared
  Row 8: Symmetry Preservation → A-compared
Do NOT proceed to P-14 until this review is complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 14 evidence label tests (P-13 RED)
  feat: implement evidence label assigner (P-13 GREEN)
~~~

---

### P-14: Physics Validator Tool

~~~text
TASK: P-14 — Physics Validator Tool
PREREQUISITES: P-12 (structural + convergence checks), P-13 (evidence labels), P-05 (ValidationConfig)
WAVE: 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-14 section
- cathodescope/validation/structural.py (check functions)
- cathodescope/validation/convergence.py (check functions)
- cathodescope/validation/evidence.py (label assignment)
- cathodescope/tools/physics_validator.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_tools/test_physics_validator.py

Tests to write (12 total):
- test_validator_returns_tool_result()
- test_validator_evidence_type_is_a_compared()
- test_validator_data_contains_checks_list()
- test_validator_data_contains_evidence_labels_list()
- test_validator_data_contains_overall_sanity_bool()
- test_validator_all_checks_pass_for_valid_data()
- test_validator_detects_bond_length_failure()
- test_validator_detects_convergence_failure()
- test_validator_detects_symmetry_break()
- test_validator_returns_warnings_for_soft_failures()
- test_validator_critical_failure_sets_overall_sanity_false()
- test_validator_evidence_labels_match_validity_matrix()

Run: pytest tests/unit/test_tools/test_physics_validator.py — expect 12 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Physics Validator

File: cathodescope/tools/physics_validator.py

Implement validate(context: dict, material: dict, config) -> ToolResult:
- Accept accumulated step results (context dict) + CanonicalMaterial dict + ValidationConfig
- Delegate to validation.structural, validation.convergence, validation.evidence
- Aggregate check results and evidence labels into a single ToolResult
- Return ToolResult with evidence_type "A-compared"
- data dict contains:
  - checks: list of CheckResult dicts
  - evidence_labels: list of label dicts from evidence assigner
  - overall_sanity: bool (True only if all critical checks pass)

Constraints:
- Do NOT duplicate check logic — always delegate to the validation layer
- Do NOT import from other tools

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT duplicate validation logic — delegate
- Do NOT import from other tools
- Do NOT modify validation layer files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_tools/test_physics_validator.py -v   → 12 pass
  pytest tests/                                                → 0 failures
  ruff check cathodescope/tools/physics_validator.py           → clean
  mypy cathodescope/tools/physics_validator.py                 → clean

Expected: Valid data produces overall_sanity: True.
Expected: Invalid data produces specific check failures with structured messages.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 12 physics validator tests (P-14 RED)
  feat: implement physics validator tool (P-14 GREEN)
~~~

---

## Wave 3: Reporting and Integration

---

### P-15: JSON Report Builder

~~~text
TASK: P-15 — JSON Report Builder
PREREQUISITES: P-04 (ReportRecord, ReportSection), P-02 (WorkflowResult)
WAVE: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-15 section
- docs/artifact_schema.md — Section 2.4 (ReportRecord, ReportSection)
- docs/scientific_validity_matrix.md — Section 5 (report format requirements)
- cathodescope/reporting/json_report.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_reporting/test_json_report.py

Tests to write (12 total):
- test_build_json_report_returns_report_record()
- test_json_report_has_all_required_sections()
    → material_summary, retrieved_data, normalization, relaxation, comparison, validation, evidence_summary, provenance
- test_json_report_material_summary_section()
- test_json_report_retrieved_data_section()
- test_json_report_normalization_section()
- test_json_report_relaxation_section()
- test_json_report_comparison_section()
- test_json_report_validation_section()
- test_json_report_evidence_summary_section()
- test_json_report_provenance_section()
- test_json_report_evidence_summary_counts()
    → {"A-retrieved": N, "A-computed": N, "A-compared": N}
- test_json_report_serializes_to_valid_json()

Run: pytest tests/unit/test_reporting/test_json_report.py — expect 12 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement JSON Report Builder

File: cathodescope/reporting/json_report.py

Implement build_json_report(workflow_result: WorkflowResult, material: CanonicalMaterial, raw_user_input: str = "") -> ReportRecord:
- Create one ReportSection per workflow step + summary + provenance sections
- Section order: material_summary, retrieved_data, normalization, relaxation, comparison, validation, evidence_summary, provenance
- Each section's evidence_labels list populated from step evidence types
- evidence_summary: aggregate count {"A-retrieved": N, "A-computed": N, "A-compared": N}
- ReportRecord.raw_user_input populated from parameter

Constraints:
- Do NOT import from cathodescope.tools
- Report builder operates on model objects, not tool internals

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract section builders into private helper functions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from cathodescope.tools
- Do NOT modify model files
- Do NOT add Markdown rendering logic here (that's P-16)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_reporting/test_json_report.py -v   → 12 pass
  pytest tests/                                              → 0 failures
  ruff check cathodescope/reporting/json_report.py           → clean
  mypy cathodescope/reporting/json_report.py                 → clean

Expected: Report sections follow the order defined in the spec.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 12 JSON report builder tests (P-15 RED)
  feat: implement JSON report builder (P-15 GREEN)
~~~

---

### P-16: Markdown Report Renderer

~~~text
TASK: P-16 — Markdown Report Renderer
PREREQUISITES: P-15 (JSON report builder), P-04 (ReportRecord)
WAVE: 3
⚠️  SCIENTIFIC REVIEW CHECKPOINT after this prompt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/scientific_validity_matrix.md — Section 4 (ALL 10 Wording Rules) and Section 5 (Mock Report Excerpt)
- docs/tdd_task_breakdown.md — T-16 section
- cathodescope/reporting/markdown_report.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

CRITICAL: The Markdown output must match the mock excerpt in scientific_validity_matrix.md Section 5 EXACTLY.
All 10 wording rules from Section 4 must be enforced.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_reporting/test_markdown_report.py

Tests to write (13 total):
- test_render_markdown_returns_string()
- test_markdown_contains_title()
- test_markdown_section_headers_include_evidence_level()
    → format: "### Retrieved Reference Data [Level A -- retrieved]"
- test_markdown_retrieved_data_section_has_level_a_retrieved()
- test_markdown_relaxation_section_has_level_a_computed()
- test_markdown_comparison_section_has_level_a_compared()
- test_markdown_contains_mp_id()
- test_markdown_contains_mace_version()
- test_markdown_contains_convergence_details()
    → steps, final fmax, convergence status
- test_markdown_contains_lattice_deviations()
    → percentage deviations with reference named
- test_markdown_assessment_paragraph_summarizes_evidence()
- test_markdown_no_disallowed_words()
    → regex check: no "validated structure", "discovered", "proved stable",
      "accurate" without qualification, "error" for deviations,
      "optimized" without method, "ground-truth"
- test_markdown_matches_validity_matrix_format()
    → section structure matches the mock excerpt

Run: pytest tests/unit/test_reporting/test_markdown_report.py — expect 13 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Markdown Renderer

File: cathodescope/reporting/markdown_report.py

Implement render_markdown(report: ReportRecord) -> str:
- Generate Markdown string from structured ReportRecord
- Section header format: "### {heading} [Level {level} -- {subtype}]"

Enforce ALL 10 wording rules from scientific_validity_matrix.md Section 4:
  Rule 1: Include method and version (e.g., "MACE-MP-0 (v0.3.6)")
  Rule 2: Include MP ID (e.g., "mp-22526"), never just formula
  Rule 3: Include quantitative thresholds (e.g., "within 2%")
  Rule 4: Include evidence level in every section header
  Rule 5: Never "validated" without specification
  Rule 6: Never "discovered" for known materials
  Rule 7: Never "proved" for computational results
  Rule 8: Never "accurate" without a reference
  Rule 9: Never drop caveats from Level B/C
  Rule 10: Never mix evidence levels without labeling

Use "deviation" not "error" for numerical differences.
Use "normalized to conventional standard setting" not "optimized" or "corrected".

Constraints:
- Do NOT parse JSON report as text — use structured ReportRecord object
- Do NOT use vague language ("good agreement") — always quantitative values
- Do NOT import from cathodescope.tools

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract section renderers into private functions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from cathodescope.tools
- Do NOT modify json_report.py
- Do NOT use disallowed wording from the validity matrix

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_reporting/test_markdown_report.py -v   → 13 pass
  pytest tests/                                                  → 0 failures
  ruff check cathodescope/reporting/markdown_report.py           → clean
  mypy cathodescope/reporting/markdown_report.py                 → clean

Expected: Markdown format matches scientific_validity_matrix.md Section 5 mock excerpt.

⚠️  SCIENTIFIC REVIEW CHECKPOINT:
Compare generated Markdown output against the mock report in scientific_validity_matrix.md Section 5.
Verify all 10 wording rules are enforced.
Verify no disallowed words appear in output.
Do NOT proceed to P-17 until this review is complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 13 Markdown report tests (P-16 RED)
  feat: implement Markdown renderer with wording rules (P-16 GREEN)
~~~

---

### P-17: Report Generator Tool

~~~text
TASK: P-17 — Report Generator Tool
PREREQUISITES: P-15 (JSON builder), P-16 (Markdown renderer), P-02 (ToolResult)
WAVE: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-17 section
- cathodescope/reporting/json_report.py (build_json_report)
- cathodescope/reporting/markdown_report.py (render_markdown)
- cathodescope/tools/report_generator.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_tools/test_report_generator.py

Tests to write (7 total):
- test_report_generator_returns_tool_result()
- test_report_generator_evidence_type_is_metadata()
    → report generation is metadata, not scientific data
- test_report_generator_data_contains_report_json()
- test_report_generator_data_contains_report_markdown()
- test_report_generator_data_contains_evidence_summary()
- test_report_generator_handles_missing_step_data()
- test_report_generator_provenance_is_populated()

Run: pytest tests/unit/test_tools/test_report_generator.py — expect 7 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Report Generator Tool

File: cathodescope/tools/report_generator.py

Implement generate_report(workflow_result, material, raw_user_input="") -> ToolResult:
- Thin wrapper: calls reporting.json_report.build_json_report() and reporting.markdown_report.render_markdown()
- Wraps both outputs in a ToolResult
- evidence_type: use a special value or exclude from evidence summary
  (report generation does not produce scientific data)
- data dict contains:
  - report_record: ReportRecord.model_dump()
  - report_markdown: str
  - evidence_summary: dict

No business logic of its own — pure delegation.

Constraints:
- Do NOT duplicate reporting logic
- Thin wrapper only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected — already thin.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT duplicate reporting logic
- Do NOT modify reporting layer files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_tools/test_report_generator.py -v   → 7 pass
  pytest tests/                                               → 0 failures
  ruff check cathodescope/tools/report_generator.py           → clean
  mypy cathodescope/tools/report_generator.py                 → clean

Expected: Report generator is a thin wrapper — no business logic duplication.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 7 report generator tool tests (P-17 RED)
  feat: implement report generator tool wrapper (P-17 GREEN)
~~~

---

### P-18: Workflow Base Classes and Engine

~~~text
TASK: P-18 — Workflow Base Classes and Engine
PREREQUISITES: P-02 (WorkflowResult, StepResult), P-05 (config)
WAVE: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-18 section
- docs/dependency_graph.md — Section 1 (orchestration layer depends on models, tools, validation)
- cathodescope/workflows/base.py (currently empty)
- cathodescope/workflows/engine.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_workflows/test_engine.py

Tests to write (17 total) — all use mock step functions:

Registry tests:
- test_workflow_registry_register_and_get()
- test_workflow_registry_list_workflows()
- test_workflow_registry_unknown_workflow_raises_error()
- test_workflow_context_accumulates_step_results()
- test_workflow_context_read_by_step_name()

Engine tests:
- test_engine_executes_steps_in_order()
- test_engine_passes_context_between_steps()
- test_engine_returns_workflow_result()
- test_engine_records_timestamps()
- test_engine_records_runtime_seconds()
- test_engine_captures_config_snapshot()
- test_engine_handles_step_failure_gracefully()
- test_engine_stores_partial_results_on_failure()
- test_engine_classifies_hard_failure()
- test_engine_classifies_soft_failure()
- test_engine_classifies_success()
- test_engine_never_swallows_errors()
- test_engine_provenance_is_populated()

Run: pytest tests/unit/test_workflows/test_engine.py — expect 17 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Workflow Engine

File: cathodescope/workflows/base.py

- WorkflowRegistry: dict mapping workflow_name → WorkflowDefinition
- WorkflowDefinition: name, version, list of StepSpec (name, callable, config_key)
- Global registry instance

File: cathodescope/workflows/engine.py

- WorkflowContext: typed dataclass with fields:
  material, normalized_query, step_results: dict[str, StepResult],
  config, workflow_run_id, started_at
- WorkflowEngine class:
  - run(workflow_name, material, config) -> WorkflowResult
  - Executes steps in order, passing context between them
  - Records timestamps and runtime_seconds
  - Captures config_snapshot
  - On step failure: store partial results, classify failure
  - Error classification:
    ComputationError with recoverable=False → hard_failure
    Borderline convergence → soft_failure
    All steps pass → success
  - Never swallow errors — always record in WorkflowResult

Constraints:
- Engine is tool-agnostic — NO imports from cathodescope.tools in engine.py
- Engine receives callables, not tool modules
- No scientific logic in the engine
- Use mock step functions in unit tests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract step execution loop logic
- Clean up error classification code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT put scientific logic in the engine
- Do NOT import specific tools in engine.py
- Do NOT modify model or tool files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_workflows/test_engine.py -v   → 17 pass
  pytest tests/                                         → 0 failures
  ruff check cathodescope/workflows/                    → clean
  mypy cathodescope/workflows/                          → clean

Expected: Engine is tool-agnostic — no imports from cathodescope.tools in engine.py.
Expected: Partial results preserved on failure (no data loss).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 17 workflow engine tests (P-18 RED)
  feat: implement workflow registry, context, and engine (P-18 GREEN)
~~~

---

### P-19: structural_analysis Workflow Definition

~~~text
TASK: P-19 — structural_analysis Workflow Definition
PREREQUISITES: P-18 (engine), all tools P-07 through P-17
WAVE: 3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-19 section
- docs/artifact_schema.md — Section 3 (step file naming: 00_resolve, 01_fetch, etc.)
- cathodescope/workflows/engine.py (WorkflowRegistry, WorkflowDefinition)
- cathodescope/workflows/structural_analysis.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_workflows/test_structural_analysis.py

Tests to write (7 total) — all tools mocked:
- test_structural_analysis_is_registered_in_registry()
- test_structural_analysis_has_correct_step_count()   → 7 steps
- test_structural_analysis_step_order_is_correct()
    → resolve_input, fetch_structure, normalize, relax, compare_reference, validate, generate_report
- test_structural_analysis_step_names_match_spec()
- test_structural_analysis_version_is_1_0_0()
- test_structural_analysis_uses_correct_tool_for_each_step()
- test_structural_analysis_passes_context_correctly()

Run: pytest tests/unit/test_workflows/test_structural_analysis.py — expect 7 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Workflow Definition

File: cathodescope/workflows/structural_analysis.py

Register structural_analysis v1.0.0 in the WorkflowRegistry.

Steps in order:
  0. resolve_input     → calls tools.input_resolver.resolve
  1. fetch_structure   → calls tools.mp_client.fetch
  2. normalize         → calls tools.structure_normalizer.normalize
  3. relax             → calls tools.structure_relaxer.relax
  4. compare_reference → calls tools.reference_comparator.compare
  5. validate          → calls tools.physics_validator.validate
  6. generate_report   → calls tools.report_generator.generate_report

Each step is a thin wrapper that extracts data from context and calls the corresponding tool function.

Constraints:
- Do NOT put validation or comparison logic here — delegate to tools
- Step names must match artifact_schema.md Section 3 naming

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT put scientific logic in this file
- Do NOT modify engine.py or tool files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_workflows/test_structural_analysis.py -v   → 7 pass
  pytest tests/                                                      → 0 failures
  ruff check cathodescope/workflows/structural_analysis.py           → clean
  mypy cathodescope/workflows/structural_analysis.py                 → clean

Expected: Step names match spec and artifact_schema.md Section 3 step file naming.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 7 structural_analysis workflow tests (P-19 RED)
  feat: register structural_analysis workflow with 7 steps (P-19 GREEN)
~~~

---

### P-20: Integration Test — LiCoO2 Single-Material Pipeline

~~~text
TASK: P-20 — Integration Test — LiCoO2 Single-Material Pipeline
PREREQUISITES: All tasks P-00 through P-19
WAVE: 3
⚠️  SCIENTIFIC REVIEW CHECKPOINT after this prompt
⚠️  STOP CONDITION: Verify MACE-MP-0 installs before running

THIS IS AN INTEGRATION TEST PROMPT — modified template (no RED/GREEN split).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-20 section
- docs/benchmark_spec.md — Section 4 (thresholds: <2% lattice, <5% volume)
- docs/scientific_validity_matrix.md — Rows 1-8 (all MVP evidence types)
- tests/integration/test_single_material_pipeline.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5
  python -c "import mace; print('MACE available')"

⚠️  STOP CONDITION (SC-01): Before proceeding, verify:
1. MACE-MP-0 installs on the dev machine
2. A single-point energy calculation on LiCoO2 completes without error
If MACE does not install: debug PyTorch/MACE compatibility. Try CPU-only install.
Do NOT proceed until MACE single-point energy returns a finite value.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. WRITE INTEGRATION TESTS

File: tests/integration/test_single_material_pipeline.py

All tests marked with @pytest.mark.integration.
Uses cached MP fixture for structure retrieval (no live API).
Uses REAL MACE-MP-0 for relaxation.
Stores artifacts to tmp_path.

Tests to write (14 total):
- test_licoo2_end_to_end_produces_workflow_result()
- test_licoo2_workflow_status_is_success()
- test_licoo2_all_steps_completed()                    → 7 steps
- test_licoo2_lattice_deviation_a_below_2_percent()
- test_licoo2_lattice_deviation_c_below_2_percent()
- test_licoo2_volume_deviation_below_5_percent()
- test_licoo2_symmetry_preserved()                     → R-3m preserved
- test_licoo2_report_generated()
- test_licoo2_all_evidence_labels_are_level_a()
- test_licoo2_artifacts_stored_correctly()
- test_licoo2_provenance_complete()
- test_licoo2_rerun_produces_same_result_category()
    → Execute pipeline twice, compare status and result categories
- test_licoo2_end_to_end_runs_offline()
    → Runs pipeline with network mocked/disabled, using cached fixtures only
- test_licoo2_integrity_check_passes()
    → Verifies post-run integrity check from artifact_schema.md Section 7

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. RUN AND FIX

Run: pytest tests/integration/test_single_material_pipeline.py -v -m integration

This is the first real MACE computation. If tests fail:
- Check MACE model version and installation
- Check that MP fixtures load correctly
- Check normalization (primitive vs conventional cell mismatch)
- Check relaxation parameters (fmax, max_steps)
- Fix production code to make tests pass

Do NOT mock MACE in this test — real computation is the point.
Do NOT skip the rerun reproducibility check.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. WHAT NOT TO CHANGE

- Do NOT mock MACE
- Do NOT lower thresholds to make tests pass
- Do NOT skip reproducibility check
- Do NOT modify unit tests from previous prompts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. VERIFICATION

Run:
  pytest tests/integration/test_single_material_pipeline.py -v   → 14 pass
  pytest tests/ -m "not integration"                              → all previous tests still pass
  ruff check tests/integration/                                   → clean

Expected: LiCoO2 lattice parameter a within 2% of ~2.836 Å
Expected: LiCoO2 lattice parameter c within 2% of ~14.083 Å
Expected: Volume deviation below 5%
Expected: Space group R-3m preserved
Expected: All evidence labels are Level A

⚠️  STOP CONDITION (SC-02):
Verify LiCoO2 relaxed lattice parameters deviate < 2% from MP reference.
If deviation > 2%: check normalization, MACE version, relaxation parameters.
Do NOT proceed until confirmed.

⚠️  SCIENTIFIC REVIEW CHECKPOINT:
This is the Phase 1 acceptance test from master_plan.md Section 3.
Verify all scientific outputs match expectations.
Do NOT proceed to P-21 until review is complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. COMMIT

  test: add 14 LiCoO2 integration tests with real MACE (P-20)
  fix: [any production code fixes needed to pass integration tests]
~~~

---

### P-21: Integration Test — LiFePO4 and LiMn2O4

~~~text
TASK: P-21 — Integration Test — LiFePO4 and LiMn2O4
PREREQUISITES: P-20 (LiCoO2 passes)
WAVE: 3

THIS IS AN INTEGRATION TEST PROMPT — modified template (no RED/GREEN split).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-21 section
- docs/benchmark_spec.md — Sections 3.2 (LiFePO4) and 3.3 (LiMn2O4)
- tests/integration/test_single_material_pipeline.py (extend existing file)

Run:
  pytest tests/integration/test_single_material_pipeline.py -v
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. WRITE INTEGRATION TESTS

File: tests/integration/test_single_material_pipeline.py (extend existing)

All tests marked with @pytest.mark.integration.
Use pytest.mark.parametrize where possible to reduce duplication.

Tests to add (8 total):

LiFePO4 tests (should achieve Full Success):
- test_lifepo4_end_to_end_produces_workflow_result()
- test_lifepo4_lattice_deviations_below_threshold()   → all < 2%
- test_lifepo4_symmetry_preserved()                    → Pnma preserved
- test_lifepo4_report_generated()

LiMn2O4 tests (may achieve Partial Success — Jahn-Teller effects):
- test_limn2o4_end_to_end_produces_workflow_result()
- test_limn2o4_completes_without_hard_failure()
    → status is "success" OR "partial_success" — not "hard_failure"
- test_limn2o4_report_generated()
- test_limn2o4_failure_classified_if_partial()
    → if partial_success, failure category is documented

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. RUN AND FIX

Run: pytest tests/integration/test_single_material_pipeline.py -v -m integration

IMPORTANT SCIENTIFIC NOTES:
- LiFePO4 should achieve Full Success (orthorhombic olivine, well-behaved)
- LiMn2O4 MAY achieve Partial Success due to Jahn-Teller effects on Mn³⁺
- A Partial Success on LiMn2O4 is a VALID SCIENTIFIC FINDING
- Do NOT expect all 3 to achieve Full Success
- Do NOT lower thresholds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. WHAT NOT TO CHANGE

- Do NOT expect LiMn2O4 Full Success — accept Partial Success
- Do NOT lower thresholds to make tests pass
- Do NOT modify LiCoO2 tests from P-20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. VERIFICATION

Run:
  pytest tests/integration/ -v -m integration   → 22 pass (14 + 8)
  pytest tests/ -m "not integration"            → all unit tests still pass

Expected: At least 2 of 3 materials achieve Full Success.
Expected: LiMn2O4 at least Partial Success.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. COMMIT

  test: add 8 LiFePO4 and LiMn2O4 integration tests (P-21)
  fix: [any production code fixes needed]
~~~

---

## Wave 4: Benchmark

---

### P-22: Benchmark Registry

~~~text
TASK: P-22 — Benchmark Registry
PREREQUISITES: P-03 (CanonicalMaterial)
WAVE: 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-22 section
- docs/benchmark_spec.md — Section 3 (3 shortlisted materials)
- cathodescope/benchmark/registry.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_benchmark/test_registry.py

Tests to write (8 total):
- test_registry_contains_3_phase1_materials()
- test_registry_licoo2_entry_correct()
    → formula: LiCoO2, mp_id: mp-22526, family: layered_oxide
- test_registry_lifepo4_entry_correct()
    → formula: LiFePO4, mp_id: mp-19017, family: olivine_polyanion
- test_registry_limn2o4_entry_correct()
    → formula: LiMn2O4, mp_id: mp-18767, family: spinel
- test_registry_get_by_name_returns_material_set()
    → get_materials("phase1_structural_analysis") returns 3 entries
- test_registry_unknown_benchmark_raises_error()
- test_registry_materials_have_correct_families()
- test_registry_materials_have_benchmark_tags()
    → all tagged with "phase1"

Run: pytest tests/unit/test_benchmark/test_registry.py — expect 8 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Registry

File: cathodescope/benchmark/registry.py

Implement BenchmarkMaterialRegistry class:
- get_materials(benchmark_name: str) -> list[dict]
- Phase 1 benchmark: "phase1_structural_analysis"
- 3 entries:
  {"formula": "LiCoO2", "mp_id": "mp-22526", "family": "layered_oxide", "benchmark_tags": ["phase1"]}
  {"formula": "LiFePO4", "mp_id": "mp-19017", "family": "olivine_polyanion", "benchmark_tags": ["phase1"]}
  {"formula": "LiMn2O4", "mp_id": "mp-18767", "family": "spinel", "benchmark_tags": ["phase1"]}

Constraints:
- Do NOT hardcode material data in the runner — keep it in the registry

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT put material data in the runner
- Do NOT modify model or tool files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_benchmark/test_registry.py -v   → 8 pass
  pytest tests/                                           → 0 failures
  ruff check cathodescope/benchmark/registry.py           → clean
  mypy cathodescope/benchmark/registry.py                 → clean

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 8 benchmark registry tests (P-22 RED)
  feat: implement benchmark material registry (P-22 GREEN)
~~~

---

### P-23: Benchmark Runner

~~~text
TASK: P-23 — Benchmark Runner
PREREQUISITES: P-18 (engine), P-22 (registry), P-04 (BenchmarkRow/Summary), P-06 (store)
WAVE: 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-23 section
- docs/benchmark_spec.md — Section 4 (all 24 metrics), Section 5 (classification rules)
- cathodescope/benchmark/runner.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_benchmark/test_runner.py

Tests to write (13 total) — all use mock engine:
- test_runner_processes_all_materials()
- test_runner_returns_benchmark_summary()
- test_runner_summary_has_correct_materials_count()
- test_runner_summary_has_status_counts()
- test_runner_produces_benchmark_row_per_material()
- test_runner_row_contains_all_metrics()
    → all 24 metrics from benchmark_spec.md Section 4:
      input_resolution, structure_retrieval, structure_normalization,
      space_group_input, relaxation_convergence, relaxation_steps,
      final_fmax, final_energy, lattice_param_deviation_a,
      lattice_param_deviation_b, lattice_param_deviation_c,
      angle_deviation_alpha, angle_deviation_beta, angle_deviation_gamma,
      volume_deviation, symmetry_preserved, space_group_output, symprec_used,
      min_bond_length, max_bond_length, evidence_labeling_complete,
      report_generated, runtime_seconds, workflow_version
- test_runner_isolates_material_failures()
- test_runner_continues_after_single_material_failure()
- test_runner_classifies_failure_categories()
    → per benchmark_spec.md Section 5 threshold table
- test_runner_stores_artifacts()
- test_runner_records_timestamps()
- test_runner_records_runtime()
- test_runner_provenance_is_populated()

Run: pytest tests/unit/test_benchmark/test_runner.py — expect 13 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Benchmark Runner

File: cathodescope/benchmark/runner.py

Implement BenchmarkRunner class:
- run(benchmark_name: str, config) -> BenchmarkSummary
- Iterate registry materials, call workflow engine for each
- Collect WorkflowResult, extract ALL 24 metrics into BenchmarkRow.metrics
- Failure isolation: try/except per material, classify exception, continue
- Status classification per benchmark_spec.md Section 5:
  Formal threshold table determines classification:
  - Full Success: all lattice <2%, volume <5%, angles <1°, symmetry preserved, bonds OK
  - Partial Success: lattice 2-5%, volume 5-10%, angles 1-3°
  - Soft Failure: lattice 5-10%, volume 10-20%, angles >3°, symmetry broken
  - Hard Failure: lattice >10% or NaN, diverged
  - Infrastructure Failure: network/disk/dependency issues
- classify_benchmark_status(metrics) independent of WorkflowResult.status
- Store results via ArtifactStore

Constraints:
- Do NOT import from cathodescope.tools directly — go through workflow engine
- Single material failure does NOT abort entire benchmark

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract metric extraction logic into a helper
- Extract status classification into a standalone function

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT import from cathodescope.tools directly
- Do NOT modify engine, registry, or model files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_benchmark/test_runner.py -v   → 13 pass
  pytest tests/                                         → 0 failures
  ruff check cathodescope/benchmark/runner.py           → clean
  mypy cathodescope/benchmark/runner.py                 → clean

Expected: Single material failure does not abort entire benchmark.
Expected: All 24 metrics from benchmark_spec.md Section 4 present in each BenchmarkRow.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 13 benchmark runner tests (P-23 RED)
  feat: implement benchmark runner with metric extraction and classification (P-23 GREEN)
~~~

---

### P-24: Benchmark Runner Integration Test

~~~text
TASK: P-24 — Benchmark Runner Integration Test
PREREQUISITES: P-21 (all 3 materials pass individually), P-23 (runner unit tests pass)
WAVE: 4
⚠️  SCIENTIFIC REVIEW CHECKPOINT after this prompt
⚠️  STOP CONDITIONS apply

THIS IS AN INTEGRATION TEST PROMPT — modified template.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-24 section
- docs/benchmark_spec.md — Section 6 (Phase 1 criteria: 2/3 Full Success)
- tests/integration/test_benchmark_suite.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. WRITE INTEGRATION TESTS

File: tests/integration/test_benchmark_suite.py

All tests marked with @pytest.mark.integration.

Tests to write (8 total):
- test_benchmark_phase1_runs_all_3_materials()
- test_benchmark_at_least_2_full_success()
    → per benchmark_spec.md Section 6
- test_benchmark_no_hard_failures()
- test_benchmark_summary_generated()
- test_benchmark_rows_stored()
- test_benchmark_metrics_complete()
    → all 24 metrics populated for every material
- test_benchmark_reproducible_on_rerun()
    → run twice, compare result categories; lattice deviations agree within 0.1%
- test_benchmark_evidence_labeling_complete_for_all()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. RUN AND FIX

Run: pytest tests/integration/test_benchmark_suite.py -v -m integration

⚠️  STOP CONDITION (SC-05):
If fewer than 2 Full Success: investigate before proceeding.
For LiMn2O4 Jahn-Teller: document as expected Partial Success, do NOT lower thresholds.
For unexpected failures: debug the pipeline.

⚠️  STOP CONDITION (SC-06):
Verify reproducibility: re-run produces same result category for each material.
Lattice deviations agree within 0.1% between runs.
If not: set OMP_NUM_THREADS=1 and MKL_NUM_THREADS=1, investigate non-determinism.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. WHAT NOT TO CHANGE

- Do NOT lower thresholds to make tests pass
- Do NOT skip the reproducibility check
- Do NOT modify unit tests from previous prompts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. VERIFICATION

Run:
  pytest tests/integration/test_benchmark_suite.py -v   → 8 pass
  pytest tests/ -m "not integration"                     → all unit tests still pass

Expected: At least 2/3 Full Success.
Expected: No Hard Failures.
Expected: Reproducible on rerun.
Expected: Phase 2 gate criteria met.

⚠️  SCIENTIFIC REVIEW CHECKPOINT:
Review benchmark results against ALL benchmark_spec.md Section 4 thresholds.
Verify all metrics make physical sense.
This is the Phase 2 gate test.
Do NOT proceed to P-24b until review is complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. COMMIT

  test: add 8 benchmark integration tests with real MACE (P-24)
  fix: [any production code fixes needed]
~~~

---

### P-24b: Benchmark Regression Comparison Tool

~~~text
TASK: P-24b — Benchmark Regression Comparison Tool
PREREQUISITES: P-23 (BenchmarkRunner), P-04 (BenchmarkSummary)
WAVE: 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-24b section
- cathodescope/models/reports.py (BenchmarkSummary)
- cathodescope/benchmark/runner.py (existing runner)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_benchmark/test_comparator.py

Tests to write (6 total):
- test_compare_benchmarks_detects_status_change()
    → material goes from success to partial_success → detected
- test_compare_benchmarks_computes_metric_deltas()
    → lattice deviation delta computed correctly
- test_compare_benchmarks_flags_new_failures()
- test_compare_benchmarks_flags_new_successes()
- test_compare_benchmarks_returns_regression_report()
    → RegressionReport with status_changes, metric_deltas, new_failures, new_successes
- test_compare_benchmarks_handles_missing_material()
    → material in one but not the other → flagged

Run: pytest tests/unit/test_benchmark/test_comparator.py — expect 6 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement Comparator

File: cathodescope/benchmark/comparator.py

Implement compare_benchmarks(summary_a: BenchmarkSummary, summary_b: BenchmarkSummary) -> RegressionReport:
- RegressionReport (dataclass or pydantic model):
  - status_changes: list of {material_id, old_status, new_status}
  - metric_deltas: dict of {material_id: {metric_name: delta}}
  - new_failures: list of material_ids that went from success to any failure
  - new_successes: list of material_ids that went from failure to success
  - missing_materials: list of material_ids in one but not the other

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT modify runner.py or registry.py
- Do NOT modify model files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_benchmark/test_comparator.py -v   → 6 pass
  pytest tests/                                             → 0 failures
  ruff check cathodescope/benchmark/comparator.py           → clean
  mypy cathodescope/benchmark/comparator.py                 → clean

Expected: Status changes between benchmark runs detected and reported.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 6 benchmark comparator tests (P-24b RED)
  feat: implement benchmark regression comparison tool (P-24b GREEN)
~~~

---

## Wave 5: CLI

---

### P-25: CLI Interface

~~~text
TASK: P-25 — CLI Interface
PREREQUISITES: P-19 (structural_analysis workflow), P-23 (benchmark runner)
WAVE: 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-25 section
- docs/demo_strategy.md — Demo 3 (3-minute formula→report demo)
- cathodescope/app/cli.py (currently empty)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/integration/test_cli.py

Tests to write (7 total):
- test_cli_analyze_command_exists()
- test_cli_analyze_licoo2_produces_report()
    → cathodescope analyze LiCoO2 → report path on stdout
- test_cli_analyze_invalid_formula_shows_error()
- test_cli_benchmark_command_exists()
- test_cli_benchmark_runs_phase1()
    → cathodescope benchmark --name phase1_structural_analysis → summary
- test_cli_help_shows_usage()
- test_cli_version_shows_version()
    → cathodescope --version → "0.1.0"

Run: pytest tests/integration/test_cli.py — expect 7 FAILURES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Implement CLI

File: cathodescope/app/cli.py

Use argparse (zero extra dependencies).

Commands:
- cathodescope analyze <formula_or_mp_id>
  → runs structural_analysis workflow, outputs report path to stdout
- cathodescope benchmark [--name phase1_structural_analysis]
  → runs benchmark, outputs summary path to stdout
- cathodescope --version
  → prints version string

Behavior:
- Progress output to stderr so report path goes to stdout cleanly
- Error messages to stderr with non-zero exit code
- Entry point in pyproject.toml: [project.scripts] cathodescope = "cathodescope.app.cli:main"

Constraints:
- Do NOT put business logic in CLI — delegate to workflows and benchmark runner
- CLI is a thin wrapper

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None expected.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT put business logic in CLI
- Do NOT modify workflow or benchmark files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/integration/test_cli.py -v   → 7 pass
  pytest tests/                              → 0 failures
  ruff check cathodescope/app/cli.py         → clean
  mypy cathodescope/app/cli.py               → clean

Expected: 3-minute demo completable per demo_strategy.md Demo 3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 7 CLI tests (P-25 RED)
  feat: implement CLI with analyze and benchmark commands (P-25 GREEN)
~~~

---

## Wave 6: Thesis-Core Hardening

---

### P-26: Pre-commit and CI Configuration

~~~text
TASK: P-26 — Pre-commit and CI Configuration
PREREQUISITES: P-00 (project skeleton exists)
WAVE: 6

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-26 section
- .pre-commit-config.yaml (exists from P-00, finalize now)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — N/A (infrastructure task)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Configure CI

File: .pre-commit-config.yaml (finalize)

Hooks:
- ruff check
- ruff format --check
- mypy

File: .github/workflows/ci.yml (create)

GitHub Actions CI workflow:
- Trigger: push to main, pull requests
- Python 3.11
- Steps:
  1. pip install -e ".[dev]"
  2. pytest --cov=cathodescope -m "not integration" (skip MACE tests)
  3. ruff check cathodescope/ tests/
  4. mypy cathodescope/
- CI uses cached MP fixtures, not live API
- Integration tests marked @pytest.mark.integration are skipped in CI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT skip linting or type checking in CI
- Do NOT modify test files or production code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pre-commit run --all-files              → passes
  cat .github/workflows/ci.yml            → valid YAML

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  chore: finalize pre-commit hooks and add CI workflow (P-26)
~~~

---

### P-27: Import Rule Enforcement Tests

~~~text
TASK: P-27 — Import Rule Enforcement Tests
PREREQUISITES: All previous tasks (enforces rules across full codebase)
WAVE: 6

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/dependency_graph.md — Section 6 (Import Dependency Rules table)
- tests/test_import_rules.py (placeholder from P-00)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests (if any violations exist)

File: tests/test_import_rules.py (replace placeholder)

Tests to write (10 total) — use ast.parse() to inspect imports:
- test_models_do_not_import_from_cathodescope_tools()
- test_models_do_not_import_from_cathodescope_config()
- test_tools_do_not_import_from_each_other()
    → each tool only imports from models, config, and external libs
- test_validation_does_not_import_from_tools()
- test_validation_does_not_import_from_workflows()
- test_reporting_does_not_import_from_tools()
- test_reporting_does_not_import_from_workflows()
- test_provenance_does_not_import_from_tools()
- test_benchmark_does_not_import_from_tools_directly()
- test_agent_directory_is_empty()

Implementation:
- Use ast.parse() to parse each source file's AST
- Check Import and ImportFrom nodes for forbidden module paths
- For each rule in dependency_graph.md Section 6:
  | Module | Must NOT Import From |
  |--------|---------------------|
  | models/* | Any cathodescope module |
  | config/* | tools/*, workflows/*, validation/* |
  | tools/* | Other tools/* modules, workflows/*, benchmark/* |
  | validation/* | tools/*, workflows/*, config/* |
  | reporting/* | tools/*, workflows/*, validation/* |
  | provenance/* | Everything except models/* |
  | benchmark/* | tools/* directly, agent/* |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Fix Any Violations

If any import rule violations are found, fix them in the production code.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract AST inspection logic into a reusable helper function

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT use runtime import checking — use AST inspection
- Do NOT weaken import rules

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/test_import_rules.py -v   → 10 pass
  pytest tests/                           → 0 failures

Expected: Any new import rule violation caught automatically in CI.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 10 import rule enforcement tests (P-27)
  fix: [any import violations corrected]
~~~

---

### P-28: Fixture Capture Script and Golden Output Generation

~~~text
TASK: P-28 — Fixture Capture Script and Golden Output Generation
PREREQUISITES: P-20 (LiCoO2 pipeline passes — outputs available)
WAVE: 6

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-28 section
- scripts/capture_fixtures.py (placeholder from P-07)
- tests/fixtures/ (existing fixture directories)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — N/A (tooling task)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Finalize Fixture Capture

File: scripts/capture_fixtures.py (finalize)

Script captures:
1. MP responses for 3 materials (if not already captured in P-07)
2. Normalized structures for 3 materials
3. One complete WorkflowResult for LiCoO2 (golden output)
4. One complete ReportRecord for LiCoO2 (golden output)
5. One BenchmarkSummary for Phase 1 benchmark (golden output)

Script features:
- --force flag for intentional re-capture
- Idempotent: re-running does not change committed fixtures unless forced
- Validates all generated JSON files

Create golden output files:
- tests/fixtures/expected_outputs/licoo2_workflow_result.json
- tests/fixtures/expected_outputs/licoo2_report.json
- tests/fixtures/expected_outputs/benchmark_summary.json

Golden outputs are frozen after first generation and committed to version control.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT modify production code
- Do NOT change fixture directory structure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  python scripts/capture_fixtures.py           → completes without error
  python -m json.tool tests/fixtures/expected_outputs/licoo2_workflow_result.json   → valid JSON
  python -m json.tool tests/fixtures/expected_outputs/licoo2_report.json            → valid JSON
  python -m json.tool tests/fixtures/expected_outputs/benchmark_summary.json        → valid JSON

Expected: All fixture files exist and contain valid JSON.
Expected: Script has --force flag for intentional re-capture.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  chore: finalize fixture capture script and generate golden outputs (P-28)
~~~

---

### P-29: Regression Tests

~~~text
TASK: P-29 — Regression Tests
PREREQUISITES: P-28 (golden outputs exist)
WAVE: 6

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-29 section
- tests/fixtures/expected_outputs/ (golden output files from P-28)

Run:
  pytest tests/ --tb=short
  git log --oneline -5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_regression.py

Tests to write (4 total):
- test_licoo2_workflow_result_matches_golden()
    → Load golden WorkflowResult, run pipeline with mock MACE (deterministic forces),
      compare key fields (status, step count, evidence types)
- test_licoo2_report_sections_match_golden()
    → Compare section headings, evidence labels exactly
- test_licoo2_evidence_summary_matches_golden()
    → Compare evidence_summary dict exactly
- test_benchmark_row_metrics_match_golden()
    → Compare metric keys and numerical values with pytest.approx(abs=0.01)

Implementation notes:
- Numerical comparisons: pytest.approx(abs=0.01)
- String fields: compared exactly
- Structural fields (section headings, evidence labels, metric keys): compared exactly
- Non-deterministic fields (UUIDs, timestamps): EXCLUDED from comparison

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Make Tests Pass

If regression tests fail, determine whether:
- The golden output needs updating (intentional change) → re-run capture script with --force
- The code has a regression (unintentional change) → fix the code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

- Extract golden output loading and comparison into a helper fixture

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT compare floating-point values with exact equality — use pytest.approx
- Do NOT compare UUIDs or timestamps
- Do NOT modify production code to match golden outputs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_regression.py -v   → 4 pass
  pytest tests/                              → 0 failures

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 4 regression tests against golden outputs (P-29)
~~~

---

## Wave 7: Agent Layer

---

### P-30: Agent Scaffolding (Empty Stubs)

~~~text
TASK: P-30 — Agent Scaffolding (Empty Stubs)
PREREQUISITES: P-18 (engine — agent depends on workflows/engine.py)
WAVE: 7

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0. ORIENTATION

Read:
- docs/tdd_task_breakdown.md — T-30 section
- docs/dependency_graph.md — Section 1 (agent layer: depends on workflows/engine.py and models/*, NOT on tools/*)
- cathodescope/agent/__init__.py (may exist from P-00 but needs content)

Run:
  pytest tests/ --tb=short
  git log --oneline -3

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RED — Write Failing Tests

File: tests/unit/test_agent.py (create new file)

Tests to write (2 total):
- test_agent_module_importable()
    → import cathodescope.agent succeeds
- test_agent_directory_contains_only_init()
    → only __init__.py exists in cathodescope/agent/

Run: pytest tests/unit/test_agent.py — expect FAILURES if not implemented

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. GREEN — Create Agent Stubs

File: cathodescope/agent/__init__.py

Content:
- Module docstring: "Agent orchestration layer. NOT IMPLEMENTED — Phase 5. Depends on workflows/engine.py and models/*. Does NOT depend on tools/* directly."
- __all__ = []
- No code beyond the docstring and __all__

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. REFACTOR

None — intentionally minimal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. WHAT NOT TO CHANGE

- Do NOT implement any agent functionality
- Do NOT add dependency on cathodescope.tools
- Do NOT add any files beyond __init__.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. VERIFICATION

Run:
  pytest tests/unit/test_agent.py -v   → 2 pass
  pytest tests/                         → 0 failures

Expected: No actual agent functionality exists.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. COMMIT

  test: add 2 agent module stub tests (P-30 RED)
  feat: create agent module stub with Phase 5 boundary docs (P-30 GREEN)
~~~

---

## Appendix A: Human Review Checklist

### Per-Prompt Checklist

After each prompt completes, verify:

- [ ] All new tests pass (`pytest` green)
- [ ] All previously passing tests still pass (no regressions)
- [ ] `ruff check cathodescope/ tests/` passes
- [ ] `mypy cathodescope/` passes
- [ ] Changes committed with correct conventional-commit prefix
- [ ] No `# TODO` comments remain in new code
- [ ] No hardcoded API keys or credentials
- [ ] Import rules respected (no cross-tool imports, etc.)

### Universal Quality Checks

- [ ] All public functions have docstrings
- [ ] All pydantic models have `model_config` with examples where appropriate
- [ ] Floating-point comparisons use `pytest.approx()` with documented tolerances
- [ ] UUIDs in tests use deterministic generator from conftest.py
- [ ] Timestamps in tests use frozen time (2026-01-01T00:00:00Z)

### Wave Gate Checks

| Wave | Gate Criterion |
|---|---|
| 0 | Package installable, test runner works, ruff + mypy pass |
| 1 | All 84+ model/config tests pass, every model round-trips through JSON |
| 2 | All ~130 tool/validation unit tests pass, scientific review checkpoints for P-09 and P-13 completed |
| 3 | Reports match validity matrix, LiCoO2 E2E passes, 3 materials tested, scientific review for P-16 and P-20 |
| 4 | 2/3 Full Success, benchmark reproducible, scientific review for P-24 |
| 5 | 3-minute CLI demo works |
| 6 | CI passes, >80% coverage, import rules enforced, regression tests pass |
| 7 | Agent stubs with correct docstrings and boundaries |

---

## Appendix B: Scientific Review Checklist

### Checkpoint 1: Space Group Preservation (after P-09)

- [ ] LiCoO2: R-3m (#166) preserved after normalization
- [ ] LiFePO4: Pnma (#62) preserved after normalization
- [ ] LiMn2O4: Fd-3m (#227) preserved after normalization
- [ ] Atom counts match expected conventional cell sizes (12, 28, 56)
- [ ] Reference: `scientific_validity_matrix.md` Row 2

### Checkpoint 2: Evidence Label Correctness (after P-13)

- [ ] Retrieved MP data → A-retrieved
- [ ] Normalized structure → A-computed
- [ ] MACE-relaxed structure → A-computed (benchmarked families)
- [ ] MACE-relaxed structure → B-restricted (non-benchmarked families)
- [ ] Lattice parameter deviation → A-compared
- [ ] Bond length comparison → A-compared
- [ ] Symmetry preservation → A-compared
- [ ] Summary inherits weakest constituent level
- [ ] Reference: `scientific_validity_matrix.md` Section 3 Part A, rows 1–8

### Checkpoint 3: Report Wording Compliance (after P-16)

- [ ] Section headers include evidence level: `[Level X -- subtype]`
- [ ] Method and version stated in every computational section
- [ ] MP ID stated in every reference data section
- [ ] Convergence details present for every relaxation
- [ ] Deviations reported as percentages with reference named
- [ ] Assessment paragraph summarizes evidence levels
- [ ] No disallowed words: "validated structure", "discovered", "proved stable", "accurate" (unqualified), "error" (for deviations), "optimized" (without method), "ground-truth"
- [ ] Reference: `scientific_validity_matrix.md` Section 4 (10 rules) and Section 5 (mock excerpt)

### Checkpoint 4: LiCoO2 Pipeline Accuracy (after P-20)

- [ ] Lattice parameter a within 2% of MP reference (~2.836 Å)
- [ ] Lattice parameter c within 2% of MP reference (~14.083 Å)
- [ ] Volume deviation below 5%
- [ ] Space group R-3m preserved after relaxation
- [ ] All evidence labels are Level A
- [ ] Report generated without errors
- [ ] Provenance complete (all fields populated)
- [ ] Rerun produces same result category
- [ ] Reference: `benchmark_spec.md` Section 4 thresholds

### Checkpoint 5: Full Benchmark Results (after P-24)

- [ ] At least 2 of 3 materials achieve Full Success
- [ ] Third material achieves at least Partial Success
- [ ] No Hard Failures
- [ ] All 24 metrics populated for every material
- [ ] Lattice deviations agree within 0.1% between reruns
- [ ] Same space groups reported on every run
- [ ] Evidence labeling complete for all materials
- [ ] Results make physical sense (LiMn2O4 harder than LiCoO2/LiFePO4 is expected)
- [ ] Reference: `benchmark_spec.md` Section 6

### Checkpoint 6: Phase 4 Coverage Gate (after all waves)

- [ ] `pytest --cov=cathodescope` shows >80% coverage for core modules
- [ ] Regression benchmark passes in CI
- [ ] External reviewer can reproduce results from documentation alone
- [ ] All validity matrix wording rules enforced in tests
- [ ] Import rules enforced via AST inspection
- [ ] All stop conditions (SC-01 through SC-07) resolved
- [ ] Reference: `tdd_task_breakdown.md` Section 6 (Stop Conditions)

---

*Every prompt in this document traces back to a task in `tdd_task_breakdown.md`. Every scientific constraint traces back to `scientific_validity_matrix.md`. Every threshold traces back to `benchmark_spec.md`. When in doubt, consult the source documents.*
