# CathodeScope — Task Sequence Summary

**Version**: 1.0.0
**Last Updated**: 2026-03-12 (Board review: 11/32 Done; sequence drift resolved; next-10 refreshed)
**Status**: Active — Project Management Document
**Cross-References**: `planning/tdd_task_breakdown.md` (task definitions), `task_board.md` (task statuses), `task_execution_rules.md` (selection algorithm)

---

## Overview

This document defines the exact execution order for all 32 tasks. The first 15 tasks are specified in precise order with rationale. The remaining 17 tasks are listed with brief descriptions and noted parallelization opportunities.

**Total estimate**: 58–84 hours across all tasks.

---

## First 15 Tasks — Exact Order

### Position 1: T-00 — Project Scaffolding and Build Configuration
**Rationale**: Everything depends on an installable package and a working test runner. Nothing else can start.
- **Wave**: 0
- **Size**: S (1–2 hours)
- **Dependencies**: None
- **Critical path**: Yes

### Position 2: T-01 — ProvenanceRecord Model
**Rationale**: `ProvenanceRecord` is embedded in every other data record. It must exist first so all other models can reference it.
- **Wave**: 1
- **Size**: S (1–2 hours)
- **Dependencies**: T-00
- **Critical path**: Yes

### Position 3: T-02 — ErrorRecord, ToolResult, StepResult, WorkflowResult Models
**Rationale**: `ToolResult` is the universal return type for all tools. `ErrorRecord` is used by every failure path. Must exist before any tool.
- **Wave**: 1
- **Size**: M (2–3 hours)
- **Dependencies**: T-01
- **Critical path**: Yes

### Position 4: T-05 — Configuration System
**Rationale**: Tools need configuration (fmax, tolerances, API keys) before they can be written. This unblocks the critical path faster than T-03/T-04.
- **Wave**: 1
- **Size**: M (2–3 hours)
- **Dependencies**: T-01
- **Critical path**: Yes

### Position 5: T-03 — CanonicalMaterial and NormalizedQuery Models
**Rationale**: Needed by the input resolver (T-08) and family classifier (T-08b). Not on the critical path but unblocks multiple downstream tasks.
- **Wave**: 1
- **Size**: M (2–3 hours)
- **Dependencies**: T-01
- **Critical path**: No (but enables T-08, T-08b, T-22)

### Position 6: T-04 — ReportRecord, BenchmarkRow, BenchmarkSummary Models
**Rationale**: Completes the model layer. Needed by reporting (T-15) and benchmark (T-22, T-23) subsystems.
- **Wave**: 1
- **Size**: S (2 hours)
- **Dependencies**: T-01
- **Critical path**: No (but enables T-15, T-23)

### Position 7: T-07 — MP Client and Fixture Capture
**Rationale**: The first external dependency. Produces fixture structures needed by the normalizer (T-09) and all downstream tools. On the critical path.
- **Wave**: 2
- **Size**: M (3–4 hours)
- **Dependencies**: T-02, T-05
- **Critical path**: Yes

### Position 8: T-06 — Artifact / Provenance Store
**Rationale**: Store must exist before integration testing. Can be built in parallel with T-07 once T-02 and T-05 are done. Building it here avoids blocking T-18/T-23 later.
- **Wave**: 2
- **Size**: M (3–4 hours)
- **Dependencies**: T-02, T-04, T-05
- **Critical path**: No (but required by T-18, T-23)

### Position 9: T-09 — Structure Normalizer
**Rationale**: Normalization must be verified for all 3 benchmark materials before relaxation. Uses fixtures from T-07. On the critical path.
- **Wave**: 2
- **Size**: M (2–3 hours)
- **Dependencies**: T-02, T-07
- **Critical path**: Yes

> **PAUSE/REVIEW GATE 1**: After T-09, conduct a **space group preservation review**. Verify that the normalizer preserves R-3m (LiCoO2), Pnma (LiFePO4), and Fd-3m (LiMn2O4) for the 3 benchmark materials. Reference: `scientific_validity_matrix.md` Row 2.
>
> **Gate 1 STATUS: PASSED** — 14/14 normalizer tests pass. R-3m (LiCoO2, 12 atoms) ✓, Pnma (LiFePO4, 28 atoms) ✓, Fd-3m (LiMn2O4, 56 atoms) ✓. Conventional cell fixtures committed. Safe to proceed.

### Position 10: T-13 — Evidence Label Assigner
**Rationale**: Evidence labels must be defined before the physics validator (T-14) can use them. Building this early ensures labels are correct before they propagate through the pipeline.
- **Wave**: 2
- **Size**: S (1–2 hours)
- **Dependencies**: T-02
- **Critical path**: No (but must be correct before integration)

> **PAUSE/REVIEW GATE 2**: After T-13, conduct an **evidence label audit** (SC-03). Verify all 8 MVP evidence labels match `scientific_validity_matrix.md` Section 3 Part A exactly: A-retrieved, A-computed (normalize), A-computed (relax), A-compared (compare), A-compared (validate). Verify summary inheritance: all-A → A, any-B → B, any-C → C.

### Position 11: T-12 — Validation Layer (Structural + Convergence Checks)
**Rationale**: The validation layer contains pure check functions needed by the physics validator (T-14). No tool dependencies — pure logic.
- **Wave**: 2
- **Size**: M (2–3 hours)
- **Dependencies**: T-02
- **Critical path**: No

### Position 12: T-08b — Family Classification Function
**Rationale**: Family classification feeds evidence label assignment (non-benchmarked families get Level B). Needed before the input resolver can fully populate `CanonicalMaterial`.
- **Wave**: 2
- **Size**: XS (1 hour)
- **Dependencies**: T-03
- **Critical path**: No

### Position 13: T-08 — Input Resolver
**Rationale**: The resolver is Step 0 of every workflow. Depends on T-03 (NormalizedQuery) and T-07 (MP client for formula lookup).
- **Wave**: 2
- **Size**: S (2 hours)
- **Dependencies**: T-03, T-07
- **Critical path**: No

### Position 14: T-10 — Structure Relaxer (Unit Tests with Mock Calculator)
**Rationale**: The relaxer is the primary computation step. Unit tests with mock calculator verify workflow logic independently of MACE. On the critical path.
- **Wave**: 2
- **Size**: M (3–4 hours)
- **Dependencies**: T-02, T-05, T-09
- **Critical path**: Yes

### Position 15: T-11 — Reference Comparator
**Rationale**: The comparator produces the scientific core — quantitative deviations between relaxed and reference structures. Uses normalized fixture structures from T-09.
- **Wave**: 2
- **Size**: M (3 hours)
- **Dependencies**: T-02, T-09
- **Critical path**: No

---

## Pause/Review Gates Summary

| Gate | After Task | Position | What to Verify | Stop Condition |
|------|------------|----------|----------------|----------------|
| 1 | T-09 | ~9 | Space group preservation for 3 benchmark materials | — |
| 2 | T-13 | ~10 | Evidence labels match validity matrix | SC-03 |
| 3 | T-20 | ~22 | MACE install + LiCoO2 accuracy < 2% | SC-01, SC-02 (Phase 1 gate) |
| 4 | T-24 | ~27 | Benchmark 2/3 Full Success, reproducibility | SC-05, SC-06 (Phase 2 gate) |

---

## Remaining Tasks (Positions 16–32)

### Wave 2 Completion (Positions 16–17)

| Position | Task | Title | Size | Dependencies |
|----------|------|-------|------|-------------|
| 16 | T-14 | Physics Validator Tool | S (2h) | T-12, T-13, T-05 |
| 17 | T-15 | JSON Report Builder | M (2–3h) | T-04, T-02 |

### Wave 3: Reporting and Workflow (Positions 18–24)

| Position | Task | Title | Size | Dependencies |
|----------|------|-------|------|-------------|
| 18 | T-16 | Markdown Report Renderer | M (2–3h) | T-15 |
| 19 | T-17 | Report Generator Tool | XS (1h) | T-15, T-16 |
| 20 | T-18 | Workflow Base Classes and Engine | M (3–4h) | T-02, T-05 |
| 21 | T-19 | structural_analysis Workflow Definition | S (2h) | T-18, T-07–T-17 |
| 22 | T-20 | Integration Test — LiCoO2 Pipeline | M (2–3h) | T-00–T-19 |
| 23 | T-21 | Integration Test — LiFePO4 and LiMn2O4 | S (1–2h) | T-20 |

> **PAUSE/REVIEW GATE 3**: After T-20, verify MACE-MP-0 installs and runs (SC-01). Verify LiCoO2 lattice deviations < 2% (SC-02). This is the Phase 1 gate.

### Wave 4: Benchmark (Positions 25–28)

| Position | Task | Title | Size | Dependencies |
|----------|------|-------|------|-------------|
| 24 | T-22 | Benchmark Registry | XS (1h) | T-03 |
| 25 | T-23 | Benchmark Runner | M (3–4h) | T-18, T-22, T-04, T-06 |
| 26 | T-24 | Benchmark Runner Integration Test | S (1–2h) | T-21, T-23 |
| 27 | T-24b | Benchmark Regression Comparison Tool | S (2h) | T-23, T-04 |

> **PAUSE/REVIEW GATE 4**: After T-24, verify 2/3 Full Success (SC-05). Verify reproducibility (SC-06). This is the Phase 2 gate.

### Wave 5–7: CLI, Hardening, Agent (Positions 29–32)

| Position | Task | Title | Size | Dependencies |
|----------|------|-------|------|-------------|
| 28 | T-25 | CLI Interface | S (2h) | T-19, T-23 |
| 29 | T-26 | Pre-commit and CI Configuration | S (1–2h) | T-00 |
| 30 | T-28 | Fixture Capture Script and Golden Outputs | S (1–2h) | T-20 |
| 31 | T-29 | Regression Tests | S (1–2h) | T-28 |
| 32 | T-27 | Import Rule Enforcement Tests | S (1–2h) | All previous |
| 33 | T-30 | Agent Scaffolding (Empty Stubs) | XS (15min) | T-18 |

---

## Parallelization Opportunities

Several tasks can be worked in parallel when their prerequisites are met:

### After T-01 (Position 2) completes:
- T-02, T-03, T-04, T-05 can all start (they only depend on T-01)

### After T-02 + T-05 (Positions 3–4) complete:
- T-07 and T-06 can start in parallel
- T-12 and T-13 can start in parallel (they depend only on T-02)

### After T-07 (Position 7) completes:
- T-09, T-08 can start in parallel (T-08 also needs T-03)

### After T-09 (Position 9) completes:
- T-10 and T-11 can start in parallel

### After T-15 (Position 17) completes:
- T-16 and T-18 can start in parallel

### Wave 4 parallelization:
- T-22 can start as early as after T-03
- T-24b can run in parallel with T-24

### Wave 5–7 parallelization:
- T-26 can start anytime after T-00 (infrastructure, no code dependencies)
- T-25, T-28, T-30 can run in parallel after their prerequisites

---

## Time Budget Summary

| Wave | Tasks | Est. Hours | Cumulative |
|------|-------|------------|------------|
| 0 | T-00 | 1–2 | 1–2 |
| 1 | T-01, T-02, T-03, T-04, T-05 | 9–14 | 10–16 |
| 2 | T-06, T-07, T-08, T-08b, T-09, T-10, T-11, T-12, T-13, T-14 | 22–30 | 32–46 |
| 3 | T-15, T-16, T-17, T-18, T-19, T-20, T-21 | 13–19 | 45–65 |
| 4 | T-22, T-23, T-24, T-24b | 7–9 | 52–74 |
| 5 | T-25 | 2 | 54–76 |
| 6 | T-26, T-27, T-28, T-29 | 4–8 | 58–84 |
| 7 | T-30 | 0.25 | 58–84 |
| **Total** | **32 tasks** | **58–84** | |

---

*Follow this sequence to minimize blocking and maximize throughput. The pause/review gates are mandatory — they catch scientific errors before they propagate through the pipeline.*

---

## Current Execution State (reviewed 2026-03-12)

**11/32 tasks Done. 177 tests passing. Gate 1 PASSED. Gate 2 PASSED (SC-03).**

### Completed Tasks
| Task | Title | Gate |
|------|-------|------|
| T-00 | Project Scaffolding | — |
| T-01 | ProvenanceRecord Model | — |
| T-02 | ErrorRecord, ToolResult, StepResult, WorkflowResult | — |
| T-03 | CanonicalMaterial and NormalizedQuery Models | — |
| T-04 | ReportRecord, BenchmarkRow, BenchmarkSummary | — |
| T-05 | Configuration System | — |
| T-07 | MP Client and Fixture Capture | — |
| T-09 | Structure Normalizer | Gate 1 PASSED |
| T-10 | Structure Relaxer (Mock Calculator) | — |
| T-13 | Evidence Label Assigner | Gate 2 PASSED (SC-03) |
| T-18 | Workflow Base Classes and Engine | — |

### Sequence Drift: RESOLVED

T-03 and T-04, which were skipped during Wave 1, are now Done. The following tasks are newly unblocked as a result:

| Previously Blocked Task | Was Blocked By | Status Now |
|------------------------|----------------|------------|
| T-08b (pos 12) | T-03 | **Unblocked** |
| T-08 (pos 13) | T-03 | **Unblocked** |
| T-22 (pos 24) | T-03 | **Unblocked** |
| T-06 (pos 8) | T-04 | **Unblocked** |
| T-15 (pos 17) | T-04 | **Unblocked** |

### Currently Unblocked Todo Tasks

| Task | Priority | Size | Why Unblocked |
|------|----------|------|---------------|
| T-08b | P1 | XS | T-03 Done |
| T-22 | P1 | XS | T-03 Done |
| T-08 | P1 | S | T-03, T-07 Done |
| T-06 | P1 | M | T-02, T-04, T-05 Done |
| T-11 | P1 | M | T-02, T-09 Done |
| T-12 | P1 | M | T-02 Done |
| T-15 | P1 | M | T-02, T-04 Done |

### Reprioritized Next 10 Tasks

| # | Task | Title | Size | Why Now | Deps Met? |
|---|------|-------|------|---------|-----------|
| 1 | T-08b | Family Classification Function | XS | Smallest unblocked; adds classify_family() to material.py; unblocks nothing new but completes T-03's sibling | Yes |
| 2 | T-12 | Validation Layer (Structural + Convergence) | M | Unblocks T-14; pure logic, no tool deps | Yes |
| 3 | T-08 | Input Resolver | S | Step 0 of every workflow; all deps done | Yes |
| 4 | T-06 | Artifact / Provenance Store | M | Required by T-23 (critical path benchmark runner) | Yes |
| 5 | T-11 | Reference Comparator | M | Core scientific output; all deps done | Yes |
| 6 | T-15 | JSON Report Builder | M | Unblocks T-16, T-17 | Yes |
| 7 | T-22 | Benchmark Registry | XS | XS task; newly unblocked by T-03 | Yes |
| 8 | T-14 | Physics Validator Tool | S | After T-12 Done | After T-12 |
| 9 | T-16 | Markdown Report Renderer | M | After T-15 Done | After T-15 |
| 10 | T-17 | Report Generator Tool | XS | After T-15, T-16 Done | After T-15+T-16 |

After positions 1–7 complete, T-19 (structural_analysis workflow) will have all dependencies met.

### Risks
- **T-19 prerequisite tail**: T-19 still needs T-08, T-08b, T-11, T-12, T-14, T-15, T-16, T-17. That is 8 tasks to clear before T-19 can start. Each is S or M sized. Prioritize these over T-22 and T-06 if throughput is the concern.
- **T-06 is blocking T-23** (Benchmark Runner, P0 critical path). Do not defer T-06 past position 6 in this list.
- **WorkflowContext type looseness**: `material: Any` and `normalized_query: Any` in `workflows/base.py` are intentional placeholders, to be tightened in T-19. Do not patch ahead of T-19.
- **T-26 scope**: `.pre-commit-config.yaml` already exists. T-26 is scoped to creating `.github/workflows/ci.yml` and verifying the pre-commit config runs cleanly. No risk of overwriting existing config.
