# CathodeScope — Project Roadmap

**Version**: 1.0.0
**Last Updated**: 2026-03-11
**Status**: Active — Project Management Document
**Cross-References**: `planning/master_plan.md` (phase definitions), `planning/implementation_order.md` (build order), `planning/tdd_task_breakdown.md` (task details), `planning/benchmark_spec.md` (benchmark criteria)

---

## Overview

This roadmap defines the phased delivery plan for CathodeScope, from documentation through thesis-core hardening and beyond. Each phase has explicit goals, deliverables, entry/exit criteria, and a label indicating its role in the project lifecycle.

**Labels**:
- **MVP** — Phases 1–3: Minimum viable product delivering deterministic single-material pipeline, benchmark suite, and reporting/CLI
- **Thesis-Core** — Phase 4: Hardening, testing, and documentation sufficient for thesis defense
- **Later Extension** — Phase 5: Agent orchestration layer (not required for thesis-core)
- **Post-Core** — Phases 6–7: Advanced scientific extensions and paper/portfolio polish

---

## Phase Summary

| Phase | Name | Label | Status | Est. Effort |
|-------|------|-------|--------|-------------|
| 0 | Framing and Constraints | Foundation | **Complete** | 1–2 weeks |
| 1 | MVP-0: Deterministic Single-Material Run | MVP | Todo | 3–5 weeks |
| 2 | MVP-1: Benchmark Core | MVP | Todo | 2–3 weeks |
| 3 | MVP-2: Reporting and Portfolio Layer | MVP | Todo | 2–3 weeks |
| 4 | Thesis-Core Hardening | Thesis-Core | Todo | 3–4 weeks |
| 5 | Agent Orchestration | Later Extension | Todo | 3–5 weeks |
| 6 | Advanced Scientific Extensions | Post-Core | Todo | 2–4 weeks per extension |
| 7 | Paper / Portfolio Polish | Post-Core | Todo | 2–3 weeks |

---

## Data Flow Diagram

```
User Input (formula / mp-id)
    │
    v
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Input      │────>│  MP Client   │────>│  Structure   │
│   Resolver   │     │  (Retrieve)  │     │  Normalizer  │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                                 v
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Report     │<────│  Physics     │<────│  Structure   │
│   Generator  │     │  Validator   │     │  Relaxer     │
└──────┬──────┘     └──────────────┘     │  (MACE)      │
       │                    ^             └──────┬───────┘
       │                    │                    │
       │            ┌──────────────┐             │
       │            │  Reference   │<────────────┘
       │            │  Comparator  │
       │            └──────────────┘
       v
┌─────────────┐     ┌──────────────┐
│  Artifact    │     │  Benchmark   │
│  Store       │     │  Runner      │
└─────────────┘     └──────────────┘
```

---

## Critical Path

```
T-00 → T-01 → T-02 → T-05 → T-07 → T-09 → T-10 → T-18 → T-19 → T-20 → T-23 → T-24
```

Any delay on the critical path delays the MVP. Tasks off the critical path can be parallelized where prerequisites allow.

---

## Phase Details

### Phase 0 — Framing and Constraints [COMPLETE]

**Goal**: Lock scope, benchmark families, evidence vocabulary, artifact schema, and risk boundaries. No code.

**Deliverables** (all complete):
- `scientific_validity_matrix.md` — Evidence levels, per-property wording rules, and anti-claims
- `architecture.md` — System architecture, module boundaries, data flow, and extension points
- `subject_matter_expert_onboarding.md` — Domain context for collaborators and reviewers
- `master_plan.md` — Phased roadmap, gates, risks, and success criteria
- `benchmark_spec.md` — Benchmark materials, reference data sources, comparison metrics, and pass/fail criteria
- `artifact_schema.md` — Schema definitions for all stored artifacts and provenance records

**Entry criteria**: None (starting point)

**Exit criteria**:
- [x] All 6 docs written and internally consistent
- [x] Cross-references verified
- [x] MVP boundary explicitly documented with acceptance test
- [x] No implementation has begun
- [x] Scientific validity matrix covers all MVP outputs
- [x] Benchmark materials selected with reference data sources identified

---

### Phase 1 — MVP-0: Deterministic Single-Material Run [MVP]

**Goal**: One clean workflow from input to report for a single known material (LiCoO2).

**Deliverables**:
- Input resolver, canonical material model, MP client
- Structure normalizer, structure relaxer (MACE), reference comparator
- Physics validator, report generator
- Artifact/provenance store
- One successful end-to-end run for LiCoO2

**Epics**: E-01, E-02, E-03, E-04, E-05, E-06, E-07 (partial), E-08 (partial)

**Entry criteria**: Phase 0 complete (all 6 docs written and gate passed)

**Exit criteria**:
- [ ] LiCoO2 processes end-to-end without manual intervention
- [ ] Artifacts stored correctly per `artifact_schema.md`
- [ ] Report generated with all evidence labels
- [ ] No silent failures (all errors caught and classified)
- [ ] Rerun produces same result category
- [ ] All models match `artifact_schema.md` definitions
- [ ] Unit tests pass for each module
- [ ] Lattice parameter deviation from MP reference < 2%
- [ ] Offline pipeline completion with cached fixtures
- [ ] Post-run integrity check passes
- [ ] Evidence labels in report match `scientific_validity_matrix.md` rules
- [ ] JSON and Markdown reports are consistent
- [ ] MACE-MP-0 checkpoint loads and completes single-point energy calculation

---

### Phase 2 — MVP-1: Benchmark Core [MVP]

**Goal**: Repeat the deterministic workflow across the small benchmark set (3 materials, 3 structural archetypes).

**Deliverables**:
- Benchmark runner, benchmark result table
- Structured failure logging
- Results for LiCoO2, LiFePO4, LiMn2O4

**Epics**: E-09

**Entry criteria**: Phase 1 complete (single-material pipeline working)

**Exit criteria**:
- [ ] At least 2 of 3 materials achieve Full Success
- [ ] Third material achieves at least Partial Success
- [ ] All failures classified per `benchmark_spec.md` categories
- [ ] Benchmark results are reproducible on rerun
- [ ] Regression comparison possible (benchmark comparator operational)
- [ ] Benchmark result table is machine-readable

---

### Phase 3 — MVP-2: Reporting and Portfolio Layer [MVP]

**Goal**: Polished material reports and benchmark viewer. Minimal CLI interface for running analyses.

**Deliverables**:
- Clean report schema (finalized)
- Local CLI for running analyses
- Saved artifacts and reproducibility notes
- Benchmark summary dashboard

**Epics**: E-10 (partial — CLI)

**Entry criteria**: Phase 2 complete (benchmark running on 3 materials)

**Exit criteria**:
- [ ] A 3-minute demo exists (input formula → see report)
- [ ] Reports render correctly in standard Markdown viewers with evidence level labels
- [ ] CLI documented with usage examples
- [ ] All artifacts from demo run are complete and valid
- [ ] Benchmark summary is viewable without running the pipeline

---

### Phase 4 — Thesis-Core Hardening [Thesis-Core]

**Goal**: Make the system thesis-worthy through testing, documentation, and evidence rigor.

**Deliverables**:
- Stronger test coverage (>80% for core modules)
- Regression benchmark (automated comparison against previous runs)
- Evidence labels verified everywhere
- Better validation and failure typing
- Reproducibility checklist document
- Code documentation

**Epics**: E-10 (partial — hardening tasks)

**Entry criteria**: Phase 3 complete (reporting and CLI working)

**Exit criteria**:
- [ ] Test coverage > 80% for core modules
- [ ] Regression benchmark runs automatically
- [ ] External reviewer can reproduce benchmark by following documentation
- [ ] All `scientific_validity_matrix.md` wording rules enforced in reports
- [ ] Methodology section for thesis is writable from documentation
- [ ] No known silent failure modes
- [ ] All artifact schemas validated against stored artifacts

---

### Phase 5 — Agent Orchestration [Later Extension]

**Goal**: Add LLM orchestration over the benchmarked backend. The agent selects and executes workflows — it does not replace them.

**Deliverables**:
- Tool schemas (JSON Schema format)
- Planning prompts
- Trace logging
- Comparison: agent-routed vs scripted workflow

**Entry criteria**: Phase 4 complete (hardened, tested deterministic stack)

**Exit criteria**:
- [ ] Agent can select and execute structural_analysis workflow for a known material
- [ ] Agent-routed results match scripted results for all benchmark materials
- [ ] Agent trace log captures all decisions with timestamps
- [ ] Agent wording stays within validity matrix constraints
- [ ] Agent improves usability without weakening trust
- [ ] Agent failure modes are classified and handled gracefully

---

### Phase 6 — Advanced Scientific Extensions [Post-Core]

**Goal**: Add restricted scientific capabilities beyond structural analysis MVP.

**Possible deliverables** (each a separate module with separate evaluation):
- Restricted voltage workflow (Level B estimate)
- Stability proxy workflow (Level C proxy)
- Transport proxy workflow (Level C proxy)
- Dynamical stability proxy (Level C proxy)
- Candidate generation workflow (Level C/D labeling)

**Entry criteria**: Phase 4 or 5 complete (hardened core required; agent layer optional)

**Exit criteria** (per extension):
- [ ] `scientific_validity_matrix.md` updated with new rows BEFORE workflow implementation
- [ ] Extension passes its own benchmark with defined reference data
- [ ] Evidence labels consistent with validity matrix
- [ ] Extension does not break existing workflows (regression test passes)
- [ ] Extension documentation includes explicit limitations and caveats

---

### Phase 7 — Paper / Portfolio Polish [Post-Core]

**Goal**: Package results for thesis, job applications, and possible publication.

**Deliverables**:
- Case studies (3+ materials analyzed in depth)
- Benchmark dashboard
- Architecture figures (publication-quality)
- Portfolio writeup
- Paper draft angle

**Entry criteria**: Phase 4 minimum, ideally Phase 5–6 for richer content

**Exit criteria**:
- [ ] Thesis methodology chapter writable from documentation
- [ ] Demo materials are compelling and well-presented
- [ ] Figures are publication-quality
- [ ] Paper angle identified and outline drafted
- [ ] Portfolio is reviewable by someone outside the project

---

## Phase Gate Process

### Gate Rules

1. **Binary**: A gate is passed or it is not. There is no partial pass.
2. **Mandatory**: All gate criteria for the current phase must be met before any work on the next phase begins.
3. **Documented**: When a gate is passed, record: phase, date, reviewer, all criteria met (yes/no), notes, deviations.

### Gate Purpose

Gates prevent:
- Building on an unstable foundation
- Scope creep through premature feature additions
- Scientific overclaiming through insufficient validation

### Who Reviews

| Phase | Reviewer |
|-------|----------|
| 0–3 | Self-review against checklist |
| 4 (thesis-core) | Advisor review strongly recommended |
| 5–7 | Self-review, advisor consultation for scientific claims |

### Gate Is Not Perfection

Gates check **minimum viability** for the next phase:
- Phase 1 gate requires schema-conformant reports, not beautiful ones
- Phase 2 gate requires 2/3 Full Success, not 3/3
- Phase 3 gate requires a working CLI demo, not a polished web UI

---

## Cross-Reference Index

| Document | Location | Relevance |
|----------|----------|-----------|
| Master Plan | `planning/master_plan.md` | Phase definitions, gate criteria, risk register |
| Architecture | `planning/architecture.md` | Module boundaries, data flow, extension points |
| Scientific Validity Matrix | `planning/scientific_validity_matrix.md` | Evidence levels, wording rules |
| Benchmark Spec | `planning/benchmark_spec.md` | Materials, metrics, pass/fail criteria |
| Artifact Schema | `planning/artifact_schema.md` | Storage schemas, directory layout |
| Implementation Order | `planning/implementation_order.md` | Build sequence rationale |
| TDD Task Breakdown | `planning/tdd_task_breakdown.md` | Task definitions, test planning |
| Dependency Graph | `planning/dependency_graph.md` | Import rules, module dependencies |
| Risk Heatmap | `planning/risk_heatmap.md` | Risk assessment, mitigations |
| Tech Stack | `planning/tech_stack.md` | Technology choices |
| Demo Strategy | `planning/demo_strategy.md` | Demo planning |
| Epic Board | `epic_board.md` | Epic definitions and groupings |
| Task Board | `task_board.md` | All 32 tasks with full details |
| Task Execution Rules | `task_execution_rules.md` | How to select and execute tasks |
| Task Template | `task_template.md` | Standard task card template |
| Task Sequence Summary | `task_sequence_summary.md` | Ordered execution sequence |

---

*This roadmap is the high-level project plan for CathodeScope. For task-level details, see `task_board.md`. For execution rules, see `task_execution_rules.md`.*
