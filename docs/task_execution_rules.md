# CathodeScope — Task Execution Rules

**Version**: 1.0.0
**Last Updated**: 2026-03-11
**Status**: Active — Project Management Document
**Cross-References**: `planning/tdd_task_breakdown.md` (task definitions, Definition of Done), `planning/dependency_graph.md` (import rules), `planning/scientific_validity_matrix.md` (wording rules), `planning/artifact_schema.md` (directory layout), `task_board.md` (task statuses)

---

## 1. Task Selection Algorithm

When choosing the next task to work on, follow this algorithm:

```
1. FILTER: Select all tasks with Status = "Todo"
2. CHECK DEPS: From filtered set, keep only tasks whose dependencies are ALL "Done"
3. PRIORITY: Sort by Priority (P0 first, then P1, P2, P3)
4. TIEBREAK 1: Among same-priority tasks, prefer tasks on the critical path:
   T-00 → T-01 → T-02 → T-05 → T-07 → T-09 → T-10 → T-18 → T-19 → T-20 → T-23 → T-24
5. TIEBREAK 2: Among remaining ties, prefer smallest Size (XS < S < M < L)
6. SELECT: Take the first task from the sorted list
```

### Critical Path Tasks (P0)

These tasks form the critical path. Any delay on these delays the entire MVP:

T-00, T-01, T-02, T-05, T-07, T-09, T-10, T-18, T-19, T-20, T-21, T-23, T-24

### When to Deviate

You may deviate from the algorithm when:
- A task requires specialized knowledge or tools that are not currently available
- Two tasks can be worked in parallel by different contributors
- A blocking external dependency makes the selected task unworkable

Document any deviation in the task's Notes field.

---

## 2. Blocked Task Protocol

### When a Task is Blocked

1. **Switch**: Move to the next unblocked task per the selection algorithm
2. **Work on blocker**: If the blocker is another CathodeScope task, prioritize completing it
3. **Document external blockers**: If the blocker is external (API down, MACE install issue, etc.), record it:
   - Task ID
   - Blocker description
   - Date blocked
   - Resolution path
4. **Never idle**: There is always an unblocked task. If all tasks appear blocked, re-examine dependency chains — something may be unblocked that was overlooked.

### External Blocker Categories

| Category | Example | Resolution |
|----------|---------|------------|
| Dependency install | MACE-torch won't install | Check PyTorch version, try CPU-only, consult `tech_stack.md` |
| API access | MP API key expired / rate limited | Use cached fixtures, skip live tests |
| Hardware | GPU not available | Use CPU-only MACE, mark integration tests as slow |
| Knowledge gap | Unsure about scientific correctness | Consult `scientific_validity_matrix.md`, `subject_matter_expert_onboarding.md` |

---

## 3. Task Splitting Rules

Split a task if ANY of the following are true:

1. **Time**: Estimated effort exceeds 4 hours
2. **Scope**: Task touches more than 3 source files (not counting test files)
3. **Scientific checkpoint**: A scientific review is needed mid-task (e.g., normalizer output must be verified before comparator can use it)

### How to Split

1. Create sub-tasks with IDs like `T-XXa`, `T-XXb`
2. Each sub-task must independently satisfy the Definition of Done
3. Update `task_board.md` with the new sub-tasks
4. Preserve the original task's dependencies on all sub-tasks

---

## 4. Required Workflow Per Task

Every task follows this exact workflow. No shortcuts.

### Step 1: Read Docs
Read these documents before writing any code:
- The task card in `task_board.md`
- All files listed in the task's "Files affected" field
- The relevant section of `planning/tdd_task_breakdown.md` for full task details

### Step 2: Inspect Repository
- Check the current state of the codebase
- Verify all dependency tasks are Done (check `task_board.md`)
- Verify the modules this task depends on exist and are tested

### Step 3: RED (Write Failing Tests)
- Write ALL tests listed in the task's specification FIRST
- Run `pytest` — all new tests must FAIL (because production code doesn't exist yet)
- Commit with prefix `test:`
- **Hard rule**: No production code without a failing test first

### Step 4: GREEN (Write Minimum Implementation)
- Write the minimum production code to make tests pass
- No optimization, no refactoring, no "while I'm here" changes
- Run `pytest` — all tests must PASS
- Commit with prefix `feat:` or `fix:`

### Step 5: REFACTOR (Clean Up)
- Clean up production code (extract helpers, improve naming, add docstrings)
- Run `pytest` after every refactor step — tests must stay GREEN
- Commit with prefix `refactor:`

### Step 6: Quality Check
- `ruff check` passes on all new/modified files
- `mypy` passes (`--strict` for `models/` files)
- All public functions have docstrings
- No `# TODO` comments remain
- Import rules from `dependency_graph.md` Section 6 respected

### Step 7: Update Status
- Mark the task as Done in `task_board.md`
- Record completion date

### Step 8: Report Next
- Identify the next task using the selection algorithm (Section 1)
- Confirm its dependencies are all Done

---

## 5. Regression Test Rule

**After Wave 2+ tasks**: Run the full test suite (`pytest tests/`) after every task completion, not just the new task's tests.

This catches:
- Unexpected interactions between modules
- Import changes that break other modules
- Configuration changes that affect downstream tools

If the full suite fails, fix the regression BEFORE starting the next task.

---

## 6. Architecture Compatibility Rule

All code must respect the import rules defined in `planning/dependency_graph.md` Section 6:

| Module | May Import From | Must NOT Import From |
|--------|----------------|---------------------|
| `models/*` | Standard library, pydantic, pymatgen (Structure only) | Any `cathodescope` module |
| `config/*` | `models/*`, standard library, pydantic | `tools/*`, `workflows/*`, `validation/*` |
| `tools/*` | `models/*`, `config/*`, external libs | Other `tools/*` modules, `workflows/*`, `benchmark/*` |
| `validation/*` | `models/*`, pymatgen, numpy | `tools/*`, `workflows/*`, `config/*` |
| `reporting/*` | `models/*` | `tools/*`, `workflows/*`, `validation/*` |
| `workflows/*` | `models/*`, `tools/*`, `validation/*` | `benchmark/*`, `app/*`, `agent/*` |
| `provenance/*` | `models/*` | Everything else |
| `benchmark/*` | `models/*`, `workflows/*`, `provenance/*` | `tools/*` directly, `agent/*` |
| `app/*` | `workflows/*`, `benchmark/*` | `tools/*` directly |
| `agent/*` (future) | `models/*`, `workflows/engine.py` | `tools/*` directly |

**Critical rule**: A tool importing from another tool is a code review rejection. The agent never imports from `tools/*` directly.

---

## 7. Artifact Schema Compatibility Rule

All artifact storage must follow the directory layout defined in `planning/artifact_schema.md` Section 3:

```
artifacts/
├── materials/{material_id}/
│   ├── canonical.json
│   └── structures/
│       ├── original.json
│       ├── normalized.json
│       └── relaxed.json
├── workflows/{workflow_run_id}/
│   ├── result.json
│   └── steps/
│       ├── 00_resolve.json
│       ├── 01_fetch.json
│       └── ...
├── reports/{report_id}/
│   ├── report.json
│   └── report.md
├── benchmarks/{benchmark_run_id}/
│   ├── summary.json
│   └── rows/{material_id}.json
└── cache/mp/{mp_id}_{fields_hash}.json
```

- Files are read-only after write (except cache directory)
- JSON uses 2-space indent
- Overwrite attempts on non-cache artifacts raise `ArtifactError`

---

## 8. Scientific Wording Safety Rules

All CathodeScope outputs must follow these 10 rules from `planning/scientific_validity_matrix.md` Section 4. These are non-negotiable.

### Rule 1: Always State the Method
Write "structure relaxed using MACE-MP-0 (v0.3.6)", not just "relaxed structure".

### Rule 2: Always State the Reference
Write "compared against Materials Project mp-22526 (PBE+U)", not "compared against reference".

### Rule 3: Always State Thresholds
Write "within 2% of reference", not "close to reference" or "good agreement".

### Rule 4: Always State the Evidence Level
Every quantitative result carries its Level label (A, B, C) in the report. This is not optional.

### Rule 5: Never Use "Validated" Without Specification
Write "structure with lattice parameters within 2% of MP reference", not "validated structure".

### Rule 6: Never Use "Discovered" for Known Materials
Write "CathodeScope's analysis of LiCoO2 shows...", not "CathodeScope discovered that LiCoO2...".

### Rule 7: Never Use "Proved" for Computational Results
Write "benchmark results consistent with references within specified thresholds", not "proves the method works".

### Rule 8: Never Use "Accurate" Without a Reference
Write "lattice parameters within 1% of MP reference", not "accurate lattice parameters".

### Rule 9: Never Drop Caveats from Level B or C Results
Caveats are part of the result. Dropping them makes the result misleading.

### Rule 10: Never Present Proxy Results Alongside Benchmarked Results Without Labeling
Level A and Level C results must be in separate, clearly labeled sections.

---

## 9. Stop Conditions

These are mandatory pause points. Do NOT proceed past a stop condition until it is explicitly resolved.

### SC-01: MACE Installation Verification
| Field | Value |
|-------|-------|
| **When** | Before running T-20 (LiCoO2 integration test) |
| **What to check** | MACE-MP-0 installs on the dev machine; a single-point energy calculation on LiCoO2 completes without error |
| **Resolution if failed** | Debug PyTorch/MACE compatibility. Try CPU-only install. Check `mace-torch` version against `tech_stack.md`. |
| **May not proceed until** | MACE single-point energy returns a finite value for the LiCoO2 fixture structure |

### SC-02: LiCoO2 Lattice Accuracy
| Field | Value |
|-------|-------|
| **When** | After T-20 passes |
| **What to check** | LiCoO2 relaxed lattice parameters deviate < 2% from MP reference. Volume deviation < 5%. |
| **Resolution if failed** | Check normalization (primitive vs. conventional cell mismatch). Check MACE model version. Check relaxation parameters. |
| **May not proceed until** | Lattice deviations confirmed < 2% or documented explanation for deviation |

### SC-03: Evidence Label Audit
| Field | Value |
|-------|-------|
| **When** | After T-13 (evidence labeler) completes |
| **What to check** | All 8 MVP evidence labels match `scientific_validity_matrix.md` Section 3 Part A exactly |
| **Resolution if failed** | Update `cathodescope/validation/evidence.py` to match the matrix. Re-run evidence tests. |
| **May not proceed until** | Every label assignment matches the authoritative validity matrix |

### SC-04: Report Wording Audit
| Field | Value |
|-------|-------|
| **When** | After T-16 (Markdown renderer) completes |
| **What to check** | Generated Markdown report matches mock excerpt format in `scientific_validity_matrix.md` Section 5. All 10 wording rules enforced. |
| **Resolution if failed** | Update `cathodescope/reporting/markdown_report.py` templates. Add missing wording checks. |
| **May not proceed until** | Report format verified against the mock excerpt |

### SC-05: Benchmark Results Review
| Field | Value |
|-------|-------|
| **When** | After T-24 (benchmark integration test) completes |
| **What to check** | At least 2/3 Full Success. Third at least Partial Success. All 24 metrics populated. Results make physical sense. |
| **Resolution if failed** | Investigate failing material. For LiMn2O4 Jahn-Teller effects: document as expected Partial Success, do NOT lower thresholds. |
| **May not proceed until** | Benchmark passes 2/3 criterion or failures are scientifically documented |

### SC-06: Reproducibility Verification
| Field | Value |
|-------|-------|
| **When** | After T-24 — same timing as SC-05 |
| **What to check** | Re-running benchmark produces same result category per material. Lattice deviations agree within 0.1% between runs. |
| **Resolution if failed** | Set `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`. Investigate floating-point non-determinism. Pin thread counts. |
| **May not proceed until** | Two consecutive runs produce consistent result categories |

### SC-07: Phase 4 Coverage Gate
| Field | Value |
|-------|-------|
| **When** | After all waves completed (before declaring thesis-core complete) |
| **What to check** | `pytest --cov=cathodescope` shows > 80% coverage. Regression benchmark passes. External reviewer can reproduce. All wording rules enforced. |
| **Resolution if failed** | Write additional tests for uncovered branches. Fix CI failures. Update documentation. |
| **May not proceed to Phase 5 until** | All coverage and reproducibility criteria met |

---

## 10. Definition of Done (Per Task)

A task is Done when ALL of the following are true (from `tdd_task_breakdown.md` Section 1.5):

1. All tests listed in the task are written and passing
2. `ruff check` passes with no errors on all new/modified files
3. `mypy --strict` passes on all `cathodescope/models/` files; `mypy` passes on all other new files
4. All public functions have docstrings
5. All pydantic models have `model_config` with `json_schema_extra` examples where appropriate
6. No `# TODO` comments remain (capture as deferred tasks instead)
7. Import rules from `dependency_graph.md` Section 6 are respected

---

*These rules are mandatory for every task. They exist to prevent scope creep, ensure scientific rigor, and maintain architectural integrity. When in doubt, follow the rules. When the rules conflict, ask before proceeding.*
