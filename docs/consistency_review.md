# CathodeScope Internal Consistency Review

**Version**: 5.0.0
**Date**: 2026-03-11
**Status**: Post-Fix Reassessment — All v4.0.0 Fixes Applied and Verified
**Scope**: All 14 documents in `docs/`
**Reviewer**: Automated architectural and scientific-consistency review
**Standard**: Scientific defensibility over ambition; strict interpretation of all inter-document contracts

**Review history**:
- v3.1.0 (2026-03-10): Initial review — 43 issues identified
- v4.0.0 (2026-03-11): Fresh audit after v3.1.0 fixes — 34 issues identified (9 resolved from v3.1.0)
- v5.0.0 (2026-03-11): Post-fix reassessment — all v4.0.0 fixes applied and verified

---

## Table of Contents

1. [Fix Verification Summary](#1-fix-verification-summary)
2. [Resolved Issues (28)](#2-resolved-issues-28)
3. [Deferred by Design (6)](#3-deferred-by-design-6)
4. [Remaining Risks and Observations](#4-remaining-risks-and-observations)
5. [Summary Statistics](#5-summary-statistics)

---

## 1. Fix Verification Summary

All 34 issues from v4.0.0 were addressed. 28 were resolved through document edits. 6 were confirmed as safe to defer per the v4.0.0 triage. Every fix was independently verified against the source document.

| Document | Fixes Applied | Fixes Verified | Status |
|----------|--------------|----------------|--------|
| `architecture.md` | 11 | 11 PASS | All fixes verified |
| `benchmark_spec.md` | 9 | 9 PASS | All fixes verified |
| `scientific_validity_matrix.md` | 4 | 4 PASS | All fixes verified |
| `artifact_schema.md` | 4 | 4 PASS | All fixes verified |
| `master_plan.md` | 3 | 3 PASS | All fixes verified |

**No new issues were introduced by any fix.**

---

## 2. Resolved Issues (28)

### Category 1: Contradictions Across Documents

| Issue | Severity | Resolution |
|-------|----------|------------|
| **CR-01** Report generator evidence_type "metadata" | CRITICAL | Changed to `null` with note: "report generation is rendering, not scientific computation; no evidence label applies" (`architecture.md` Section 4.4.6) |
| **CR-02** Bond length threshold contradiction | HIGH | Collapsed to binary pass/fail for Phase 1. Soft Failure row replaced with "— (binary check in Phase 1)". Classification note added. (`benchmark_spec.md` Section 5) |
| **CR-03** Failure taxonomy location mismatch | MEDIUM | Cross-reference corrected in `artifact_schema.md` Section 2.6 and `benchmark_spec.md` Section 5 to point to `architecture.md` Section 4.8. Five failure categories explicitly listed. |
| **CR-04** StepResult evidence_type for non-scientific steps | MEDIUM | Made nullable: `evidence_type: string \| null`. Null value documented for input resolution and report generation steps. (`artifact_schema.md` Section 2.2) |
| **CR-05** Diagram 1 layer ordering misleading | LOW | Added note after Diagram 1: "This diagram shows logical layers and their dependency relationships, not execution order. For the actual step execution sequence, see Section 4.3." (`architecture.md` Section 3) |
| **CR-06** Coordination comparison scope deferral | MEDIUM | Removed from MVP scope. Added to Deferred list with rationale: "no benchmark metric evaluates it." Output contract field annotated with `# deferred to Phase 4`. (`architecture.md` Section 4.4.4) |
| **CR-07** Report step file ambiguity | LOW | Added clarification: "The step count in WorkflowResult.steps (7) exceeds the number of step files (6). This is by design — step 6 artifacts are stored under reports/, not steps/." (`architecture.md` Section 4.7) |

### Category 2: MVP Scope Overreach

| Issue | Severity | Resolution |
|-------|----------|------------|
| **SC-01** Future tool contracts overspecified | MEDIUM | Replaced detailed contracts in Section 4.4.7 with one-sentence descriptions per tool. Added: "Detailed interface contracts will be specified during Phase 5–6 planning." (`architecture.md` Section 4.4.7) |

### Category 3: Scientific Overclaiming Risks

| Issue | Severity | Resolution |
|-------|----------|------------|
| **OC-01** "Reproduces" and "accurately" in benchmark spec | HIGH | Replaced "reproduce the structure accurately" with "produce a relaxed structure within defined threshold tolerances of the MP reference." All overclaiming verbs removed. (`benchmark_spec.md` Sections 3.1, 3.2, introduction) |
| **OC-02** No PBE+U systematic bias context in reports | HIGH | Added mandatory methodology caveat to report template: "PBE+U reference deviates from experimental values by approximately 1–3%." Added as formatting requirement #7. (`scientific_validity_matrix.md` Section 5) |
| **OC-03** Level A definition missing benchmark scope | MEDIUM | Added: "In Phase 1, 'benchmarked' refers to comparison against 3 known cathode materials (LiCoO2, LiFePO4, LiMn2O4)." (`scientific_validity_matrix.md` Section 2) |
| **OC-04** "Consistent" phrasing in assessment | LOW | Replaced with: "All lattice parameter deviations are within the defined 2% threshold, and volume deviation is within the 5% threshold." (`scientific_validity_matrix.md` Section 5) |

### Category 4: Vague Interfaces

| Issue | Severity | Resolution |
|-------|----------|------------|
| **VI-01** Formula disambiguation undefined | HIGH | Added 6-step algorithm: query → filter stable → select lowest energy_above_hull → raise on tie → log rationale. (`architecture.md` Section 4.1) |
| **VI-02** CanonicalMaterial factory undefined | HIGH | Added `create_canonical_material()` specification with complete field mapping (11 fields). Placed in `models/material.py`, called between steps 1 and 2. (`architecture.md` Section 4.2) |
| **VI-04** MP database version change policy | MEDIUM | Added reference data pinning policy: benchmark data exempt from TTL, version bump required for updates. (`benchmark_spec.md` Section 6) |
| **VI-05** WorkflowContext construction ambiguous | LOW | Added construction note: engine creates context with `normalized_query=None` before step 0; updates after step 0 completes. (`architecture.md` Section 4.3) |

### Category 5: Underspecified Benchmark Definitions

| Issue | Severity | Resolution |
|-------|----------|------------|
| **BD-01** Symmetry tolerance sensitivity | HIGH | Added two-tolerance protocol: `symprec=0.1 Å` (standard, determines classification) + `symprec=0.01 Å` (strict, informational diagnostic). Warning logged when results diverge. (`benchmark_spec.md` Section 5) |
| **BD-02** Category boundary noise | HIGH | Added boundary buffer: 0.2 percentage points around boundaries. Materials within buffer flagged as "boundary-proximate." Reproducibility assessed on flagged classification. (`benchmark_spec.md` Section 6) |
| **BD-03** MACE model size unspecified | MEDIUM | Fixed: "All Phase 1 benchmark runs use MACE-MP-0-medium." Variant change requires new benchmark run series. (`benchmark_spec.md` Section 6) |
| **BD-04** Reproducibility validation procedure | MEDIUM | Defined: 5 runs on reference machine, tolerance = `max(0.1%, 3 × observed_std_dev)`. Update tolerance if observed variance exceeds estimate. (`benchmark_spec.md` Section 6) |
| **BD-05** Convergence Partial/Soft boundary | LOW | Defined: Soft Failure = `fmax > threshold but < 2 × threshold` at step limit. Hard Failure = `fmax ≥ 2 × threshold` or divergence. (`benchmark_spec.md` Section 5) |

### Category 6: Missing Reporting Fields

| Issue | Severity | Resolution |
|-------|----------|------------|
| **RF-01** No units convention | MEDIUM | Added units convention table to `artifact_schema.md` Section 1: eV, eV/Å, Å, degrees, Å³, %, s, K. MAJOR version bump required for changes. |
| **RF-02** No cell convention field | MEDIUM | Added `cell_convention` field note to ToolResult section: `"primitive" \| "conventional"` included in comparator output. (`artifact_schema.md` Section 2.3) |

### Category 7: Agent Layer Too Central

| Issue | Severity | Resolution |
|-------|----------|------------|
| **AG-01** Diagram phase annotations | MEDIUM | Changed `[future]` to `[PHASE 5 — NOT BEFORE PHASE 4 GATE]` (agent) and `[PHASE 6]` (future tools) in Diagrams 1 and 3. (`architecture.md` Section 3) |
| **AG-02** Agent reference in Rule 5 | LOW | Moved to standalone paragraph: "Phase 5 note: When the Agent Layer is added, it must also respect family boundaries." (`architecture.md` Section 7, Rule 5) |

### Category 8: Missing Acceptance Criteria

| Issue | Severity | Resolution |
|-------|----------|------------|
| **AC-01** No evidence label validation test | HIGH | Added Phase 1 gate criterion: "Evidence labels in generated report match `scientific_validity_matrix.md` rules for each output type (automated integration test)." (`master_plan.md` Phase 1 gate) |
| **AC-02** No JSON/Markdown consistency test | HIGH | Added Phase 1 gate criterion: "JSON report and Markdown report are consistent (same sections, evidence labels, and numeric values)." (`master_plan.md` Phase 1 gate) |
| **AC-03** No MACE model loading validation | MEDIUM | Added Phase 1 gate criterion: "MACE-MP-0 checkpoint loads and completes a single-point energy calculation (pre-flight check before integration testing)." (`master_plan.md` Phase 1 gate) |

---

## 3. Deferred by Design (6)

These items were triaged as safe to defer in v4.0.0. They remain open and should be addressed at the indicated phase.

| Issue | Severity | Defer Until | Rationale |
|-------|----------|-------------|-----------|
| **SC-02** Trajectory storage unbounded | LOW | Phase 2 | Negligible for 3 materials; add `store_trajectory` config before scaling |
| **SC-03** Five registry interface definitions for one-entry registries | LOW | Phase 4 | Phase 1 note already mitigates over-engineering; verify interfaces against implementations before building |
| **VI-03** Cache key does not handle field subset queries | MEDIUM | Phase 4 | Negligible for 3 materials; consider full-field caching when scaling |
| **RF-03** No explicit optimizer identification in provenance | LOW | Phase 4 | `config_snapshot` captures the optimizer; dedicated field can be added when provenance queries become frequent |
| **AC-04** No cache TTL expiry and stale data handling tests | MEDIUM | Phase 1 | Add `test_mp_client_expired_cache_refetches()` and related tests during MP client implementation |
| **AC-05** No acceptance criterion for formula input beyond benchmark materials | LOW | Phase 1 | Add `test_invalid_formula_raises_input_error()` and related tests during input resolver implementation |

---

## 4. Remaining Risks and Observations

### No Critical or High Issues Remain

All CRITICAL (1) and HIGH (9) issues from v4.0.0 have been resolved. The remaining deferred items are MEDIUM (2) and LOW (4).

### Observations from Reassessment

1. **Cross-reference integrity**: All inter-document cross-references were verified. No broken links or mismatched section numbers detected after edits.

2. **No contradictions introduced**: The fixes are internally consistent. For example, `evidence_type: null` in the report generator (architecture.md) aligns with `string | null` in StepResult (artifact_schema.md).

3. **Scientific language audit**: No remaining instances of "reproduce", "reproduces", "accurately" (unqualified), "validated" (unqualified), "discovered", or "proved" in overclaiming contexts. The validity matrix wording rules are now consistently applied across `benchmark_spec.md`.

4. **Threshold table is now implementable**: All benchmark classification boundaries have quantitative definitions. No "borderline" or "near" qualifiers remain. The `classify_benchmark_status(metrics)` function can be implemented deterministically from the spec.

5. **Report template is defensible**: The mandatory PBE+U caveat, benchmark scope in Level A labels, and quantitative assessment language collectively address the thesis examiner concern. The evidence labels are honest about what "benchmarked" means (N=3).

6. **Diagram clarity**: Phase annotations prevent premature cognitive anchoring on the agent layer. The logical-vs-execution-order note prevents misinterpreting Diagram 1 as a pipeline.

### Low-Priority Items to Watch During Implementation

These are not issues per se, but areas to monitor as code is written:

- **Factory function integration**: The `create_canonical_material()` spec is clear, but the adapter between steps 1 and 2 must be tested to ensure all 11 fields are populated correctly. Missing fields will surface as pydantic validation errors.

- **Two-tolerance symmetry**: The strict check (0.01 Å) may fire frequently for MACE-relaxed structures. If every benchmark material triggers the tolerance-dependent warning, the warning loses diagnostic value. Monitor during first benchmark runs and adjust if needed.

- **Boundary buffer**: The 0.2 percentage point buffer is a reasonable starting estimate. If empirical variance (from BD-04 procedure) reveals that deviations cluster far from boundaries, the buffer may be unnecessary. If deviations cluster near boundaries, the buffer may need widening.

---

## 5. Summary Statistics

### v5.0.0 Issue Status

| Status | Count |
|--------|-------|
| Resolved | 28 |
| Deferred by design | 6 |
| New issues introduced | 0 |
| **Total from v4.0.0** | **34** |

### Severity Distribution of Resolved Issues

| Severity | Resolved | Deferred | Total |
|----------|----------|----------|-------|
| CRITICAL | 1 | 0 | 1 |
| HIGH | 9 | 0 | 9 |
| MEDIUM | 12 | 2 | 14 |
| LOW | 6 | 4 | 10 |
| **Total** | **28** | **6** | **34** |

### Review Progression

| Metric | v3.1.0 | v4.0.0 | v5.0.0 |
|--------|--------|--------|--------|
| Total issues | 43 | 34 | 6 (deferred only) |
| Critical | 2 | 1 | 0 |
| High | 12 | 9 | 0 |
| Medium | 19 | 14 | 2 |
| Low | 10 | 10 | 4 |
| Blocking implementation? | Yes | Yes | **No** |

### Documents Modified in This Fix Cycle

| Document | Edits | Key Changes |
|----------|-------|-------------|
| `architecture.md` | 11 | evidence_type null, disambiguation algorithm, factory function, diagram annotations, future tools simplified, WorkflowContext construction, coordination deferred, step file clarification |
| `benchmark_spec.md` | 9 | overclaiming language, bond length binary, convergence boundary, symmetry protocol, boundary buffer, reproducibility procedure, MACE variant, reference pinning, failure taxonomy cross-ref |
| `scientific_validity_matrix.md` | 4 | PBE+U caveat, Level A scope, assessment wording, formatting requirement |
| `artifact_schema.md` | 4 | units convention, nullable evidence_type, cell convention, failure taxonomy cross-ref |
| `master_plan.md` | 3 | evidence label test, JSON/MD consistency test, MACE pre-flight check |

---

## Conclusion

**The documentation suite is now internally consistent and ready for Phase 1 implementation.** All critical and high-severity issues have been resolved. The 6 remaining deferred items are low-risk and have clear resolution timelines (Phase 1 implementation or Phase 4).

The next consistency review should be conducted at the Phase 1 gate, focusing on:
1. Whether the deferred items (SC-02, SC-03, VI-03, RF-03, AC-04, AC-05) were addressed on schedule
2. Whether implementation revealed any new contradictions or underspecifications
3. Whether the empirical reproducibility procedure (BD-04) produced results consistent with the specified tolerances

---

*This review confirms that all v4.0.0 fixes were applied correctly and no regressions were introduced. The documentation is implementation-ready.*
