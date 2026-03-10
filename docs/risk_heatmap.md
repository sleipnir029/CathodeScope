# CathodeScope Risk Heatmap

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active — Implementation Planning Document
**Cross-References**: `master_plan.md` (Section 9, risk register), `scientific_validity_matrix.md` (wording rules), `benchmark_spec.md` (reproducibility criteria), `artifact_schema.md` (completeness checklist)

---

## 1. Severity Matrix

Likelihood x Impact grid for quick severity classification. Identical to `master_plan.md` Section 9.

```
                    Low Impact    Medium Impact    High Impact    Critical Impact
                   +-----------+--------------+-------------+----------------+
High Likelihood    |  Medium   |    High      |  Critical   |   Critical     |
                   +-----------+--------------+-------------+----------------+
Medium Likelihood  |   Low     |   Medium     |    High     |   Critical     |
                   +-----------+--------------+-------------+----------------+
Low Likelihood     |   Low     |    Low       |   Medium    |     High       |
                   +-----------+--------------+-------------+----------------+
```

**Response protocol** (from `master_plan.md` Section 9):
- **Critical**: Address immediately. Block progress until mitigated.
- **High**: Address within current phase. Document mitigation steps.
- **Medium**: Monitor. Address if impact increases.
- **Low**: Accept. Review at phase gates.

---

## 2. Visual Heatmap

```
RISK                                   LIKELIHOOD   IMPACT      SEVERITY
-----------------------------------------------------------------------
1. Scientific overclaiming             ██████░░░░   ██████████  CRITICAL
2. Scope creep                         ██████████   ██████████  CRITICAL
3. Thesis timeline pressure            ██████████   ██████████  CRITICAL
4. Hardware/runtime mismatch           ██████░░░░   ██████░░░░  HIGH
5. Agent complexity too early          ██████░░░░   ██████████  HIGH
6. Benchmark = orchestration not sci.  ██████░░░░   ██████████  HIGH
7. Dependency brittleness              ██████░░░░   ██████░░░░  HIGH
8. Reproducibility failure             ██████░░░░   ██████████  HIGH
9. Provenance gaps                     ██████░░░░   ██████░░░░  HIGH
10. Bad report wording                 ██████░░░░   ██████░░░░  MEDIUM
11. Extension-interface instability    ████░░░░░░   ██████░░░░  MEDIUM
```

---

## 3. Detailed Risk Register

### Risk 1: Scientific Overclaiming

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #1 |
| **Description** | CathodeScope outputs or thesis text make claims that exceed the evidence level of the underlying data. Examples: calling a proxy result "validated," claiming "discovery" for known-material analysis, presenting MACE-computed values as "accurate" without reference comparison. This is the single most dangerous risk — it can invalidate the thesis. |
| **Likelihood** | Medium — easy to overclaim in natural language; thesis pressure amplifies it |
| **Impact** | Critical — thesis credibility destroyed; may cause examination failure |
| **Severity** | **CRITICAL** |
| **Triggers** | Writing reports without consulting `scientific_validity_matrix.md`; copy-pasting results without evidence labels; summarizing Level C proxies alongside Level A results without clear separation; using "proved," "validated," "accurate," or "discovered" without qualification. |
| **Mitigations** | Hard validity matrix enforced at report generation time (`scientific_validity_matrix.md`); wording rules (Section 4: 10 rules) checked programmatically where possible; anti-claims enforced (`master_plan.md` Section 2); evidence labels mandatory in every report section (`scientific_validity_matrix.md` Section 5); code review for all report templates. |
| **Contingency** | If overclaiming is detected post-generation: re-generate report with corrected wording, audit all existing reports, add the offending pattern to the disallowed wording list. |

---

### Risk 2: Scope Creep

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #2 |
| **Description** | Features outside the MVP boundary are implemented before the MVP is complete. Examples: adding voltage estimation before the structural analysis pipeline works; building a web UI before the CLI; implementing agent orchestration before Phase 4 gate is passed. |
| **Likelihood** | High — natural inclination to build exciting features; advisor or reviewer requests may push scope |
| **Impact** | Critical — delays thesis-core completion; introduces untested complexity; violates phase gates |
| **Severity** | **CRITICAL** |
| **Triggers** | Boredom with "plumbing" work (models, tests); external suggestions to add features; feeling that the MVP is "too simple"; comparing against more feature-rich tools. |
| **Mitigations** | Phase gates are mandatory (`master_plan.md` Section 6); identity test for every feature ("Does this fit within a reproducible scientific workflow platform for benchmarked cathode screening?"); "Do not build yet" list in `implementation_order.md` Section 6; decision log in `master_plan.md` Section 10 records all scope decisions. |
| **Contingency** | If scope creep occurs: stop, assess how far out of scope the work is, determine if it can be completed without delaying the current phase gate, or revert and defer. |

---

### Risk 3: Thesis Timeline Pressure

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #9 |
| **Description** | External deadline pressure creates temptation to skip Phase 4 hardening, rush testing, weaken scientific rigor, or jump directly to "flashy" features (agent, web UI) without completing the deterministic core. |
| **Likelihood** | High — thesis deadlines are real and inflexible |
| **Impact** | Critical — skipping hardening means thesis claims are indefensible; skipping testing means silent failures go undetected |
| **Severity** | **CRITICAL** |
| **Triggers** | Approaching thesis submission deadline; slow progress on plumbing work; advisor pressure to show results; comparing progress against peers. |
| **Mitigations** | Phase gates enforce minimum viable quality (`master_plan.md` Section 6); Phase 4 is the hard deadline for thesis-core — if Phase 4 is complete, the thesis is defensible even without Phases 5-7; keep the MVP narrow (3 materials, 1 workflow); resist feature additions under pressure. |
| **Contingency** | If timeline is critically tight: the thesis can succeed with Phases 1-4 alone (`master_plan.md` Section 2: "The thesis can succeed without [agent orchestration]"). Prioritize Phase 4 hardening over any new features. |

---

### Risk 4: Hardware/Runtime Mismatch

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #3 |
| **Description** | MACE relaxation is too slow on the development machine, exceeds available memory, or produces different results on different hardware (CPU vs GPU, different floating-point implementations). |
| **Likelihood** | Medium — MACE-MP-0 is designed for reasonable compute, but LiMn2O4 (56 atoms) may stress CPU-only execution |
| **Impact** | Medium — slows development; may prevent CI from running benchmarks; reproducibility at risk |
| **Severity** | **HIGH** |
| **Triggers** | Large unit cells (spinel has 56 atoms in conventional cell); CPU-only execution on a laptop; CI runner with limited resources; different numpy/PyTorch versions producing different floating-point results. |
| **Mitigations** | Small benchmark set first (3 materials, small cells); CPU-only for MVP (`tech_stack.md` assumption); strict version pinning; reproducibility criterion allows 0.1% deviation between runs (`benchmark_spec.md` Section 6); profile relaxation times early in Phase 1. |
| **Contingency** | If CPU is too slow: use a smaller MACE model variant if available, or run benchmarks on a machine with GPU access. If reproducibility fails across platforms: document the platform-specific behavior, run benchmarks on a single reference machine, and note the platform in provenance. |

---

### Risk 5: Premature Agent Complexity

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #4 |
| **Description** | Agent orchestration is attempted before the deterministic workflow stack is complete, tested, and benchmarked. The agent becomes a crutch that masks pipeline issues or introduces non-deterministic behavior into the scientific workflow. |
| **Likelihood** | Medium — agents are exciting; LLM tools are trendy; there is temptation to build the "cool part" early |
| **Impact** | High — agent adds complexity to an untested stack; agent failures conflate with pipeline bugs; trust in results is undermined |
| **Severity** | **HIGH** |
| **Triggers** | Phase 1-3 feels repetitive; desire to demonstrate agent capabilities; external interest in the "AI" aspect. |
| **Mitigations** | Phase 5 gate requires Phase 4 complete (`master_plan.md` Phase 5 dependencies); agent module directory exists but is empty in MVP (`architecture.md` Section 9); agent depends on `workflows/engine.py`, not `tools/*` (`architecture.md` Diagram 3); agent-routed results must match scripted results (`master_plan.md` Phase 5 gate). |
| **Contingency** | If agent work starts too early: stop, complete the Phase 4 gate first, then resume agent work. No code in `agent/` until Phase 4 gate is documented as passed. |

---

### Risk 6: Benchmark Proves Orchestration but Not Science

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #5 |
| **Description** | The benchmark demonstrates that the pipeline runs end-to-end ("it didn't crash") but does not actually validate scientific quality. Lattice parameter deviations are recorded but not scrutinized. Reports are generated but evidence labels are not verified. The benchmark becomes a checkbox exercise. |
| **Likelihood** | Medium — natural tendency to celebrate "it ran" without examining "it produced correct results" |
| **Impact** | High — false confidence in pipeline quality; thesis claims rest on untested scientific outputs |
| **Severity** | **HIGH** |
| **Triggers** | Rushing through Phase 2 to get to "more interesting" work; not reading generated reports; automating benchmark without reviewing results; treating runtime as the only metric that matters. |
| **Mitigations** | Quantitative deviation thresholds are first-class metrics (`benchmark_spec.md` Section 4: lattice < 2%, volume < 5%); success categories are based on scientific quality, not just completion (`benchmark_spec.md` Section 5); evidence labeling completeness is a benchmark metric; every benchmark run must produce a reviewed report. |
| **Contingency** | If benchmark results are suspect: manually verify one material's results against MP data. Hand-compute lattice parameter deviations and compare against automated values. If they disagree, there is a bug in the comparator. |

---

### Risk 7: Dependency Brittleness

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #6 |
| **Description** | External dependencies (MP API, MACE, pymatgen, ASE) change their API, behavior, or availability, breaking CathodeScope's pipeline. |
| **Likelihood** | Medium — MP API has changed formats in the past; pymatgen and ASE have breaking changes between major versions; MACE is under active development |
| **Impact** | Medium — development blocked until compatibility is restored; benchmark results may become non-reproducible across software versions |
| **Severity** | **HIGH** |
| **Triggers** | Running `pip install --upgrade`; MP API version change; MACE-MP-0 checkpoint update; pymatgen deprecating a function used in normalization or comparison. |
| **Mitigations** | Version-locked dependencies in `pyproject.toml` and lock file; cached MP responses for offline development and testing (`artifact_schema.md` Section 5); mock-first unit tests that don't depend on external services; MACE model checkpoint pinned by version and recorded in provenance (`architecture.md` Section 8). |
| **Contingency** | If a dependency breaks: use the locked version. If the locked version is no longer installable, document the issue, find the minimal version change needed, test the benchmark, and update the lock file. Record the change in the decision log (`master_plan.md` Section 10). |

---

### Risk 8: Reproducibility Failure

| Field | Detail |
|-------|--------|
| **Source** | New risk derived from `benchmark_spec.md` Section 6 (reproducibility criterion) |
| **Description** | Re-running the benchmark on the same machine with the same environment does not produce the same result category. Lattice parameter deviations differ by more than 0.1% between runs. Space group changes between runs. This undermines the fundamental claim of reproducibility. |
| **Likelihood** | Medium — floating-point non-determinism in numpy/PyTorch, thread scheduling affecting MACE computation order, random seed differences in optimizers |
| **Impact** | High — reproducibility is a Phase 1 gate criterion and a thesis-core claim; failure here is a thesis-level problem |
| **Severity** | **HIGH** |
| **Triggers** | Different numpy/PyTorch versions; multi-threaded MACE execution; different CPU architectures (ARM vs x86); optimizer sensitivity to numerical noise near convergence. |
| **Mitigations** | Pin all dependency versions; use deterministic MACE configuration if available; set random seeds explicitly; run benchmark twice during Phase 1 to verify reproducibility; `benchmark_spec.md` allows 0.1% deviation tolerance for lattice parameters between runs; document the reference platform in provenance. |
| **Contingency** | If reproducibility fails: investigate the non-deterministic component (numpy threading, MACE execution order). Set `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1` to force single-threaded execution. If the issue is in MACE, document it as a known limitation and define a wider reproducibility tolerance with justification. |

---

### Risk 9: Provenance Gaps

| Field | Detail |
|-------|--------|
| **Source** | New risk derived from `artifact_schema.md` Section 7 (completeness checklist) |
| **Description** | Workflow runs produce incomplete provenance records. Software versions are not captured. Configuration snapshots are missing. Parent artifact linkage is broken. The provenance DAG has gaps. This undermines reproducibility and auditability claims. |
| **Likelihood** | Medium — provenance is "boring" metadata that is easy to skip during implementation; bugs in provenance recording are easy to miss because they don't affect scientific results |
| **Impact** | Medium — an audit reveals gaps; a reviewer asks "which MACE version produced this?" and the answer isn't recorded; reproducibility claims are weakened |
| **Severity** | **HIGH** |
| **Triggers** | Implementing tools without populating the `ProvenanceRecord`; forgetting to capture `dependencies` or `config_snapshot`; not running the completeness checklist after workflow runs; not testing provenance in unit tests. |
| **Mitigations** | Post-run integrity check confirms all items in `artifact_schema.md` Section 7 checklist have corresponding files; `ProvenanceRecord` is a mandatory field in every record type (pydantic validation rejects records without it); unit tests verify provenance is populated for each tool; CI includes an integrity check step. |
| **Contingency** | If gaps are discovered after multiple runs: add a migration script that reconstructs provenance from available data (software versions from the lock file, timestamps from file metadata). Prevent future gaps by adding provenance assertions to integration tests. |

---

### Risk 10: Bad Report Wording

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #8, expanded with `scientific_validity_matrix.md` wording rules |
| **Description** | Generated reports use vague, narrative, or overclaiming language. Reports say "good agreement" instead of "within 2% of reference." Reports omit evidence level labels. Reports present Level C proxies alongside Level A results without visual separation. This is a specialized form of Risk 1 (overclaiming) that operates at the report generation layer. |
| **Likelihood** | Medium — template writing naturally drifts toward narrative; evidence labels feel like clutter until you realize they are the point |
| **Impact** | Medium — reports lose scientific credibility; thesis examiner questions wording rigor; reports cannot be cited without qualification |
| **Severity** | **MEDIUM** |
| **Triggers** | Writing report templates without consulting `scientific_validity_matrix.md` Section 4 (10 wording rules); prioritizing readability over precision; not reviewing generated reports for compliance; using natural-language summaries that abstract away evidence levels. |
| **Mitigations** | Machine-readable report schema (`report.json`) first, Markdown rendering second (`architecture.md` Section 4.7: "JSON report is the primary artifact"); automated checks for evidence labels in Markdown output; wording rules programmatically enforced where feasible (e.g., regex check that "validated" never appears without qualification); report generation unit tests include wording compliance checks. |
| **Contingency** | If bad wording is found in generated reports: update the Markdown template, re-generate all affected reports from stored `WorkflowResult` data (reports are always regenerable from structured data per `artifact_schema.md` design principle). |

---

### Risk 11: Extension-Interface Instability

| Field | Detail |
|-------|--------|
| **Source** | `master_plan.md` Risk #7 |
| **Description** | The extension hooks defined in `architecture.md` (registries, plugin interfaces, `ToolResult` contract) turn out to be too vague, too rigid, or incorrectly designed when actual extensions are attempted in Phase 5-6. This forces a rewrite of core interfaces during later phases. |
| **Likelihood** | Low — interfaces are well-specified in `architecture.md`; the `ToolResult` contract is simple and generic; registries are a proven pattern |
| **Impact** | Medium — core interface changes require updating all existing tools; may break benchmark reproducibility across versions |
| **Severity** | **MEDIUM** |
| **Triggers** | A Phase 5/6 extension that doesn't fit the `ToolResult` contract (e.g., needs streaming results); a workflow that requires parallel step execution but the engine only supports sequential; a data source that doesn't fit the `DataSource` interface. |
| **Mitigations** | Interface contracts reviewed at each phase gate (`master_plan.md` Section 10, deferral rules); `ToolResult` contract is deliberately minimal and generic; extension hooks are documented with future use cases in mind (`architecture.md` Section 4.4.7: future tool contracts already sketched). |
| **Contingency** | If an interface is found inadequate: version the interface (MAJOR bump per `artifact_schema.md` Section 4); provide an adapter for existing tools to work with the new interface; do not break the benchmark by changing interfaces mid-phase. |

---

## 4. Risk-Phase Interaction Map

Which risks are most active in which phases:

```
              Phase 1    Phase 2    Phase 3    Phase 4    Phase 5    Phase 6
              MVP-0      Bench.     Report     Harden     Agent      Extend
              ------     ------     ------     ------     ------     ------
Overclaim     ░░░░░░     ░░░░░░     ██████     ██████     ██████     ██████
Scope creep   ██████     ██████     ██████     ░░░░░░     ██████     ██████
Timeline      ░░░░░░     ░░░░░░     ██████     ██████     ░░░░░░     ░░░░░░
HW mismatch   ██████     ██████     ░░░░░░     ░░░░░░     ░░░░░░     ░░░░░░
Agent early   ░░░░░░     ██████     ██████     ██████     ░░░░░░     ░░░░░░
Bench = orch  ░░░░░░     ██████     ░░░░░░     ██████     ░░░░░░     ░░░░░░
Dep. brittle  ██████     ░░░░░░     ░░░░░░     ██████     ░░░░░░     ██████
Repro fail    ██████     ██████     ░░░░░░     ██████     ░░░░░░     ░░░░░░
Provenance    ██████     ██████     ░░░░░░     ██████     ░░░░░░     ░░░░░░
Bad wording   ░░░░░░     ░░░░░░     ██████     ██████     ██████     ██████
Ext. interf.  ░░░░░░     ░░░░░░     ░░░░░░     ░░░░░░     ██████     ██████
```

`██████` = risk is highly active in this phase
`░░░░░░` = risk is dormant or low in this phase

---

## 5. Top 3 Risks Requiring Immediate Attention (Phase 1)

1. **Dependency brittleness (Risk 7)**: Lock all dependency versions before writing any tool code. Create cached MP response fixtures before implementing the MP client. This must happen in implementation Step 1-2.

2. **Hardware/runtime mismatch (Risk 4)**: Verify MACE-MP-0 installs and runs on the development machine before writing the structure relaxer. Run a single LiCoO2 relaxation manually to measure runtime and memory usage. This must happen before implementation Step 6.

3. **Reproducibility failure (Risk 8)**: Run the LiCoO2 acceptance test twice at the end of Phase 1. Compare lattice parameter deviations. If they differ by more than 0.1%, investigate before proceeding to Phase 2.

---

## Cross-Reference Index

| Topic | Related Document | Section |
|-------|-----------------|---------|
| Original risk register | `master_plan.md` | Section 9 |
| Severity matrix and response protocol | `master_plan.md` | Section 9 |
| Wording rules (Risk 10 mitigation) | `scientific_validity_matrix.md` | Section 4 |
| Reproducibility criterion (Risk 8) | `benchmark_spec.md` | Section 6 |
| Completeness checklist (Risk 9) | `artifact_schema.md` | Section 7 |
| Evidence label format (Risk 10) | `scientific_validity_matrix.md` | Section 5 |
| Anti-claims (Risk 1) | `master_plan.md` | Section 2 |
| Phase gates (Risk 2, 5 mitigation) | `master_plan.md` | Section 6 |
| Extension hooks (Risk 11) | `architecture.md` | Section 7 |

---

*Every risk in this document maps to a mitigation. Every mitigation maps to a concrete action. Risks are reviewed at each phase gate per `master_plan.md` Section 6.*
