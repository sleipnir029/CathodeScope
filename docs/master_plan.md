# CathodeScope — Master Plan

**A Reproducible Scientific Workflow Platform for Benchmarked Cathode Screening with Agent Orchestration**

> This is the strategic "what and when" document — the phased roadmap from zero to thesis-core and beyond. It defines scope, phases, gates, risks, and success criteria. All other project documents are subordinate to or cross-referenced from this plan.

---

## Table of Contents

1. [Project Identity](#1-project-identity)
2. [Thesis Claims](#2-thesis-claims)
3. [MVP Definition](#3-mvp-definition)
4. [Out of Scope (with Rationale)](#4-out-of-scope-with-rationale)
5. [Phase Roadmap](#5-phase-roadmap)
6. [Phase Gates: Definition and Process](#6-phase-gates-definition-and-process)
7. [Benchmark Philosophy](#7-benchmark-philosophy)
8. [Success Criteria](#8-success-criteria)
9. [Risk Register](#9-risk-register)
10. [Deferrals and Decision Log](#10-deferrals-and-decision-log)
11. [Implementation Order Rationale](#11-implementation-order-rationale)

---

## 1. Project Identity

**CathodeScope** is a reproducible scientific workflow platform for benchmarked Li-ion cathode screening, with agent orchestration layered on top of deterministic, benchmarked workflows.

The key phrase is *reproducible scientific workflow platform*. CathodeScope is not a discovery engine, not a materials database, and not an autonomous research agent. It is a disciplined pipeline that takes known cathode materials, processes them through benchmarked computational workflows, compares results against known references, and produces evidence-labeled reports. Agent orchestration is a usability layer added later — it does not replace or weaken the deterministic scientific core.

### The Identity Test

Any proposed feature, claim, or design decision must pass the following question:

> **"Does this fit within a reproducible scientific workflow platform for benchmarked cathode screening?"**

- If **yes**, the feature belongs. Proceed to phase and priority assessment.
- If **no**, the feature is either **out of scope** or must be **explicitly justified** against the identity with a recorded rationale in the Decision Log (Section 10).

This test is the single most important filter against scope creep and overclaiming. Apply it early and often.

---

## 2. Thesis Claims

### Primary Claim (Thesis-Core)

> A reproducible, benchmarked workflow system that can analyze known cathode materials, run selected atomistic workflows, compare against known references, and produce disciplined evidence-labeled reports.

This claim is defensible through Phases 1-4. It does not require agent orchestration, unknown-material handling, or advanced scientific extensions. It requires:

- A working deterministic pipeline
- A benchmark set with reproducible results
- Evidence-labeled outputs that follow the scientific validity matrix
- Documentation sufficient for external reproduction

### Supporting Claim (Later Phase)

> Agent orchestration over the benchmarked workflow backend improves usability without weakening evidence discipline.

This claim is pursued in Phase 5. It is explicitly secondary to the primary claim. The thesis can succeed without it. It requires:

- A proven deterministic stack (Phase 4 gate passed)
- Agent-routed results that match scripted results
- Agent decision traces that are auditable
- Agent wording that respects validity matrix constraints

### Anti-Claims (Level D — Never Allowed)

The following claims are **permanently prohibited** in any CathodeScope output, report, or documentation. They represent scientific overclaiming that the platform's methodology cannot support:

- **"CathodeScope discovered a new stable cathode material."**
  Reason: CathodeScope validates known materials against references. Discovery requires experimental confirmation and theoretical rigor beyond this platform's scope.

- **"CathodeScope validated migration barriers using lightweight molecular dynamics."**
  Reason: Lightweight MD proxies cannot validate migration barriers. Nudged Elastic Band (NEB) with DFT or equivalent rigor is required.

- **"CathodeScope proved thermodynamic stability of hypothetical compounds using database comparison alone."**
  Reason: Database energy-above-hull values are proxies, not proofs. True thermodynamic stability requires accurate phase diagram construction with consistent energy referencing.

- **"CathodeScope proved dynamical stability from gamma-point phonon checks alone."**
  Reason: Gamma-point phonon calculations sample only a single point in the Brillouin zone. Full phonon dispersion across the entire Brillouin zone is required for dynamical stability claims.

> **Cross-reference:** `scientific_validity_matrix.md` for the full evidence framework, including all four evidence levels (A through D) and per-property wording constraints.

---

## 3. MVP Definition

### The MVP Sentence

> The MVP takes a known cathode material formula, retrieves its structure from Materials Project, normalizes it, relaxes it using MACE, compares the relaxed structure against the MP reference, and produces an evidence-labeled report.

This is the irreducible core of CathodeScope. Every word in this sentence maps to a concrete module. If a module is not needed to fulfill this sentence, it is not MVP.

### MVP Includes

| Component | Purpose | Module |
|-----------|---------|--------|
| Known-material inputs only | Formula string or Materials Project ID | Input resolver |
| Canonical material representation | Standard internal model for all downstream modules | Material model |
| Materials Project retrieval | Fetch structure, metadata, and reference properties | MP client |
| Structure normalization | Reduce to conventional cell, standardize settings | Normalizer |
| MACE-based relaxation | Relax atomic positions and cell parameters | Relaxer |
| Reference comparison | Compare relaxed structure against MP reference | Comparator |
| Physics validation | Check results against physical plausibility bounds | Validator |
| Artifact/provenance storage | Store all inputs, outputs, parameters, and metadata | Artifact store |
| Benchmark runner for 3 known materials | LiCoO2, LiFePO4, LiMn2O4 | Benchmark runner |
| Evidence-labeled report generation | Human-readable output with explicit evidence levels | Report generator |
| Tests and caching | Unit tests for each module; cached MP responses for offline development | Test suite |

### MVP Excludes (as Required Outputs)

| Excluded Feature | Reason |
|------------------|--------|
| Unknown-material trust or generation | Requires benchmarked known-material pipeline first |
| Rigorous transport claims | Migration barriers require NEB/MD, not MVP scope |
| Strong stability proof | Thermodynamic stability requires phase diagram rigor |
| Agent-first workflow | Deterministic stack must work independently before agent layer |
| Full autonomous discovery language | Violates identity test and anti-claims |
| Voltage estimation | Requires delithiated structure workflow, not MVP scope |
| Web UI or API server | Core value is the scientific pipeline, not the interface |

### Acceptance Test

**Material:** LiCoO2 (R-3m layered oxide)

**Procedure:**
1. Input the formula `LiCoO2` to the pipeline.
2. Pipeline resolves to MP ID, retrieves structure, normalizes, relaxes with MACE, compares against MP reference, generates report.
3. No manual intervention at any step.

**Pass criteria:**
- Lattice parameter comparison present in report with deviation values
- All deviations within defined thresholds (< 2% for lattice parameters)
- All evidence labels in the report are Level A (reference-compared against known Materials Project references)
- Artifacts stored per `artifact_schema.md`
- Rerun on the same machine with the same environment produces the same result category
- No silent failures (all errors are caught, classified, and reported)

---

## 4. Out of Scope (with Rationale)

| Feature | Reason Deferred | Phase Planned | Architecture Hook |
|---------|----------------|---------------|-------------------|
| Unknown-material generation | Trust framework for unknowns requires benchmarked known-material pipeline first | Phase 6 | Separate workflow family per Extension Rule 5 |
| Rigorous transport properties | Migration barrier calculations require NEB or MD, computationally expensive and scientifically complex | Phase 6 | `transport_proxy` tool interface defined |
| Strong stability proof | Thermodynamic stability requires accurate phase diagram data and energy referencing beyond MP comparison | Phase 6 | `stability_workflow` tool interface defined |
| Agent orchestration | Agent must orchestrate benchmarked tools, not replace them; deterministic stack must work first | Phase 5 | Agent layer defined in architecture, tool schemas ready |
| Dynamical stability | Full phonon dispersion is computationally expensive; gamma-point is only a proxy | Phase 6 | `dynamics_workflow` tool interface defined |
| Multi-agent planner/critic | Advanced orchestration requires proven single-agent workflow selection first | Phase 5+ | Agent layer extensible |
| Large-scale candidate screening | Requires trust in unknown-material workflows, which are not thesis-core | Phase 6+ | Candidate generation workflow interface defined |
| Web UI / API server | Core value is in the scientific pipeline, not the interface; CLI/minimal app sufficient for thesis | Phase 3 (minimal), Phase 7 (polish) | App module defined in repo structure |

Every deferred feature has an **architecture hook** — a defined interface or extension point in the system design. This means deferral does not create technical debt; it creates planned extension points. See `architecture.md` for interface definitions.

---

## 5. Phase Roadmap

### Phase 0 — Framing and Constraints

**Goal:** Lock scope, benchmark families, evidence vocabulary, artifact schema, and risk boundaries. No code.

**Deliverables:**
- `scientific_validity_matrix.md` — Evidence levels, per-property wording rules, and anti-claims
- `architecture.md` — System architecture, module boundaries, data flow, and extension points
- `subject_matter_expert_onboarding.md` — Domain context for collaborators and reviewers
- `master_plan.md` — This document: phased roadmap, gates, risks, and success criteria
- `benchmark_spec.md` — Benchmark materials, reference data sources, comparison metrics, and pass/fail criteria
- `artifact_schema.md` — Schema definitions for all stored artifacts and provenance records

**Dependencies:** None (starting point)

**Estimated effort:** Medium (1-2 weeks)

**Key risks:**
- Over-planning without starting implementation
- Scope not narrow enough (identity test not applied rigorously)
- Documents become inconsistent with each other

**Gate criteria:**
- [ ] All 6 docs written and internally consistent
- [ ] Cross-references verified (every cross-reference points to an existing section)
- [ ] MVP boundary explicitly documented with acceptance test
- [ ] No implementation has begun
- [ ] Scientific validity matrix covers all MVP outputs
- [ ] Benchmark materials selected with reference data sources identified

---

### Phase 1 — MVP-0: Deterministic Single-Material Run

**Goal:** One clean workflow from input to report for a single known material (LiCoO2).

**Deliverables:**
- **Input resolver** — Accepts formula string or MP ID, resolves to canonical identifier
- **Canonical material model** — Pydantic (or equivalent) model representing a material throughout the pipeline
- **MP client** — Materials Project API client with caching, rate limiting, and error handling
- **Structure normalizer** — Reduces to conventional cell, standardizes lattice settings
- **Structure relaxer** — MACE-based ionic relaxation with configurable parameters
- **Reference comparator** — Compares relaxed structure against MP reference (lattice parameters, volume, symmetry, bond lengths)
- **Physics validator** — Checks results against physical plausibility bounds (e.g., positive volume, reasonable bond lengths)
- **Report generator** — Produces evidence-labeled Markdown report
- **Artifact/provenance store** — Stores all inputs, outputs, parameters, and metadata per `artifact_schema.md`
- **One successful run for LiCoO2** — The acceptance test defined in Section 3

**Dependencies:** Phase 0 complete (all 6 docs written and gate passed)

**Estimated effort:** Large (3-5 weeks)

**Key risks:**
- MACE installation/compatibility issues on target hardware
- Materials Project API changes or rate limiting
- Relaxation does not converge for test material
- Canonical material model does not capture all needed properties

**Gate criteria:**
- [ ] LiCoO2 processes end-to-end without manual intervention
- [ ] Artifacts stored correctly per `artifact_schema.md`
- [ ] Report generated with all evidence labels
- [ ] No silent failures (all errors caught and classified)
- [ ] Rerun produces same result category
- [ ] All models match `artifact_schema.md` definitions
- [ ] Unit tests pass for each module
- [ ] Lattice parameter deviation from MP reference < 2%
- [ ] Offline pipeline completion with cached fixtures (no live network dependency for gate pass)
- [ ] Post-run integrity check per `artifact_schema.md` Section 7 passes (all required artifacts present on disk)

---

### Phase 2 — MVP-1: Benchmark Core

**Goal:** Repeat the deterministic workflow across the small benchmark set (3 materials, 3 structural archetypes).

**Deliverables:**
- **Benchmark runner** — Orchestrates pipeline runs across multiple materials with structured result collection
- **Benchmark result table** — Structured output comparing all materials against references
- **Structured failure logging** — Categorized failure types per `benchmark_spec.md`
- **Results for LiCoO2, LiFePO4, LiMn2O4** — Full pipeline runs with reports and artifacts

**Dependencies:** Phase 1 complete (single-material pipeline working)

**Estimated effort:** Medium (2-3 weeks)

**Key risks:**
- Materials with different structural complexity may require relaxation parameter tuning
- Spinel LiMn2O4 Jahn-Teller effects may challenge MACE accuracy
- Olivine LiFePO4 has different symmetry constraints than layered oxides
- Benchmark runner introduces orchestration complexity

**Gate criteria:**
- [ ] At least 2 of 3 materials achieve Full Success
- [ ] Third material achieves at least Partial Success
- [ ] All failures classified per `benchmark_spec.md` categories
- [ ] Benchmark results are reproducible (rerun produces same result categories)
- [ ] Regression comparison possible (a script or CLI command compares two `BenchmarkSummary` JSON files and reports status changes and metric deltas)
- [ ] Benchmark result table is machine-readable

---

### Phase 3 — MVP-2: Reporting and Portfolio Layer

**Goal:** Polished material reports and benchmark viewer. Minimal CLI interface for running analyses.

**Deliverables:**
- **Clean report schema** (finalized) — Machine-readable report format with all required fields
- **Local CLI or minimal app** for running analyses — Command-line interface for single-material and benchmark runs
- **Saved artifacts and reproducibility notes** — Complete provenance for all runs
- **Benchmark summary dashboard** — Markdown or simple HTML summary of benchmark results

**Dependencies:** Phase 2 complete (benchmark running on 3 materials)

**Estimated effort:** Medium (2-3 weeks)

**Key risks:**
- Report format becomes too verbose or too sparse
- CLI ergonomics hinder usability
- Dashboard scope creeps into full web application

**Gate criteria:**
- [ ] A 3-minute demo exists (input formula -> see report)
- [ ] Reports render correctly in standard Markdown viewers, all section headers include evidence level labels, all quantitative values include units, and report structure matches `scientific_validity_matrix.md` Section 5 template
- [ ] CLI documented with usage examples
- [ ] All artifacts from demo run are complete and valid
- [ ] Benchmark summary is viewable without running the pipeline

---

### Phase 4 — Thesis-Core Hardening

**Goal:** Make the system thesis-worthy through testing, documentation, and evidence rigor. This is the phase where "it works" becomes "it is defensible."

**Deliverables:**
- **Stronger test coverage** — Unit, integration, and regression tests for all core modules
- **Regression benchmark** — Automated comparison against previous runs with deviation detection
- **Evidence labels verified everywhere** — Audit of all report outputs against validity matrix
- **Better validation and failure typing** — Exhaustive error classification and handling
- **Reproducibility checklist document** — Step-by-step instructions for external reproduction
- **Code documentation** — Docstrings, module-level documentation, and architecture decision records

**Dependencies:** Phase 3 complete (reporting and CLI working)

**Estimated effort:** Large (3-4 weeks)

**Key risks:**
- Thesis timeline pressure creates temptation to skip hardening and jump to flashy features
- Test coverage targets are difficult to reach for I/O-heavy modules
- Reproducibility across different environments is harder than expected

**Gate criteria:**
- [ ] Test coverage > 80% for core modules
- [ ] Regression benchmark runs automatically
- [ ] External reviewer can reproduce benchmark by following documentation
- [ ] All `scientific_validity_matrix.md` wording rules enforced in reports
- [ ] Methodology section for thesis is writable from documentation
- [ ] No known silent failure modes
- [ ] All artifact schemas validated against stored artifacts

---

### Phase 5 — Agent Orchestration

**Goal:** Add LLM orchestration over the benchmarked backend. The agent selects and executes workflows — it does not replace them.

**Deliverables:**
- **Tool schemas** — JSON Schema format definitions for each tool the agent can invoke
- **Planning prompts** — Prompt templates that constrain the agent to valid workflow selections
- **Trace logging** — Full audit trail of agent decisions, tool calls, parameters, and results
- **Comparison: agent-routed vs scripted workflow** — Quantitative comparison showing same results through both paths

**Dependencies:** Phase 4 complete (hardened, tested deterministic stack)

**Estimated effort:** Large (3-5 weeks)

**Key risks:**
- Agent complexity exceeds the value it provides
- Agent makes incorrect tool selections leading to invalid workflow sequences
- Agent output wording violates validity matrix constraints
- Latency and cost of LLM calls degrade usability
- Agent becomes a crutch that masks pipeline issues

**Gate criteria:**
- [ ] Agent can select and execute the structural_analysis workflow for a known material
- [ ] Agent-routed results match scripted results for all benchmark materials
- [ ] Agent trace log captures all decisions with timestamps
- [ ] Agent wording stays within validity matrix constraints
- [ ] Agent improves usability without weakening trust (qualitative assessment documented)
- [ ] Agent failure modes are classified and handled gracefully

---

### Phase 6 — Advanced Scientific Extensions

**Goal:** Add restricted scientific capabilities beyond the structural analysis MVP. Each extension is a separate module with its own evaluation, evidence level, and benchmark.

**Possible deliverables** (each entered as a separate module with separate evaluation):
- **Restricted voltage workflow** — Energy difference between lithiated and delithiated structures, labeled as Level B estimate
- **Stability proxy workflow** — Energy above hull from MP data, labeled as Level C proxy
- **Transport proxy workflow** — Lightweight migration barrier estimate, labeled as Level C proxy with strong caveats
- **Dynamical stability proxy** — Gamma-point phonon check, labeled as Level C proxy (not full stability claim)
- **Candidate generation workflow** — Cautious generation with strong caveats and Level C/D labeling

**Dependencies:** Phase 4 or 5 complete (hardened core required; agent layer optional)

**Estimated effort:** Large (per extension, 2-4 weeks each)

**Key risks:**
- Overclaiming from proxy results (the most dangerous risk in this phase)
- Complexity explosion as each extension adds new failure modes
- Each extension doubles the test surface
- Extension interactions are not well-understood

**Gate criteria (per extension):**
- [ ] `scientific_validity_matrix.md` updated with new rows BEFORE workflow implementation begins
- [ ] Extension passes its own benchmark with defined reference data
- [ ] Evidence labels consistent with validity matrix (Level B or C as appropriate, never Level A for proxies)
- [ ] Extension does not break existing workflows (regression test passes)
- [ ] Extension documentation includes explicit limitations and caveats
- [ ] Anti-claims updated if new overclaiming risks are identified

---

### Phase 7 — Paper / Portfolio Polish

**Goal:** Package results for thesis, job applications, and possible publication. This is a presentation phase, not a feature phase.

**Deliverables:**
- **Case studies** — 3+ materials analyzed in depth with full reports and discussion
- **Benchmark dashboard** — Interactive or well-formatted static summary of all benchmark results
- **Architecture figures** — Publication-quality diagrams of system design and data flow
- **Portfolio writeup** — Concise project summary for external audiences
- **Paper draft angle** — Identified publication venue and drafted outline

**Dependencies:** Phase 4 minimum, ideally Phase 5-6 for richer content

**Estimated effort:** Medium (2-3 weeks)

**Key risks:**
- Scope creep into new features instead of polishing existing ones
- Perfectionism delays completion
- Paper angle is unclear or too broad

**Gate criteria:**
- [ ] Thesis methodology chapter writable from documentation
- [ ] Demo materials are compelling and well-presented
- [ ] Figures are publication-quality (vector format, clear labels, consistent style)
- [ ] Paper angle identified and outline drafted
- [ ] Portfolio is reviewable by someone outside the project

---

## 6. Phase Gates: Definition and Process

### What a Gate Is

A gate is a **mandatory review point** before proceeding to the next phase. All gate criteria for the current phase must be checked off before any work on the next phase begins.

Gates exist to prevent:
- Building on an unstable foundation
- Scope creep through premature feature additions
- Scientific overclaiming through insufficient validation

### Who Reviews

- **Phases 0-3:** The thesis author conducts a self-review against the checklist. Document the review date and any notes.
- **Phase 4 (thesis-core):** Advisor review is **strongly recommended** in addition to self-review. This is the gate that determines thesis defensibility.
- **Phases 5-7:** Self-review, with advisor consultation for any scientific claims introduced.

### Gate Failure

If gate criteria are not met, the phase is **not complete**. Do not proceed to the next phase. Instead:

1. Identify which criteria are unmet.
2. Determine the effort required to meet them.
3. Complete the remaining work.
4. Re-review.

There is no "partial pass." A gate is binary: all criteria met, or the gate has not been passed.

### Gate Documentation

When a gate is passed, record:

| Field | Value |
|-------|-------|
| Phase | Phase N |
| Gate passed date | YYYY-MM-DD |
| Reviewer | Name |
| All criteria met? | Yes |
| Notes | Any observations, deviations, or future concerns |
| Deviations from criteria | If any criterion was modified, document the rationale |

### Gate Is Not Perfection

The gate checks **minimum viability** for the next phase, not perfection. Perfection is a Phase 4 and Phase 7 concern. For example:

- Phase 1 gate does not require beautiful reports — it requires *schema-conformant, evidence-labeled* reports.
- Phase 2 gate does not require 3/3 Full Success — it requires 2/3 Full Success and 1/3 Partial Success minimum.
- Phase 3 gate does not require a polished web UI — it requires a working CLI demo.

---

## 7. Benchmark Philosophy

### Known Materials First

The benchmark set consists **exclusively** of materials for which community-consensus reference data exists. This is a deliberate constraint. The benchmark tests whether CathodeScope's pipeline produces results consistent with known references — not the materials themselves.

A material qualifies for the benchmark set if and only if:
- Computational reference data exists from multiple independent studies
- Experimental structural data exists (lattice parameters, space group)
- The material is present in Materials Project with a stable entry
- The structural archetype is relevant to Li-ion cathode research

### Why 3 Families

| Family | Archetype | Diffusion | Representative | Space Group |
|--------|-----------|-----------|----------------|-------------|
| Layered oxide | 2D layers | 2D in-plane | LiCoO2 | R-3m |
| Olivine | 1D channels | 1D along b-axis | LiFePO4 | Pnma |
| Spinel | 3D network | 3D tetrahedral-octahedral | LiMn2O4 | Fd-3m |

These three families cover the three major structural archetypes of commercial Li-ion cathodes. This provides **structural diversity without overreaching**:

- **2D diffusion** (layered) tests the pipeline on materials with van der Waals-like interlayer interactions.
- **1D diffusion** (olivine) tests the pipeline on materials with strong directional bonding.
- **3D diffusion** (spinel) tests the pipeline on materials with complex symmetry and potential Jahn-Teller distortions.

### Why These Specific Materials

- **LiCoO2:** The most-studied layered oxide cathode. Extensive computational and experimental reference data. Simple composition (no mixing on transition metal site). The "hydrogen atom" of cathode research.
- **LiFePO4:** The most-studied olivine cathode. Well-characterized structural properties. Different symmetry and bonding from layered oxides. Commercial relevance.
- **LiMn2O4:** The most-studied spinel cathode. Challenging due to Jahn-Teller effects in Mn3+. Tests the pipeline's ability to handle structural complexity. 3D diffusion network.

### Benchmark Is Not Aspirational

Every material in the benchmark **must already have reliable reference data**. The benchmark does not aspire to characterize new materials or push computational boundaries. It answers one question:

> "Does CathodeScope's pipeline produce results consistent with known references for well-studied materials?"

If the answer is yes, the pipeline produces results consistent with known references within defined thresholds. If the answer is no, the pipeline needs fixing — not the benchmark.

> **Cross-reference:** `benchmark_spec.md` for the full specification including reference data sources, comparison metrics, tolerance thresholds, and pass/fail criteria.

---

## 8. Success Criteria

### Phase 1 Success

| Criterion | Measurable Target |
|-----------|-------------------|
| Deterministic workflow runs end-to-end | LiCoO2 completes without manual intervention |
| Structural accuracy | Lattice parameter deviation from MP reference < 2% |
| Artifact storage | All artifacts stored per `artifact_schema.md` |
| Report generation | Evidence-labeled report produced |
| Failure handling | No silent failures; all errors caught and classified |
| Reproducibility | Rerun produces same result category |

### Phase 2 Success

| Criterion | Measurable Target |
|-----------|-------------------|
| Benchmark coverage | 3 known materials processed |
| Success rate | At least 2/3 Full Success |
| Minimum quality | Third material at least Partial Success |
| Failure classification | All failures categorized per `benchmark_spec.md` |
| Report discipline | All reports evidence-labeled |
| Reproducibility | Benchmark results reproducible on rerun |

### Phase 3 Success

| Criterion | Measurable Target |
|-----------|-------------------|
| Demo speed | 3-minute demo from formula input to viewable report |
| Interface | CLI works with documented usage |
| Report quality | Reports render correctly in standard Markdown viewers, all section headers include evidence level labels, all quantitative values include units, and report structure matches `scientific_validity_matrix.md` Section 5 template |
| Artifact completeness | All demo run artifacts complete and valid |

### Phase 4 Success (Thesis-Core)

| Criterion | Measurable Target |
|-----------|-------------------|
| Methodology | Defensible in thesis examination |
| Evidence discipline | All outputs evidence-labeled per validity matrix |
| Reproducibility | Benchmark reproducible by external reviewer following documentation |
| Architecture | Extensible for agent layer and advanced workflows |
| Independence | Agent layer optional, not required for core function |
| Test coverage | > 80% for core modules |
| External reproduction | Reviewer can reproduce within documented environment |

### Phase 5 Success

| Criterion | Measurable Target |
|-----------|-------------------|
| Usability improvement | Agent reduces steps for common workflows |
| Evidence consistency | Agent results match scripted results |
| Auditability | Agent decisions fully traceable |
| Wording compliance | Agent outputs respect validity matrix constraints |

### Not Required for Thesis-Core Success

The following are explicitly **not** success criteria for the thesis:

- Unknown-material discovery
- Full thermodynamic stability proof
- Full transport property validation
- Flashy multi-agent behavior
- Web UI or interactive dashboard
- Large-scale candidate screening
- Publication in a top-tier journal (desirable but not required)

---

## 9. Risk Register

| # | Risk | Likelihood | Impact | Severity | Mitigation | Owner |
|---|------|-----------|--------|----------|------------|-------|
| 1 | Scientific overclaiming | Medium | Critical | **Critical** | Hard validity matrix; report wording constraints; explicit proxy labels; anti-claims enforced at generation time | Author |
| 2 | Scope creep | High | High | **Critical** | Phase gates; identity test for all features; no advanced extensions before benchmark core works; decision log | Author |
| 3 | Hardware/runtime mismatch | Medium | Medium | **High** | Small benchmark first; overnight jobs only after deterministic stack is stable; strict profiling; resource budgets | Author |
| 4 | Agent complexity arriving too early | Medium | High | **High** | No agent before workflow engine + benchmark (Phase 5 gate); deterministic stack must pass Phase 4 gate first | Author |
| 5 | Benchmark tests orchestration but not science | Medium | High | **High** | Structure and comparison quality are first-class metrics, not just "did it run"; quantitative deviation thresholds | Author |
| 6 | Dependency brittleness (MP API changes, MACE updates) | Medium | Medium | **High** | Mock-first tests; local fixtures; cached MP responses; pinned environment; version-locked dependencies | Author |
| 7 | Extension hooks too vague | Low | Medium | **Medium** | Define interface contracts in `architecture.md` during Phase 0; review interfaces at each gate | Author |
| 8 | Report layer becomes vague or narrative | Medium | Medium | **Medium** | Machine-readable report schema first, Markdown rendering second; schema validation on every report | Author |
| 9 | Thesis timeline pressure | High | High | **Critical** | Phase gates enforce minimum viable quality; resist feature additions under pressure; Phase 4 is the hard deadline for thesis-core | Author |

### Severity Matrix

|  | Low Impact | Medium Impact | High Impact | Critical Impact |
|---|-----------|---------------|-------------|-----------------|
| **High Likelihood** | Medium | High | Critical | Critical |
| **Medium Likelihood** | Low | Medium | High | Critical |
| **Low Likelihood** | Low | Low | Medium | High |

### Risk Response Protocol

- **Critical severity:** Address immediately. Block progress on the affected phase until mitigated.
- **High severity:** Address within the current phase. Document mitigation steps taken.
- **Medium severity:** Monitor. Address if impact increases.
- **Low severity:** Accept. Review at phase gates.

> **Cross-reference:** `scientific_validity_matrix.md` for overclaiming risk mitigation (Risk #1). The validity matrix is the primary defense against the most dangerous risk in the project.

---

## 10. Deferrals and Decision Log

### Current Deferrals

| Feature | Reason Deferred | Phase Planned | Architecture Hook |
|---------|----------------|---------------|-------------------|
| Unknown-material generation | Requires benchmarked pipeline first; trust framework for unknowns is a separate research problem | Phase 6 | Separate workflow family |
| Multi-agent planner/critic | Needs proven single-agent first; multi-agent adds coordination complexity | Phase 5+ | Agent layer extensible |
| Transport proxy | Computationally complex, scientifically nuanced; migration barriers require NEB or equivalent | Phase 6 | Tool interface defined |
| Dynamical stability proxy | Gamma-point is only a proxy; full phonon dispersion is computationally expensive | Phase 6 | Tool interface defined |
| Advanced voltage profiling | Requires delithiated structure workflow and accurate energy referencing | Phase 6 | Tool interface defined |
| Large-scale candidate screening | Trust framework for unknowns needed; screening without trust is dangerous | Phase 6+ | Workflow family defined |
| Web UI | Core value is pipeline, not interface; CLI sufficient for thesis | Phase 3 (minimal), Phase 7 (polish) | App module in repo structure |
| Experimental data integration | Requires curated experimental datasets with consistent formatting | Phase 4+ | Comparison tool extensible |

### Decision Log

Record all scope decisions here. Every deferral, inclusion, or modification to the plan should be documented.

| Date | Decision | Rationale | Impact on Phases | Recorded By |
|------|----------|-----------|-----------------|-------------|
| *(example)* | Defer NMC-111 to Phase 2+ | Need pipeline stability on simpler materials first; NMC introduces site mixing complexity | Phase 2 benchmark may expand if NMC-111 is added | Author |
| | | | | |

### Deferral Rules

1. **A deferral is not a rejection.** Deferred features have planned phases and architecture hooks.
2. **Every deferral must have an architecture hook.** If you cannot define the extension point, the deferral may indicate a design gap.
3. **Deferrals are reviewed at each phase gate.** A deferred feature may be promoted if its phase arrives, or further deferred if priorities change.
4. **Re-introducing a deferred feature requires passing the identity test** (Section 1) and updating this document.

---

## 11. Implementation Order Rationale

**Note**: This section provides a conceptual ordering. The authoritative, granular implementation sequence is defined in `implementation_order.md`.

The implementation order follows the data flow of the system. Each step depends on the previous ones being complete. This is not an arbitrary ordering — it is dictated by information dependencies.

```
Input --> Process --> Validate --> Store --> Report --> Benchmark --> Orchestrate --> Extend
```

### Ordered Steps

| Order | Component | Rationale |
|-------|-----------|-----------|
| 1 | **Docs and scientific validity matrix** | Phase 0 gate requires docs before code. You cannot build what you have not specified. The validity matrix constrains every subsequent decision. |
| 2 | **Canonical material model** | Every subsequent module depends on having a standard material representation. Without this, modules cannot communicate. |
| 3 | **MP client and structure retrieval** | You need a structure to work with. Materials Project is the source. The client must exist before any processing can begin. |
| 4 | **Structure normalization** | The retrieved structure must be in canonical form before relaxation. Different MP entries may have different cell conventions. |
| 5 | **Relaxation workflow** | This is the primary computation. It requires steps 2-4 to exist (a canonical, normalized structure to relax). |
| 6 | **Reference comparison** | You need both a relaxed structure (step 5) and a reference (step 3) to compare. This is where scientific value is generated. |
| 7 | **Artifact/provenance storage** | Now that you have outputs to store, build the storage layer. Storing artifacts retroactively is error-prone. |
| 8 | **Report generation** | With stored, reference-compared results, generate the human-readable output. Reports consume artifacts; they do not produce them. |
| 9 | **Benchmark runner** | With a working pipeline, run it across the benchmark set. The runner is an orchestrator of the existing pipeline, not new science. |
| 10 | **Minimal interface/demo** | Wrap the pipeline in a usable CLI. The interface is a thin layer over the existing components. |
| 11 | **Agent orchestration** | Layer the agent on top of the tested, benchmarked stack. The agent calls the same tools the CLI calls. |
| 12 | **Advanced extensions** | Build additional scientific workflows using the established patterns. Each extension follows the same build-validate-benchmark cycle. |

### Why This Order Matters

- **Steps 1-8** correspond to Phase 0-1 (single material, end-to-end).
- **Step 9** corresponds to Phase 2 (benchmark core).
- **Step 10** corresponds to Phase 3 (reporting and portfolio).
- **Steps 11-12** correspond to Phases 5-6 (agent and extensions).

Skipping or reordering steps creates hidden dependencies and untested assumptions. For example:

- Building the agent (step 11) before the comparison module (step 6) means the agent has no benchmarked science to orchestrate.
- Building reports (step 8) before artifact storage (step 7) means reports cannot reference stored provenance.
- Building the benchmark runner (step 9) before the single-material pipeline (steps 2-8) means you are benchmarking an incomplete system.

---

## Cross-Reference Index

This document references and is referenced by the following project documents:

| Document | Relationship |
|----------|-------------|
| `scientific_validity_matrix.md` | Defines evidence levels and wording constraints referenced throughout this plan |
| `architecture.md` | Defines module boundaries, interfaces, and extension points for all phases |
| `benchmark_spec.md` | Defines benchmark materials, metrics, and pass/fail criteria for Phases 2-4 |
| `artifact_schema.md` | Defines storage schemas referenced in MVP definition and gate criteria |
| `subject_matter_expert_onboarding.md` | Provides domain context for understanding phase goals and scientific constraints |

---

## Document History

| Date | Change | Author |
|------|--------|--------|
| 2026-03-10 | Initial version — full master plan from Phase 0 through Phase 7 | Author |

---

*This document is the strategic backbone of CathodeScope. All implementation decisions, scope changes, and phase transitions should be evaluated against this plan. When in doubt, apply the identity test.*
