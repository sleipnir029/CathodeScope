Below is the **corrected v2 master plan** for **CathodeScope**. It plans the **whole system from the start**, but keeps the **MVP narrow, defensible, and buildable**, while preserving extension hooks so later phases do not force a redesign. It directly revises the original MatPilot blueprint’s overreach on autonomy, stability, transport, and phase ordering.  

---

# CathodeScope v2 Master Plan

## 1. Project identity

**CathodeScope** is a reproducible scientific workflow platform for **benchmarked Li-ion cathode screening**, with **agent orchestration layered on top of deterministic validated workflows**.

### Core thesis claim

CathodeScope does **not** claim full autonomous materials discovery in the thesis-core version.
It claims:

> A reproducible, benchmarked workflow system that can analyze known cathode materials, run selected atomistic workflows, compare against trusted references, and produce disciplined evidence-labeled reports.

### Supporting claim

A later phase adds:

> Agent orchestration over the validated workflow backend.

This is a cleaner and more defensible version of the original plan, which put autonomy and advanced physics too early in the stack.  

---

## 2. End goal vs MVP

## End goal

A platform that can eventually:

* analyze known cathode materials,
* benchmark workflows across major cathode families,
* orchestrate tools with an LLM,
* support cautious exploration of unknown candidates,
* and provide extension points for stronger stability, voltage, and transport workflows.

## MVP

The MVP must do one thing very well:

> **relaxed structure + reference comparison + disciplined report**

This is the first scientifically trusted output you selected.

### MVP includes

* known-material inputs only,
* canonical material representation,
* Materials Project retrieval,
* structure normalization,
* MACE-based relaxation,
* reference comparison,
* artifact/provenance storage,
* benchmark runner for known materials,
* report generation,
* tests and caching.

### MVP excludes as required outputs

* unknown-material trust,
* rigorous transport claims,
* strong stability proof,
* agent-first workflow,
* full autonomous discovery language.

---

## 3. Scientific validity ladder

This must be hard-coded into the project language, report templates, and evaluation.

## Level A — trusted in MVP

These are acceptable thesis-core outputs.

**Retrieved**

* MP metadata
* benchmark labels
* literature/reference values

**Computed**

* normalized structure
* relaxed structure
* relaxation metadata
* deterministic workflow outputs

**Compared**

* structure vs reference
* family consistency
* convergence and sanity checks

Allowed wording:

* “retrieved from reference source”
* “computed by CathodeScope”
* “compared against reference”
* “consistent within the defined benchmark threshold”

## Level B — restricted estimates

Allowed later in a narrow scope.

* average voltage estimate for supported cases
* family-constrained ranking outputs
* limited heuristic classification

Allowed wording:

* “screening estimate”
* “restricted workflow estimate”
* “requires deeper validation”

## Level C — proxies

Planned from the beginning, not thesis-core trust outputs.

* stability proxy
* dynamical stability proxy
* transport proxy

Allowed wording:

* “proxy”
* “screening signal”
* “follow-up recommended”

## Level D — not allowed as thesis-core claims

* “discovered a new stable cathode”
* “validated migration barrier” from lightweight MD
* “proved thermodynamic stability” of hypothetical compounds using database comparison alone
* “proved dynamical stability” from lightweight checks alone

This is the biggest conceptual correction from the original plan.  

---

## 4. Whole-system architecture

The architecture must support the whole roadmap from day one, even though only part of it is implemented first.

```text
User Input / Query
    ↓
Input Resolver
    ↓
Canonical Material Model
    ↓
Workflow Engine  ← deterministic execution graph
    ↓
Scientific Tools
    ├─ MP Client
    ├─ Structure Tools
    ├─ Relaxation Tools
    ├─ Reference Comparison
    ├─ Report Builder
    └─ [future] Voltage / Stability / Dynamics / Candidate Gen
    ↓
Validation Layer
    ↓
Artifacts + Provenance Store
    ↓
Reporting Layer
    ↓
Benchmark Layer
    ↓
[future] Agent Orchestration Layer
```

## Architectural rule

The **agent never owns the scientific logic**.
It only selects and sequences workflows later.

That directly fixes the original plan’s tendency to center the agent too early.  

---

## 5. Core modules

## 5.1 Input Resolver

Accepts:

* formula
* material name
* MP id
* structure file
* later: natural-language query

Output:

* normalized query object

## 5.2 Canonical Material Model

Stores:

* formula
* reduced formula
* family
* structure source
* identifiers
* provenance
* benchmark tags
* workflow eligibility flags

This model is central because everything else depends on it.

## 5.3 Workflow Engine

A deterministic executor that runs predefined workflows such as:

* fetch and normalize structure
* relax structure
* compare against reference
* compile report

The MVP must work entirely through this layer.

## 5.4 Scientific Tools

MVP tools:

* `mp_client`
* `structure_builder`
* `structure_normalizer`
* `structure_relaxer`
* `reference_comparator`
* `report_generator`
* `physics_validator`

Future tools:

* `voltage_workflow`
* `stability_workflow`
* `dynamics_workflow`
* `candidate_generation_workflow`

## 5.5 Validation Layer

Applies:

* structural sanity checks
* family-specific constraints
* convergence checks
* evidence labeling
* error classification

## 5.6 Artifact / Provenance Layer

Stores:

* raw input
* canonical record
* structure files
* relaxed outputs
* config snapshot
* software versions
* tool parameters
* benchmark results
* report JSON and markdown

## 5.7 Reporting Layer

Produces:

* material analysis report
* benchmark summaries
* machine-readable result record

## 5.8 Benchmark Layer

Tracks:

* benchmark materials
* expected references
* run metrics
* regression history
* later: ablations and LLM comparisons

## 5.9 Agent Layer

Deferred until after the deterministic stack works.
Capabilities later:

* workflow selection
* tool routing
* result explanation
* optional hypothesis generation

---

## 6. Extension-first design rules

These are the rules that prevent future pain.

### Rule 1

Every tool returns a structured result object:

* status
* evidence type
* data
* warnings
* provenance
* artifacts

### Rule 2

No downstream module depends on free-form text output.

### Rule 3

Every workflow is a named graph with versioning.

### Rule 4

Future workflows plug in through interfaces, not by modifying core logic.

### Rule 5

Unknown-material exploration must be a separate workflow family, not mixed into the trusted benchmark core.

---

## 7. Phase roadmap

## Phase 0 — framing and constraints

Goal:

* lock scope, benchmark families, evidence vocabulary, artifact schema, and risk boundaries.

Deliverables:

* scientific validity matrix
* benchmark shortlist
* artifact schema
* architecture doc
* success criteria

Gate:

* no implementation before these are written.

## Phase 1 — MVP-0 deterministic single-material run

Goal:

* one clean workflow from input to report.

Workflow:

* resolve material
* fetch structure
* normalize
* relax
* compare with reference
* produce report

Deliverable:

* one trusted run for a known cathode.

Gate:

* reproducible rerun with same result class.

## Phase 2 — MVP-1 benchmark core

Goal:

* repeat the deterministic workflow across a small benchmark set.

Initial benchmark set:

* LiCoO2
* LiFePO4
* LiMn2O4
* one additional representative after stability of the pipeline is proven

Deliverables:

* benchmark runner
* benchmark result table
* structured failure logging

Gate:

* majority of benchmark runs complete deterministically with interpretable outputs.

## Phase 3 — MVP-2 reporting and portfolio layer

Goal:

* polished material report and benchmark viewer.

Deliverables:

* clean report schema
* local CLI or minimal app
* saved artifacts and reproducibility notes

Gate:

* a 3-minute demo exists.

## Phase 4 — thesis-core hardening

Goal:

* make the system thesis-worthy.

Add:

* stronger test coverage
* regression benchmark
* evidence labels everywhere
* better validation and failure typing
* reproducibility checklist
* documentation

Gate:

* enough to defend methodology and correctness.

## Phase 5 — agent orchestration

Goal:

* add LLM orchestration over the validated backend.

Add:

* tool schemas
* planning prompts
* trace logging
* benchmark vs scripted workflow

Gate:

* agent improves usability without weakening trust.

## Phase 6 — advanced scientific extensions

Planned from the beginning, implemented only after the core works.

Possible additions:

* restricted voltage workflow
* stability proxy workflow
* transport proxy workflow
* candidate generation workflow

Each extension must enter as a separate module with separate evaluation.

## Phase 7 — paper / portfolio polish

Goal:

* package results for jobs, thesis, and possibly publication.

Deliverables:

* case studies
* benchmark dashboard
* architecture figures
* portfolio writeup
* paper draft angle

---

## 8. Benchmark design

The benchmark should start narrow and representative.

## Families

* layered oxides
* olivines / polyanion
* spinels

## Why

This gives structural diversity without jumping into messy unknowns.

## Initial benchmark philosophy

Benchmark **known materials first**.
Do not use hypothetical materials to evaluate the core workflow.

## Benchmark outputs

For each benchmark material:

* input resolution success
* structure retrieval success
* relaxation success
* structural sanity result
* reference comparison result
* evidence-labeled report quality
* runtime/cost metadata

---

## 9. Success criteria

## Phase 1 success

* deterministic workflow runs end to end on one known material
* artifacts stored
* report generated
* no silent failures
* result is reproducible

## Phase 2 success

* benchmark runs on multiple known materials
* failures are categorized, not hidden
* reports stay disciplined

## Thesis-core success

* methodology is defensible
* outputs are evidence-labeled
* benchmark is reproducible
* architecture is extensible
* agent layer is optional, not a crutch

## Not required for thesis-core success

* unknown-material discovery
* full stability proof
* full transport validation
* flashy multi-agent behavior

---

## 10. Risk register

## Critical risks

**1. Scientific overclaiming**
Mitigation:

* hard validity matrix
* report wording constraints
* explicit proxy labels

**2. Scope creep**
Mitigation:

* phase gates
* no advanced extensions before benchmark core works

**3. Hardware/runtime mismatch**
Mitigation:

* small benchmark first
* overnight jobs only after the deterministic stack is stable
* strict profiling of expensive workflows

## High risks

**4. Agent complexity arriving too early**
Mitigation:

* no agent before workflow engine + benchmark

**5. Benchmark proves orchestration but not science**
Mitigation:

* structure and comparison quality are first-class metrics

**6. Dependency brittleness**
Mitigation:

* mock-first tests
* local fixtures
* cache and pinned environment

## Medium risks

**7. Extension hooks that are too vague**
Mitigation:

* define interface contracts now

**8. Report layer becoming vague or overly narrative**
Mitigation:

* machine-readable report schema first, markdown second

This risk framing is stricter and more realistic than the original plan’s version.  

---

## 11. Repository shape

Use a repo structure that reflects the architecture, not the original tool-heavy fantasy scope.

```text
cathodescope/
├── docs/
│   ├── subject_matter_expert_onboarding.md
│   ├── architecture.md
│   ├── master_plan.md
│   ├── scientific_validity_matrix.md
│   ├── benchmark_spec.md
│   └── artifact_schema.md
├── cathodescope/
│   ├── config/
│   ├── models/
│   ├── workflows/
│   ├── tools/
│   ├── validation/
│   ├── reporting/
│   ├── benchmark/
│   ├── provenance/
│   ├── agent/          # added later
│   └── app/            # added later
├── tests/
├── scripts/
└── artifacts/
```

Notice the difference:

* workflows and validation are central,
* agent is not the center,
* extensions have a place without distorting the core.

---

## 12. What gets built first

In strict order:

1. docs and scientific validity matrix
2. canonical material model
3. MP client and structure retrieval
4. structure normalization
5. relaxation workflow
6. reference comparison
7. artifact/provenance storage
8. report generation
9. benchmark runner
10. minimal interface/demo
11. agent orchestration
12. advanced extensions

That is the implementation order I recommend locking.

---

## 13. What gets explicitly deferred

These are designed now, not built now:

* unknown-material generation
* multi-agent planner/critic
* transport proxy
* dynamical stability proxy
* advanced voltage profiling
* large-scale candidate screening

They should exist in architecture documents as named future workflows so they slot in cleanly later.

---

## 14. Thesis title and subtitle

**Title:** CathodeScope
**Subtitle:** *A Reproducible Scientific Workflow Platform for Benchmarked Cathode Screening with Agent Orchestration*

That is strong, accurate, and career-useful.

---

## 15. Immediate next deliverables

The next documents we should create from this master plan are:

1. `docs/scientific_validity_matrix.md`
2. `docs/architecture.md`
3. `docs/subject_matter_expert_onboarding.md`
4. `docs/master_plan.md`
5. `docs/benchmark_spec.md`
6. `docs/artifact_schema.md`

Then we derive:

* tech stack,
* implementation order,
* dependency graph,
* risk heatmap,
* TDD task breakdown,
* Claude Code execution prompts.

If you want, next I’ll convert this master plan into the **six exact Claude Code planning prompts**, updated for **CathodeScope** instead of the older MatPilot framing.

**Confidence:** 0.97
