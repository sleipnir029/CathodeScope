# CathodeScope Demo Strategy

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active — Implementation Planning Document
**Cross-References**: `master_plan.md` (acceptance test, phase gates, success criteria), `benchmark_spec.md` (benchmark materials and metrics), `scientific_validity_matrix.md` (evidence labels, wording rules), `architecture.md` (system design)

---

## 1. Demo Philosophy

Demos are structured demonstrations of CathodeScope's capabilities, not sales pitches. Every demo must show:

1. **What the system does** — concrete, observable outputs.
2. **Why the outputs are trustworthy** — evidence labels, reference comparisons, reproducibility.
3. **What the system does NOT claim** — explicit boundaries, honest limitations.

The demo sequence mirrors the build order: each demo becomes possible only when the corresponding implementation phase is complete.

---

## 2. Demo Sequence

### Demo 1: LiCoO2 End-to-End (Phase 1 Gate)

**When**: Immediately after Phase 1 gate is passed.

**What to show**:
```
Input:   "LiCoO2"
Output:  Evidence-labeled Markdown report with:
         - Retrieved MP reference data [Level A -- retrieved]
         - MACE-relaxed structure [Level A -- computed]
         - Lattice parameter deviations [Level A -- compared]
         - Symmetry preservation check
         - Full provenance metadata
```

**Duration**: 3-5 minutes live execution + 5 minutes walkthrough.

**What this demonstrates**:
- The pipeline works end-to-end from formula input to final report.
- No manual intervention at any step.
- Evidence labels are present and correctly assigned per `scientific_validity_matrix.md`.
- Artifacts are stored per `artifact_schema.md` directory layout.
- Lattice parameter deviations are within 2% of MP reference (`benchmark_spec.md` Section 4).
- Rerun produces the same result category (reproducibility).

**What this does NOT demonstrate**:
- That the pipeline works for all materials (only LiCoO2 tested).
- That MACE is accurate (it shows MACE is consistent with MP for this material).
- Anything about voltage, stability, transport, or dynamics.

**Key talking points**:
- "This is a computational comparison, not an experimental validation."
- "Deviation means difference between two computational methods (MACE and PBE+U), not error."
- "Evidence level A means: produced by a validated workflow with full provenance."

---

### Demo 2: Benchmark Suite — 3 Materials (Phase 2 Gate)

**When**: Immediately after Phase 2 gate is passed.

**What to show**:
```
Input:   Benchmark command (3 materials: LiCoO2, LiFePO4, LiMn2O4)
Output:  Benchmark summary table:
         - Per-material: status, lattice deviations, symmetry, convergence
         - Aggregate: 2/3 Full Success, 1/3 Partial Success (expected)
         - Failure classification for any non-full-success results
```

**Duration**: Benchmark runtime (minutes) + 10 minutes walkthrough.

**What this demonstrates**:
- The pipeline generalizes across structural archetypes (layered, olivine, spinel).
- Results are quantitatively evaluated against defined thresholds.
- Failure classification works (Partial Success on LiMn2O4 is a scientific result, not a bug).
- The benchmark is reproducible (same result categories on rerun).

**What this does NOT demonstrate**:
- That MACE is universally accurate (3 materials is not a comprehensive survey).
- Anything beyond structural analysis.

**Key talking points**:
- "LiMn2O4 Partial Success is expected — Jahn-Teller effects challenge the model."
- "A Partial Success is itself a scientific finding: it characterizes the model's boundary."
- "Every number in this table traces back to a metric in `benchmark_spec.md`."

---

### Demo 3: CLI Interaction (Phase 3 Gate)

**When**: After Phase 3 gate is passed.

**What to show**:
```
$ cathodescope analyze LiCoO2
[Processing...] Resolving formula... Fetching structure... Normalizing...
[Processing...] Relaxing with MACE-MP-0... (23 steps, fmax = 0.005 eV/A)
[Processing...] Comparing against reference... Validating... Generating report...
[Done] Report saved to artifacts/reports/{id}/report.md

$ cathodescope benchmark
[Benchmark] Running structural_analysis on 3 materials...
[1/3] LiCoO2: Full Success (a: 0.5%, c: 0.2%)
[2/3] LiFePO4: Full Success (a: 0.8%, b: 0.4%, c: 0.6%)
[3/3] LiMn2O4: Partial Success (a: 2.3%)
[Done] Summary: 2 Full, 1 Partial, 0 Failures
```

**Duration**: 3-minute demo (this is the Phase 3 gate criterion: `master_plan.md` Phase 3).

**What this demonstrates**:
- Clean user interface for non-programmatic usage.
- Progress feedback during execution.
- Summary output is immediately informative.
- Reports and artifacts are accessible after the run.

---

### Demo 4: Report Quality Deep-Dive (Phase 3/4)

**When**: After Phase 3, refined during Phase 4.

**What to show**:
- Open a generated `report.md` and walk through every section.
- Show evidence level labels in section headers: `[Level A -- retrieved]`, `[Level A -- computed]`, `[Level A -- compared]`.
- Show the assessment paragraph and its evidence level inheritance.
- Show the provenance section: software versions, MACE model, configuration.
- Open the corresponding `report.json` and show the machine-readable structure.
- Demonstrate that the Markdown report is derived from the JSON report.

**What this demonstrates**:
- Reports are publication-quality.
- Evidence labels are not decorative — they are systematic and enforced.
- The machine-readable JSON is the primary artifact; Markdown is a view.
- Full provenance enables external reproduction.

**Key talking points**:
- "Every section header tells you how much to trust the data in that section."
- "The word 'deviation' is used instead of 'error' because the MP reference is itself a computation."
- "The JSON report can be programmatically consumed for further analysis."

---

### Demo 5: Agent Orchestration (Phase 5)

**When**: After Phase 5 gate is passed. **DO NOT DEMO BEFORE PHASE 5.**

**What to show**:
- Agent receives a natural-language query: "Analyze LiCoO2 and compare its structure to the Materials Project reference."
- Agent selects the `structural_analysis` workflow.
- Agent executes the workflow through the same engine as the CLI.
- Agent produces a natural-language summary that respects evidence level constraints.
- Show the agent trace log: every decision, tool call, and parameter.
- Show that agent-routed results match scripted results for the same material.

**What this demonstrates**:
- Agent orchestration adds usability without weakening scientific trust.
- Agent cannot bypass validation or provenance.
- Agent decisions are fully auditable.
- Agent wording respects the validity matrix.

---

## 3. Audience-Specific Presentation Strategies

### 3.1 Academic Supervisors / Thesis Examiners

**What they care about**: Scientific rigor, reproducibility, methodological soundness, awareness of limitations.

**What to emphasize**:
- The validity matrix and evidence labeling system. Show them that every output is classified and constrained.
- The anti-claims (`master_plan.md` Section 2). Show them what CathodeScope explicitly will NOT claim.
- Reproducibility: run the benchmark twice, show identical result categories.
- The distinction between "deviation from reference" and "error" (Rule 2 in `scientific_validity_matrix.md` Section 4).
- The benchmark philosophy: "If CathodeScope cannot reproduce known results, nothing else it produces can be trusted" (`benchmark_spec.md` Section 1).

**What to avoid**:
- Overselling the agent capabilities.
- Using words like "validated," "proved," or "accurate" without qualification.
- Presenting MACE accuracy as a CathodeScope achievement (MACE accuracy is an external model property).

**Demo to lead with**: Demo 2 (Benchmark Suite) — shows scientific rigor and honest results.

**Key phrase**: "CathodeScope is a reproducible workflow platform with evidence-labeled outputs, not a discovery engine."

---

### 3.2 Battery / Materials Researchers

**What they care about**: Benchmark results, MACE accuracy for cathode materials, comparison methodology, whether this is useful for their work.

**What to emphasize**:
- The three benchmark families and why they were chosen (structural diversity, `benchmark_spec.md` Section 2).
- Quantitative deviation values: show the actual lattice parameter deviations for each material.
- How LiMn2O4's Jahn-Teller effects challenge the model and what that tells us about MACE.
- The comparison methodology: MACE-relaxed vs. MP-PBE+U, not MACE vs. experiment.
- The structured benchmark output: machine-readable, reusable.

**What to avoid**:
- Claiming MACE is more accurate than DFT (it's trained on DFT, so it inherits DFT errors).
- Implying CathodeScope replaces experimental characterization.
- Overstating the significance of passing a 3-material benchmark.

**Demo to lead with**: Demo 2 (Benchmark Suite) — shows concrete numbers they can evaluate.

**Key phrase**: "The benchmark tests the workflow pipeline against known materials — not the MACE model itself."

---

### 3.3 German Industry Recruiters / Software Engineering Roles

**What they care about**: Software architecture quality, testing discipline, code organization, engineering maturity, ability to handle complex technical projects.

**What to emphasize**:
- Architecture: layered design, dependency graph, extension-first rules, plugin registries (`architecture.md`).
- Testing: pytest suite, mock-first development, integration tests, >80% coverage target.
- Data contracts: pydantic models, structured I/O between modules, no free-form text dependencies.
- Error handling: typed error taxonomy, classified failures, partial result preservation.
- Configuration management: defaults in code, overrides from JSON, secrets in environment variables.
- CI/CD: automated testing, linting (ruff), type checking (mypy), pre-commit hooks.
- Provenance system: immutable artifacts, reproducibility verification, version tracking.

**What to avoid**:
- Deep scientific details they cannot evaluate.
- Spending too long on battery chemistry instead of software design.
- Apologizing for the domain — frame it as a complex, real-world system integration problem.

**Demo to lead with**: Demo 3 (CLI) followed by architecture walkthrough — shows clean engineering.

**Key phrase**: "CathodeScope demonstrates disciplined software engineering applied to a real scientific domain: reproducible workflows, structured data contracts, and evidence-tracked outputs."

---

### 3.4 Scientific Software / Research Software Engineering Roles

**What they care about**: Workflow design patterns, extensibility, provenance tracking, reproducibility, how scientific constraints influenced engineering decisions.

**What to emphasize**:
- Workflow engine design: named, versioned workflows with step sequencing and context passing (`architecture.md` Section 4.3).
- Extension-first rules: plugin registries, `ToolResult` contract, separate workflow families (`architecture.md` Section 7).
- Provenance as a first-class concern: every artifact carries a `ProvenanceRecord` with software versions, config snapshots, and parent artifact linkage (`artifact_schema.md` Section 2.5).
- The validity matrix as a design constraint: scientific conservatism driving engineering decisions (`scientific_validity_matrix.md`).
- How the benchmark spec constrains the benchmark runner: machine-readable success criteria, not subjective assessment (`benchmark_spec.md`).
- The data artifact dependency DAG: how `parent_ids` enable full lineage tracking.
- Immutability: write-once artifacts, append-only benchmark history.

**What to avoid**:
- Glossing over the scientific motivation — these audiences appreciate the domain constraint.
- Presenting the architecture as generic (it's opinionated, and that's the point).

**Demo to lead with**: Demo 4 (Report Quality) — shows provenance, evidence labels, and the JSON-to-Markdown derivation.

**Key phrase**: "Scientific validity constraints drive the architecture: evidence labeling, immutable provenance, and benchmarked workflows are not afterthoughts — they are the design."

---

## 4. Demo Readiness Checklist

Before each demo, verify:

### Demo 1 (LiCoO2 end-to-end)
- [ ] LiCoO2 processes without errors
- [ ] Report generated with all evidence labels
- [ ] Artifacts stored in correct directory structure
- [ ] Lattice parameter deviations < 2%
- [ ] Rerun produces same result category

### Demo 2 (Benchmark suite)
- [ ] All 3 materials process (success or classified failure)
- [ ] At least 2/3 Full Success
- [ ] Benchmark summary table generated
- [ ] Failure categories correctly assigned

### Demo 3 (CLI)
- [ ] CLI commands work: `analyze`, `benchmark`
- [ ] Progress output is informative
- [ ] Help text is documented
- [ ] Demo completable in 3 minutes

### Demo 4 (Report quality)
- [ ] Report Markdown renders correctly
- [ ] Evidence labels present in all section headers
- [ ] Provenance section includes MACE version, pymatgen version, timestamps
- [ ] JSON report and Markdown report are consistent

### Demo 5 (Agent)
- [ ] Phase 4 gate passed
- [ ] Agent-routed results match scripted results
- [ ] Agent trace log captures all decisions
- [ ] Agent wording respects validity matrix

---

## 5. What NOT to Demo

| Excluded Demo | Reason |
|---------------|--------|
| Voltage estimation | Phase 6 — not MVP. No workflow exists yet. |
| Stability assessment | Phase 6 — only Level C proxy at best. |
| Unknown-material screening | Phase 6+ — trust framework for unknowns not built. |
| Web UI | Phase 7 — not part of thesis-core. |
| Multi-agent planning | Phase 5+ — needs proven single-agent first. |
| Cross-model comparison | Phase 7 — paper-polish activity, not core demo. |

**Rule**: If a feature is in the "Do Not Build Yet" list (`implementation_order.md` Section 6), it is also in the "Do Not Demo" list.

---

## Cross-Reference Index

| Topic | Related Document | Section |
|-------|-----------------|---------|
| LiCoO2 acceptance test | `master_plan.md` | Section 3 |
| Phase gate criteria (demo readiness) | `master_plan.md` | Section 5 (per phase) |
| 3-minute demo requirement | `master_plan.md` | Phase 3 gate |
| Benchmark materials and metrics | `benchmark_spec.md` | Sections 3-4 |
| Evidence label format in reports | `scientific_validity_matrix.md` | Section 5 |
| Wording rules (presentation language) | `scientific_validity_matrix.md` | Section 4 |
| Anti-claims (what NOT to say) | `master_plan.md` | Section 2 |
| Architecture for engineering audiences | `architecture.md` | Full document |
| Phase 5 agent comparison requirement | `master_plan.md` | Phase 5 gate |

---

*Every demo must demonstrate both capability and discipline. Show what the system does, and show that it knows what it cannot claim.*
