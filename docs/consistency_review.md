# CathodeScope Internal Consistency Review

**Version**: 2.1.0
**Date**: 2026-03-10
**Status**: Pre-Implementation Audit — Fixes Applied
**Fixes Applied**: 2026-03-10 — All Critical and High issues resolved; Medium issues addressed where feasible
**Scope**: All 13 documents in `docs/`
**Reviewer**: Automated architectural and scientific-consistency review
**Standard**: Scientific defensibility over ambition; strict interpretation of all inter-document contracts

---

## Table of Contents

1. [Contradictions Across Documents](#1-contradictions-across-documents)
2. [MVP Scope Overreach](#2-mvp-scope-overreach)
3. [Scientific Overclaiming Risks](#3-scientific-overclaiming-risks)
4. [Vague Interfaces Likely to Cause Redesign](#4-vague-interfaces-likely-to-cause-redesign)
5. [Underspecified Benchmark Definitions](#5-underspecified-benchmark-definitions)
6. [Missing Reporting Fields for Reproducibility](#6-missing-reporting-fields-for-reproducibility)
7. [Agent Layer Still Too Central](#7-agent-layer-still-too-central)
8. [Missing Acceptance Criteria](#8-missing-acceptance-criteria)
9. [Critical Fixes Before Coding](#9-critical-fixes-before-coding)
10. [Safe to Defer](#10-safe-to-defer)
11. [Suggested Document Edits](#11-suggested-document-edits)

---

## 1. Contradictions Across Documents

---

### CR-01: WorkflowResult status enum — 4 values vs. 5

| Field | Detail |
|-------|--------|
| **Severity** | **CRITICAL** |
| **Where** | `architecture.md` Section 4.3 (output contract) vs. `artifact_schema.md` Section 2.2 vs. `benchmark_spec.md` Section 5 |
| **Finding** | `architecture.md` Section 4.3 defines the WorkflowResult output contract with `status: "success" | "partial_success" | "soft_failure" | "hard_failure"` (4 values). The same section's status determination table includes `infrastructure_failure` at priority 1 — contradicting its own output contract. `artifact_schema.md` Section 2.2 correctly defines all 5 statuses. `benchmark_spec.md` Section 5 also uses all 5. The architecture doc is internally inconsistent and inconsistent with the other two documents. |
| **Why it matters** | The pydantic model in `models/results.py` must use a `Literal` type. A developer reading only the architecture output contract will define 4 values. All infrastructure failure paths will break at serialization. This is the most-referenced enum in the entire codebase. |
| **Correction** | Add `"infrastructure_failure"` to the status enum in `architecture.md` Section 4.3 output contract. The 5-value list in `artifact_schema.md` is authoritative. |

---

### CR-02: ProvenanceRecord — 3 fields silently dropped in TDD breakdown

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `artifact_schema.md` Section 2.5 (12 fields) vs. `tdd_task_breakdown.md` T-01 (10 fields) |
| **Finding** | `artifact_schema.md` defines `ProvenanceRecord` with 12 fields: `schema_version`, `created_at`, `created_by`, `cathodescope_version`, `python_version`, `dependencies`, `config_snapshot`, `input_hash`, `parent_ids`, `mace_checkpoint_hash`, `mp_database_version`, `platform`, `notes`. T-01 says "Fields per `artifact_schema.md` Section 2.5" but then lists only 10 — omitting `mace_checkpoint_hash`, `mp_database_version`, and `platform`. No rationale for the omission. |
| **Why it matters** | `mace_checkpoint_hash` is the only way to verify which MACE model produced a result. `mp_database_version` is needed to explain reference value changes. `platform` explains cross-machine numerical differences. Omitting these from the pydantic model means they can never be recorded. |
| **Correction** | Update T-01 to include all 12 fields. Add nullable types for the 3 missing fields (they are null when irrelevant to the step). Add tests: `test_provenance_record_mace_checkpoint_hash_is_optional()`, `test_provenance_record_mp_database_version_is_optional()`, `test_provenance_record_platform_is_string()`. |

---

### CR-03: Angle deviation used for classification but never recorded

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `benchmark_spec.md` Section 4 (metric table) vs. Section 5 (formal threshold table) |
| **Finding** | The formal threshold table in Section 5 classifies runs by angle deviation: < 1deg Full Success, 1-3deg Partial Success, > 3deg Soft Failure, "structure collapsed" Hard Failure. But Section 4's metric table (the definitive list of what each run records) does not include angle deviation. Angles are used for classification but never measured, stored, or reported. |
| **Why it matters** | Classification decisions must trace to recorded values. If an examiner asks "why Partial Success?" and the answer is "angle deviation of 2deg," but no angle metric exists, the classification is unjustifiable. Additionally, `tdd_task_breakdown.md` T-23 lists "all 18 metrics" — none are angle deviations. |
| **Correction** | Add `angle_deviation_alpha`, `angle_deviation_beta`, `angle_deviation_gamma` (float, degrees) to Section 4's metric table. Success criterion: < 1deg for Full Success, matching Section 5. Update T-23 metric list. |

---

### CR-04: Implementation order conflicts between master_plan.md and implementation_order.md

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `master_plan.md` Section 11 (12-step conceptual order) vs. `implementation_order.md` Section 2 (16-step build order) |
| **Finding** | `master_plan.md` lists "artifact/provenance storage" at step 7, then "report generation" at step 8. `implementation_order.md` places validation layer at step 8, artifact store at step 9, report generator at step 10. The mapping table in `implementation_order.md` Section 7 adds further confusion (e.g., Step 4 "Input resolver" maps to "Step 2-3" in master_plan, which makes no sense). Both claim to follow data flow dependencies, but they produce different orderings. |
| **Why it matters** | Two competing sequences create ambiguity about which is authoritative. |
| **Correction** | Declare `implementation_order.md` as the authoritative build sequence (it is more granular). Add a note to `master_plan.md` Section 11: "This is a conceptual ordering. See `implementation_order.md` for the binding implementation sequence." Fix or remove the mapping table in `implementation_order.md` Section 7. |

---

### CR-05: Configuration system specified as both dataclasses and pydantic

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `architecture.md` Section 8 vs. `tech_stack.md` Section 4 vs. `tdd_task_breakdown.md` T-05 |
| **Finding** | `architecture.md` Section 8 specifies "Python dataclasses + JSON" for configuration. `tech_stack.md` Section 6 says "pydantic v2+ models + JSON config files." `tdd_task_breakdown.md` T-05 explicitly defines config models as pydantic (`RelaxationConfig`, `ComparisonConfig`, etc.). Dataclasses and pydantic have different validation semantics, serialization APIs, and error messages. |
| **Why it matters** | An implementer reading `architecture.md` alone will use dataclasses. An implementer reading T-05 will use pydantic. These are not interchangeable. |
| **Correction** | Standardize on pydantic v2+ for all config models (consistent with the project-wide pydantic decision). Update `architecture.md` Section 8 accordingly. |

---

### CR-06: Metric count: "18 metrics" vs. 20 rows in benchmark_spec.md

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `benchmark_spec.md` Section 4 vs. `tdd_task_breakdown.md` T-23 |
| **Finding** | `benchmark_spec.md` Section 4 says "No metric is optional" and lists 20 rows including `runtime_seconds` and `workflow_version`. T-23 says "all 18 metrics" and lists 18 keys excluding those two. The number "18" appears nowhere in `benchmark_spec.md`. The discrepancy creates confusion about which metrics must be in `BenchmarkRow.metrics`. |
| **Why it matters** | If `runtime_seconds` and `workflow_version` are excluded from the metrics dict, the "no metric is optional" rule is violated. |
| **Correction** | Update `benchmark_spec.md` to state: "20 metrics total, of which 18 have success criteria and 2 are informational-only." Update T-23 to include all 20 metrics in the dict. |

---

### CR-07: Broken cross-reference in architecture.md

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `architecture.md` Section 2 |
| **Finding** | References "master_plan.md Section 13." `master_plan.md` ends at Section 11. Likely intended Section 4 (Out of Scope). |
| **Why it matters** | Broken references erode document trust. |
| **Correction** | Change "Section 13" to "Section 4 (Out of Scope with Rationale)." |

---

### CR-08: ReportRecord.raw_user_input present in schema but absent from TDD

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `artifact_schema.md` Section 2.4 vs. `tdd_task_breakdown.md` T-04, T-15 |
| **Finding** | `artifact_schema.md` defines `raw_user_input: string` on `ReportRecord`. Neither T-04 (model definition) nor T-15 (JSON report builder) mention this field. |
| **Why it matters** | Without `raw_user_input`, reports cannot show what the user originally typed, which matters for provenance traceability. |
| **Correction** | Add field and test to T-04. Populate from `NormalizedQuery.raw_input` in T-15. |

---

## 2. MVP Scope Overreach

---

### SC-01: Per-element bond length and coordination analysis in Phase 1 comparator

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `architecture.md` Section 4.4.4, `tdd_task_breakdown.md` T-11 |
| **Finding** | The reference comparator is expected to compute Li-O bond lengths, M-O bond lengths, and coordination numbers. This requires choosing appropriate neighbor-finding cutoffs per element pair, handling mixed coordination environments (LiFePO4 has Li-O octahedra, Fe-O octahedra, P-O tetrahedra), and matching sites between structures. The benchmark pass/fail criteria use only lattice deviations (< 2%), volume deviation (< 5%), symmetry preservation, and global bond length bounds (1.0-4.0 A). Per-pair analysis has no pass/fail threshold. |
| **Why it matters** | Significant implementation complexity (cutoff sensitivity, mixed oxidation states, site matching) for metrics that are purely informational in Phase 1. This is the most likely Phase 1 scope sink. |
| **Correction** | For Phase 1: implement only global min/max bond length (already in benchmark metrics), lattice deviations, volume deviation, symmetry check. Defer per-element bond analysis and coordination numbers to Phase 4. Remove `test_compare_bond_lengths_li_o()`, `test_compare_bond_lengths_metal_o()`, `test_compare_coordination_numbers()` from T-11. |

---

### SC-02: Five registries for one workflow

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `architecture.md` Section 4.3 Phase 1 note |
| **Finding** | Five registries planned for Phase 1: `WorkflowRegistry`, `NormalizationStrategyRegistry`, `ComparisonMetricRegistry`, `FamilyValidatorRegistry`, `SectionRegistry`. Each has exactly 1 entry. Five registries for five singletons is premature abstraction that adds ~300-500 lines of boilerplate. |
| **Why it matters** | Registry infrastructure delays the first working run. The Phase 1 gate is "LiCoO2 processes end-to-end," not "plugin architecture is extensible." |
| **Correction** | Implement only `WorkflowRegistry` in Phase 1 (justified by benchmark runner needing workflow lookup). Use direct function calls for the other 4. Add registries in Phase 4 when a second implementation exists. |

---

### SC-03: Wyckoff position analysis in normalizer

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `architecture.md` Section 4.4.2, `tdd_task_breakdown.md` T-09 |
| **Finding** | Normalizer output includes `wyckoff_positions` (marked nullable) with a corresponding test `test_normalize_data_contains_wyckoff_positions()`. No downstream MVP module consumes Wyckoff data. No benchmark metric requires it. No report section references it. |
| **Why it matters** | Wyckoff analysis is crystallographically non-trivial and version-sensitive. Implementation effort with zero MVP payoff. |
| **Correction** | Remove Wyckoff from the normalizer output contract. Remove the test. Return `null`. Add as Phase 4 enhancement. |

---

### SC-04: Transformation matrix as a tested output

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `tdd_task_breakdown.md` T-09 |
| **Finding** | `test_normalize_data_contains_transformation_matrix()` tests for the primitive-to-conventional conversion matrix. No downstream module uses it. |
| **Why it matters** | Minor scope inflation. Can be logged in provenance without being a tested contract. |
| **Correction** | Remove dedicated test. Log matrix in provenance if available. |

---

## 3. Scientific Overclaiming Risks

---

### OC-01: Level A assigned unconditionally to MACE relaxation — conditional trust not enforced

| Field | Detail |
|-------|--------|
| **Severity** | **CRITICAL** |
| **Where** | `scientific_validity_matrix.md` Row 3 Notes vs. `tdd_task_breakdown.md` T-13 |
| **Finding** | Row 3 notes: "Level A is conditional on the material belonging to a benchmarked cathode family. Materials outside benchmarked families should be treated as Level B until benchmark coverage is extended." But T-13 maps `relax` -> `A-computed` unconditionally with no family check. The evidence label assigner ignores the conditionality that the validity matrix explicitly states. |
| **Why it matters** | If a user analyzes NMC-111 or LiNiO2 (not in the benchmark set), the system silently assigns Level A to results that have never been benchmarked. This is the exact overclaiming scenario the validity matrix was designed to prevent. |
| **Correction** | The evidence assigner must accept material family and benchmark status as inputs. Non-benchmarked families receive `B-restricted`, not `A-computed`. Add test: `test_label_relaxed_structure_as_b_restricted_for_non_benchmarked_family()`. Update T-13 implementation notes. |

---

### OC-02: "Benchmarked" claim based on 3 materials — no mandatory qualifier

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `scientific_validity_matrix.md` Level A definition, report templates |
| **Finding** | Level A means "produced by a workflow that has passed benchmark validation against known reference materials." With only 3 materials (one per family), the benchmark is a 3-point sample. Reports carry Level A labels but never state *how many* materials underpin that label. An examiner reading "[Level A -- computed]" has no immediate visibility into the benchmark scope. |
| **Why it matters** | "Benchmarked" without "against N materials" is misleading by omission. The narrowness of the benchmark should be visible at every point the label appears. |
| **Correction** | Require the report assessment section to state: "benchmarked against 3 known cathode materials (LiCoO2, LiFePO4, LiMn2O4)." Update `scientific_validity_matrix.md` Section 5 mock excerpt. Update T-16 Markdown renderer to include benchmark scope in assessment paragraph. |

---

### OC-03: Overclaiming verbs in benchmark descriptions

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `master_plan.md` Section 7, `benchmark_spec.md` Section 1, `demo_strategy.md` |
| **Finding** | `master_plan.md` Section 7: "The benchmark validates CathodeScope's pipeline" (violates Rule 5). `benchmark_spec.md` Section 1: "The MVP benchmark proves that CathodeScope produces correct, reproducible, evidence-labeled results" (violates Rule 7 "never use proved" AND uses unqualified "correct"). The validity matrix's own wording rules prohibit this language. |
| **Why it matters** | Self-contradiction: the documents defining wording discipline violate their own rules. An examiner who reads both will notice. |
| **Correction** | Replace with: "The benchmark tests whether CathodeScope produces results consistent with MP references within defined thresholds." Apply systematically across `master_plan.md` Section 7, `benchmark_spec.md` Section 1, `demo_strategy.md`. |

---

### OC-04: "Trusted" as the Level A label

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `scientific_validity_matrix.md` Section 2, `subject_matter_expert_onboarding.md` Section 7 |
| **Finding** | Level A is labeled "Trusted" throughout. "Trusted" implies unconditional reliability. Computational results from an ML potential trained on DFT data, benchmarked against 3 materials, are not unconditionally trustworthy — they are reproducible and referenced. |
| **Why it matters** | An examiner may challenge: "You call these 'Trusted' — trusted by whom? On what basis?" A more neutral label is harder to challenge. |
| **Correction** | Consider renaming Level A from "Trusted" to "Benchmarked" or "Reference-compared." The label then describes the methodology, not a subjective quality judgment. |

---

### OC-05: No programmatic enforcement of anti-claims

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `master_plan.md` Section 2 (anti-claims), report generation pipeline |
| **Finding** | Four anti-claims are documented but enforcement is entirely manual. T-16 has `test_markdown_no_disallowed_words()` but this only covers the renderer output and only checks a few terms. No check covers agent outputs, CLI messages, log entries, or the JSON report data values. |
| **Why it matters** | Overclaiming is the #1 risk (Critical severity). Critical risks require automated mitigation, not manual review. |
| **Correction** | Create a `DISALLOWED_PHRASES` list in `validation/evidence.py`. Add `check_wording_compliance(text: str) -> list[str]`. Call it in the report generator. Test with every anti-claim phrase. Extend to CLI output messages. |

---

## 4. Vague Interfaces Likely to Cause Redesign

---

### VI-01: WorkflowContext — typed container vs. mutable dict

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `architecture.md` Section 4.3 vs. `tdd_task_breakdown.md` T-18 |
| **Finding** | `architecture.md` defines `WorkflowContext` as a formal typed container with named fields (`material`, `normalized_query`, `step_results`, `config`, `workflow_run_id`, `started_at`) and states it is "a typed container — not a free-form dictionary." T-18 describes it as "mutable dict accumulating step results." These are different designs with different type safety, autocomplete, validation, and refactoring properties. |
| **Why it matters** | Every tool adapter accesses the context. Wrong choice cascades into every test. Changing after tools are written requires rewriting all adapter signatures. |
| **Correction** | Commit to `@dataclass` for `WorkflowContext` as defined in `architecture.md`. The `step_results: dict[str, StepResult]` field provides flexible step lookup within a typed shell. Update T-18 to remove "mutable dict" and test typed field access. |

---

### VI-02: Family classification algorithm undefined

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `architecture.md` Section 4.2, `tdd_task_breakdown.md` T-03 |
| **Finding** | `CanonicalMaterial.family` must be one of `layered_oxide | olivine_polyanion | spinel | other`. No document specifies how this value is assigned. Is it based on space group? Composition pattern? Manual lookup by mp_id? A classifier function? For 3 materials this is trivially hardcoded, but the interface must be explicit because family classification feeds evidence label assignment (per OC-01). |
| **Why it matters** | Wrong family -> wrong evidence level -> overclaiming. The classification algorithm must be testable and auditable. |
| **Correction** | Define rules: R-3m + LiMO2 composition -> `layered_oxide`; Pnma + LiMPO4 composition -> `olivine_polyanion`; Fd-3m + LiM2O4 composition -> `spinel`; everything else -> `other`. Implement as `classify_family(space_group: str, formula: str) -> str`. Add as T-08b or sub-task of T-08. Test all 3 benchmark materials plus an unknown. |

---

### VI-03: Two overlapping status classification systems

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `architecture.md` Section 4.3 vs. `benchmark_spec.md` Section 5 |
| **Finding** | The workflow engine determines `WorkflowResult.status` from step-level outcomes (crashes, warnings). The benchmark spec determines status from metric thresholds (lattice deviation ranges, angle ranges). A workflow engine might classify a run as `success` (all steps completed) while the benchmark threshold table classifies it as `partial_success` (lattice deviation 3%). `BenchmarkRow.status` uses the same enum. Nowhere is the interaction specified. |
| **Why it matters** | If the benchmark runner copies `WorkflowResult.status`, threshold-based classification is bypassed. If it re-classifies, the two statuses may conflict. The Phase 2 gate checks `BenchmarkRow.status` — which system determined it? |
| **Correction** | Document explicitly: `BenchmarkRow.status` is determined by the benchmark threshold table in Section 5, NOT by `WorkflowResult.status`. Add `classify_benchmark_status(metrics: dict) -> str` to the benchmark runner. `WorkflowResult.status` reflects pipeline completion; `BenchmarkRow.status` reflects scientific quality. Add a clarifying note to `benchmark_spec.md` Section 5. |

---

### VI-04: Step function signature vs. tool signature mismatch

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `architecture.md` Section 4.3 vs. Sections 4.4.1-4.4.6 |
| **Finding** | Section 4.3 specifies a uniform step signature: `step(context: WorkflowContext, config: StepConfig) -> StepResult`. But tools have diverse signatures: `mp_client(mp_id, fields)`, `normalizer(structure, symprec)`, `relaxer(structure, config)`, `validator(context, material, config)`. The architecture mentions an "adapter pattern" in passing but does not specify it. |
| **Why it matters** | Someone must write adapter functions that bridge the uniform step signature to tool-specific inputs. Without specification, each tool author invents their own adapter convention. |
| **Correction** | The `architecture.md` adapter pattern description exists but is buried. Elevate it: workflow definition modules (`structural_analysis.py`) contain per-step adapter functions that (1) extract inputs from context, (2) call the tool, (3) wrap output as StepResult. This is the binding pattern. Add an example adapter to `architecture.md` Section 4.3. |

---

### VI-05: CanonicalMaterial construction point undefined

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `architecture.md` Section 4.2, workflow step sequence |
| **Finding** | `CanonicalMaterial` is the central data object but no workflow step is designated as its constructor. The input resolver produces `NormalizedQuery`. The MP client returns structure + metadata. These must merge into a `CanonicalMaterial` with UUID, family, workflow eligibility, etc. No task covers this assembly. |
| **Why it matters** | Without a defined construction point, the material will be assembled ad-hoc in the workflow adapter, leading to inconsistent construction and missing fields. |
| **Correction** | Add `create_canonical_material(query: NormalizedQuery, mp_data: dict) -> CanonicalMaterial` factory function. Place in `models/material.py` or the workflow adapter. Add as sub-task of T-19. |

---

### VI-06: Report generator evidence type semantically incorrect

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `tdd_task_breakdown.md` T-17 |
| **Finding** | T-17 assigns `evidence_type: "A-computed"` to the report generator. Report generation is a rendering step — it assembles data into a document. It does not compute any scientific quantity. Labeling it `A-computed` inflates the evidence summary with a phantom scientific output. |
| **Why it matters** | The evidence summary would show an extra `A-computed` entry that corresponds to no science. An auditor reviewing the summary would be confused. |
| **Correction** | Either (a) exclude report generation from evidence accounting (compute evidence summary from steps 0-5 only, not step 6), or (b) remove the report generator from the workflow step sequence and treat it as a post-workflow rendering pass. Option (a) is simpler. |

---

## 5. Underspecified Benchmark Definitions

---

### BD-01: "Expected range" for bond lengths undefined

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `benchmark_spec.md` Section 5, formal threshold table |
| **Finding** | Full Success requires bond lengths "within 1.0-4.0 A and expected range." Partial Success: "within 1.0-4.0 A, outside expected range." The "expected range" is never defined per material or per family. What is the expected Li-O range in LiCoO2? The expected Mn-O range in LiMn2O4? |
| **Why it matters** | Without defined ranges, Full Success vs. Partial Success for bond lengths is subjective. Two implementations would disagree. |
| **Correction** | For MVP: simplify to hard bounds only (1.0-4.0 A pass, outside fail). Defer per-family expected ranges to Phase 4. Update the threshold table to remove "expected range" for Phase 1. |

---

### BD-02: "Near max_steps" undefined for convergence classification

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `benchmark_spec.md` Section 5 |
| **Finding** | Partial Success includes "converged but near max_steps." No quantitative definition of "near." 80%? 90%? 95%? This is a classification boundary that must be deterministic. |
| **Why it matters** | Subjective classification boundary on a gate-critical metric. |
| **Correction** | Define: `relaxation_steps > 0.8 * max_steps` downgrades convergence from Full Success to Partial Success. Add to threshold table. |

---

### BD-03: Reproducibility tolerance is a "starting estimate"

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `benchmark_spec.md` Section 6 |
| **Finding** | The 0.1% run-to-run tolerance is described as "a starting estimate pending empirical justification." This is not an acceptance criterion — it's a placeholder. If actual variance is 0.5%, the criterion fails or gets silently relaxed. |
| **Why it matters** | Reproducibility is a Phase 1 gate criterion. Soft criteria on gate-critical metrics undermine gate rigor. |
| **Correction** | During Phase 1: run LiCoO2 relaxation 5 times, measure variance, set tolerance to 3x observed standard deviation. Document the empirical basis before Phase 2. |

---

### BD-04: Symmetry tolerance not recorded as a metric

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `benchmark_spec.md` Section 4, `scientific_validity_matrix.md` Row 8 |
| **Finding** | Symmetry check uses `symprec` (default 0.1 A). Row 8 notes results are "sensitive to this parameter." But the benchmark metrics record only the binary `symmetry_preserved` result, not the tolerance used. |
| **Why it matters** | Two runs with different symprec produce different results from the same structure. Without recording the tolerance, symmetry results are not independently reproducible. |
| **Correction** | Add `symprec_used: float` as an informational metric in Section 4. Record in `BenchmarkRow.metrics`. |

---

### BD-05: Reference lattice parameters are approximate

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `benchmark_spec.md` Sections 3.1-3.3 |
| **Finding** | All three materials list lattice parameters with "~" (approximate) and notes like "(approximate; authoritative values are fetched from MP at runtime via `mp_client`)." The 2% deviation threshold is applied against the runtime-fetched values, not the listed values. This is correct behavior but the document is ambiguous — a reader might think the listed values are the reference. |
| **Why it matters** | Minor confusion risk. |
| **Correction** | Clarify: "The values listed below are approximate for documentation purposes. The authoritative reference for deviation calculations is always the value retrieved at runtime from the Materials Project API." |

---

## 6. Missing Reporting Fields for Reproducibility

---

### RF-01: No MACE model variant name in provenance

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `artifact_schema.md` Section 2.5 |
| **Finding** | `mace_checkpoint_hash` records the SHA-256 of the model file but not the human-readable model variant (e.g., "MACE-MP-0-medium" vs "MACE-MP-0-large"). The hash is useful for exact verification but tells a human nothing about which model was used. Different MACE-MP-0 sizes have different accuracy profiles. |
| **Why it matters** | Reproducibility requires knowing which model was used. "MACE-MP-0 medium" is actionable; "SHA-256: a1b2c3d4..." is not. A thesis reader needs both. |
| **Correction** | Add `mace_model_name: string | null` to `ProvenanceRecord`. Populate from `RelaxationConfig.mace_model`. |

---

### RF-02: No random seed recorded

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `artifact_schema.md` Section 2.5, `risk_heatmap.md` Risk 8 |
| **Finding** | Risk 8 identifies "random seed differences in optimizers" as a reproducibility trigger. The TDD doc mandates deterministic seeds in tests. But `ProvenanceRecord` has no `random_seed` field. If MACE or ASE uses a random seed, it cannot be recovered from provenance. |
| **Why it matters** | Reproducibility failure diagnosis requires knowing the seed. |
| **Correction** | Add `random_seeds: object | null` to `ProvenanceRecord`. Set explicit seeds in the relaxer and record them. If deterministic by default, document this and set to null. |

---

### RF-03: No compute device recorded

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `artifact_schema.md` Section 2.5 |
| **Finding** | `platform` records OS and architecture but not the compute device (CPU vs GPU). MACE on CPU vs GPU may produce different results due to floating-point operation ordering. |
| **Why it matters** | First diagnostic question for reproducibility issues is "CPU or GPU?" |
| **Correction** | Add `compute_device: string | null` (e.g., "cpu", "cuda:0", "mps"). Populate from PyTorch at relaxation time. |

---

### RF-04: Workflow step directory layout missing report step

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `artifact_schema.md` Section 3 vs. `architecture.md` Section 4.3 |
| **Finding** | Architecture defines 7 steps (0-6) including report generation. The artifact directory layout shows 6 step files (`00_resolve` through `05_validate`). No `06_generate_report.json`. |
| **Why it matters** | Implementer building the store will create an unexpected file or break the step-result contract. |
| **Correction** | Either add `06_generate_report.json` to the layout, or document that report generation does not produce a step file (it produces report artifacts separately). |

---

## 7. Agent Layer Still Too Central

---

### AG-01: Architecture.md devotes disproportionate attention to agent design

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `architecture.md` Sections 4.9, Diagrams 1 and 3, extension points throughout |
| **Finding** | Agent content appears in every major section: Diagram 1, Diagram 3 annotations, Section 4.3 extension points, Section 4.9 (detailed `AgentInterface` with `invoke_workflow`, `explain_result`, `suggest_next_steps` methods), and future tool contracts in Section 4.4. For a Phase 5 feature in a Phase 0 document, this level of detail is disproportionate. |
| **Why it matters** | Cognitive anchoring. Developers reading the architecture absorb the agent as a first-class concern, increasing temptation to design for agent compatibility (Risk 5). This contradicts `master_plan.md`: "agent is a usability layer added later." |
| **Correction** | Consolidate all agent content into a single appendix: "Phase 5: Agent Extension Points." Remove detailed agent interface (Section 4.9) — replace with one paragraph: "Agent orchestration is Phase 5. It interacts via WorkflowEngine only. Interface details TBD." Keep agent annotations in diagrams but add "(PHASE 5)" labels. |

---

### AG-02: "Tool schemas ready" implies agent-first design

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `master_plan.md` Section 4, "Agent orchestration" row |
| **Finding** | "Tool schemas ready" as an architecture hook implies tool APIs should be agent-compatible now. Tool APIs will evolve through Phases 1-4. Pre-designing for the agent constrains tool design for a hypothetical consumer. |
| **Why it matters** | Minor but reinforces the pattern in AG-01. |
| **Correction** | Change to "tool schemas will be derived from Phase 4 stable interfaces." |

---

### AG-03: Agent directory in Phase 1 skeleton

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `tdd_task_breakdown.md` Section 2 repo skeleton |
| **Finding** | The repo skeleton originally included `cathodescope/agent/__init__.py` with a comment "deferred to Phase 5." Its presence signals premature readiness. The TDD doc now says "directory will be created at that time" but the comment structure suggests it was originally part of the skeleton. |
| **Why it matters** | Trivial, but consistency with "no code in agent/ until Phase 4 gate passes." |
| **Correction** | Confirm agent directory is fully absent from Phase 1 skeleton. |

---

## 8. Missing Acceptance Criteria

---

### AC-01: No regression comparison tool in TDD breakdown

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `master_plan.md` Phase 2 gate vs. `tdd_task_breakdown.md` |
| **Finding** | Phase 2 gate requires: "Regression comparison possible (a script or CLI command compares two BenchmarkSummary JSON files and reports status changes and metric deltas)." No task in the TDD breakdown implements this. |
| **Why it matters** | The Phase 2 gate cannot be passed as defined. Regression comparison is how you detect that a code change degraded benchmark performance. |
| **Correction** | Add task T-24b: implement `compare_benchmarks(summary_a, summary_b) -> RegressionReport`. Test: status changes detected, metric deltas computed, new failures flagged. Expose via CLI: `cathodescope benchmark compare <path_a> <path_b>`. |

---

### AC-02: No acceptance criterion for offline operation

| Field | Detail |
|-------|--------|
| **Severity** | **HIGH** |
| **Where** | `master_plan.md` Phase 1 gate, `tech_stack.md` assumption 5 |
| **Finding** | `tech_stack.md` assumes cached responses enable offline development. Phase 1 gate requires "Offline pipeline completion with cached fixtures." But no test verifies this. The Phase 1 gate says it but the TDD breakdown (T-20) does not include an offline-mode test. |
| **Why it matters** | CI must be offline. If the pipeline makes an unexpected live API call when a cache entry is incomplete, CI breaks intermittently. |
| **Correction** | Add to T-20: `test_licoo2_end_to_end_runs_offline()` — disable network (mock or environment variable), verify pipeline completes using cached fixtures only. |

---

### AC-03: No acceptance criterion for provenance completeness

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `artifact_schema.md` Section 7 vs. `master_plan.md` Phase 1 gate |
| **Finding** | Section 7 defines a 10-item completeness checklist. Phase 1 gate says "Artifacts stored correctly per artifact_schema.md" but doesn't reference the Section 7 checklist specifically. No test runs the integrity check against a completed workflow run. |
| **Why it matters** | Provenance gaps are HIGH severity (Risk 9). Without a test, gaps are discovered only during Phase 4 — too late. |
| **Correction** | Add to Phase 1 gate: "Post-run integrity check per artifact_schema.md Section 7 passes." Add to T-20: `test_licoo2_integrity_check_passes()`. |

---

### AC-04: Artifact store integrity check fails on partial workflows

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `artifact_schema.md` Section 7 |
| **Finding** | The completeness checklist says "Missing artifacts indicate a bug in the pipeline, not a design choice." But for a `hard_failure` at step 3, steps 4-6 produce no artifacts. The integrity check as specified will always report "missing" files for failed runs. |
| **Why it matters** | The check becomes useless — it fires on every failure, producing noise rather than signal. |
| **Correction** | Specify that the integrity check validates artifacts up to the last completed step. Missing artifacts after the failure point are expected. Add test in T-06: `test_store_integrity_check_passes_for_partial_workflow(tmp_path)`. |

---

### AC-05: No acceptance criteria for cache TTL and invalidation

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `artifact_schema.md` Section 5, `tdd_task_breakdown.md` T-07 |
| **Finding** | Caching defines 30-day TTL, manual invalidation via `cathodescope cache clear`, and provenance logging of cache hits. T-07 tests write/read but not: TTL expiry, forced refresh, corrupt cache handling, or provenance recording of cache hits. |
| **Why it matters** | A stale cache serving outdated MP data produces wrong references with no warning. |
| **Correction** | Add to T-07: `test_mp_client_cache_expired_refetches()`, `test_mp_client_cache_clear_removes_data()`, `test_mp_client_provenance_records_cache_hit()`. |

---

### AC-06: "Publication-quality Markdown" is subjective

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `master_plan.md` Phase 3 gate |
| **Finding** | Gate criterion: "Reports are publication-quality Markdown." "Publication-quality" has no measurable definition. The gate is binary ("all criteria met or not") but this criterion is subjective. |
| **Why it matters** | Unjudgeable gate criteria undermine the gate system's purpose. |
| **Correction** | Replace with: "Reports render correctly in standard Markdown viewers. All section headers include evidence level labels. All quantitative values include units. Report structure matches `scientific_validity_matrix.md` Section 5 template." |

---

### AC-07: Import rule enforcement test exists in skeleton but no task implements it

| Field | Detail |
|-------|--------|
| **Severity** | **MEDIUM** |
| **Where** | `tdd_task_breakdown.md` Section 2 (lists `tests/test_import_rules.py`) |
| **Finding** | The repo skeleton includes `tests/test_import_rules.py` for architectural constraint enforcement. No task implements it. The import rules in `dependency_graph.md` Section 6 are critical invariants (e.g., "tools do not import from each other") with zero automated enforcement. |
| **Why it matters** | Import rule violations accumulate silently, creating hidden coupling. |
| **Correction** | Add to T-00: implement `tests/test_import_rules.py` using `ast.parse` to verify each package only imports from allowed packages per `dependency_graph.md` Section 6. |

---

### AC-08: No wall-clock timing expectation documented

| Field | Detail |
|-------|--------|
| **Severity** | **LOW** |
| **Where** | `benchmark_spec.md` Section 7 |
| **Finding** | Runtime is recorded but explicitly excluded from success criteria. No document states what "reasonable time" means for development workflow iteration. |
| **Why it matters** | If LiMn2O4 (56 atoms) takes 4 hours, development stalls. A non-functional timing target prevents silent performance regressions. |
| **Correction** | Add to `benchmark_spec.md`: "Informational timing target: single material pipeline completes in < 10 minutes wall-clock on the reference machine (CPU-only). Exceeding this triggers performance investigation, not benchmark failure." |

---

## 9. Critical Fixes Before Coding

These must be resolved before implementation begins. They affect data model definitions, core interfaces, or scientific credibility.

| Priority | Issue | Action |
|----------|-------|--------|
| 1 | **CR-01** Status enum mismatch | Add `infrastructure_failure` to `architecture.md` Section 4.3 output contract |
| 2 | **OC-01** Level A unconditional | Update T-13: evidence assigner must check family/benchmark status |
| 3 | **VI-01** WorkflowContext ambiguity | Commit to typed `@dataclass` in `architecture.md` and T-18 |
| 4 | **VI-02** Family classification undefined | Add classification rules and task (T-08b) |
| 5 | **VI-03** Two status classification systems | Document BenchmarkRow uses threshold table, not WorkflowResult.status |
| 6 | **CR-02** ProvenanceRecord missing 3 fields | Update T-01 to include all 12 fields |
| 7 | **CR-03** Angle deviation unrecorded | Add angle metrics to `benchmark_spec.md` Section 4 |
| 8 | **CR-05** Config: dataclasses vs pydantic | Standardize on pydantic in `architecture.md` Section 8 |
| 9 | **AC-01** Regression comparison missing | Add task T-24b |
| 10 | **BD-01** Bond length "expected range" undefined | Simplify to hard bounds for Phase 1 |

---

## 10. Safe to Defer

| Issue | Defer Until | Rationale |
|-------|-------------|-----------|
| **SC-01** Per-element bond analysis | Phase 4 | No pass/fail threshold in Phase 1 |
| **SC-02** Five registries | Phase 4 | One workflow doesn't need five registries |
| **SC-03** Wyckoff positions | Phase 4 | No downstream consumer |
| **SC-04** Transformation matrix test | Phase 4 | Log in provenance, don't test as contract |
| **OC-04** Rename "Trusted" to "Benchmarked" | Phase 3/4 | Label change propagates to all docs and templates |
| **OC-05** Anti-claim enforcement | Phase 4 | Manual review sufficient for 3 materials |
| **AG-01** Agent-heavy architecture | Phase 5 | Consolidate during Phase 5 kickoff |
| **AG-02** "Tool schemas ready" | Phase 5 | Wording change, low impact |
| **RF-02** Random seed recording | Phase 1 end | Add field during T-01 but justify value during Phase 1 |
| **RF-03** Compute device recording | Phase 1 end | Add field during T-01 |
| **BD-03** Reproducibility tolerance | Phase 1 end | Empirically determine during first relaxation runs |
| **BD-05** Reference value ambiguity | Phase 1 | Clarify wording, no functional change |
| **AC-06** Subjective gate criteria | Phase 3 | Replace before Phase 3 gate review |
| **AC-08** Wall-clock timing | Phase 1 end | Set after first benchmark run |

---

## 11. Suggested Document Edits

### Immediate (Before Coding)

| Document | Section | Edit |
|----------|---------|------|
| `architecture.md` | 2 | Fix cross-reference: "Section 13" -> "Section 4" |
| `architecture.md` | 4.3 | Add `infrastructure_failure` to status enum in output contract |
| `architecture.md` | 4.3 | Clarify `WorkflowContext` is a typed `@dataclass`, not a dict; add example adapter function |
| `architecture.md` | 4.3 | Reduce to 1 registry (WorkflowRegistry) for Phase 1 |
| `architecture.md` | 4.4.2 | Mark `wyckoff_positions` as deferred to Phase 4; remove from MVP output contract |
| `architecture.md` | 8 | Change "Python dataclasses + JSON" to "pydantic v2+ models + JSON config files" |
| `artifact_schema.md` | 2.5 | Add `mace_model_name`, `random_seeds`, `compute_device` to ProvenanceRecord |
| `artifact_schema.md` | 7 | Specify integrity check validates up to last completed step only |
| `benchmark_spec.md` | 1 | Replace "proves" and "correct" with threshold-based language |
| `benchmark_spec.md` | 4 | Add angle deviation metrics and `symprec_used` |
| `benchmark_spec.md` | 5 | Define "near max_steps" as > 0.8 * max_steps; simplify bond length to hard bounds |
| `benchmark_spec.md` | 5 | Add formal threshold table with all 5 categories and all metrics |
| `scientific_validity_matrix.md` | Row 3 | Add: evidence assigner MUST check family/benchmark status |
| `scientific_validity_matrix.md` | Section 5 | Add benchmark material count to assessment paragraph |
| `master_plan.md` | 7 | Replace "validates" with "tests whether ... within thresholds" |
| `master_plan.md` | 11 | Add note that `implementation_order.md` is the authoritative build sequence |
| `master_plan.md` | Phase 1 gate | Add: "Offline pipeline completion" and "Post-run integrity check" |
| `master_plan.md` | Phase 2 gate | Define regression comparison concretely |
| `implementation_order.md` | 7 | Fix or remove the master_plan mapping table |

### TDD Breakdown Updates

| Task | Edit |
|------|------|
| T-01 | Add all 12 ProvenanceRecord fields (including `mace_checkpoint_hash`, `mp_database_version`, `platform`, `mace_model_name`, `random_seeds`, `compute_device`) |
| T-04 | Add `raw_user_input` to ReportRecord |
| T-11 | Remove per-element bond length and coordination tests; keep global min/max |
| T-13 | Add family-conditional evidence labeling with test for non-benchmarked family |
| T-17 | Exclude report generation from evidence accounting |
| T-18 | Replace "mutable dict" with typed WorkflowContext dataclass |
| T-20 | Add offline mode test and integrity check test |
| New: T-08b | Family classification function with tests |
| New: T-24b | Benchmark regression comparison tool |
| T-00 | Add import rule enforcement test implementation |

### Phase 4 Edits

| Document | Edit |
|----------|------|
| `benchmark_spec.md` | Add per-family bond length expected ranges |
| `architecture.md` | Add remaining registries; consolidate agent content into appendix |
| `scientific_validity_matrix.md` | Consider renaming Level A "Trusted" to "Benchmarked" |
| CI pipeline | Add automated wording compliance checks and anti-claim enforcement |

---

## Summary Statistics

| Category | Count | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Contradictions | 8 | 1 | 2 | 3 | 2 |
| Scope overreach | 4 | 0 | 1 | 1 | 2 |
| Overclaiming risks | 5 | 1 | 1 | 3 | 0 |
| Vague interfaces | 6 | 0 | 4 | 2 | 0 |
| Benchmark underspecification | 5 | 0 | 1 | 3 | 1 |
| Missing reproducibility fields | 4 | 0 | 1 | 2 | 1 |
| Agent too central | 3 | 0 | 0 | 1 | 2 |
| Missing acceptance criteria | 8 | 0 | 2 | 4 | 2 |
| **Total** | **43** | **2** | **12** | **19** | **10** |

**Critical**: 2 (must fix before coding)
**High**: 12 (must fix before or during Phase 1)
**Medium**: 19 (fix during Phase 1-2 as encountered)
**Low**: 10 (defer to Phase 4+)

---

*This review prioritizes scientific defensibility. Every recommendation aims to make the thesis harder to challenge, the implementation harder to misunderstand, and the outputs harder to overclaim. Re-run this review after applying the immediate edits and again at each phase gate.*
