# CathodeScope Scientific Validity Matrix

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active — Thesis-Critical Document
**Cross-References**: `master_plan.md` (risk register, phase gates)

---

## 1. Purpose and Scope

This document is the single authoritative reference for what CathodeScope can and cannot claim about its outputs. It exists to prevent scientific overclaiming — the single greatest risk to thesis credibility.

### Why This Document Exists

CathodeScope is a **reproducible, benchmarked workflow system** that analyzes known cathode materials, runs atomistic workflows, compares results against established computational references, and produces disciplined, evidence-labeled reports. It does **not** claim full autonomous materials discovery, nor does it claim experimental validation of any computed property. Every output carries an explicit evidence level, and every claim in reports or thesis text must use wording consistent with this matrix.

### How to Use This Document

1. **Before writing ANY claim** about CathodeScope's outputs — in a report, in thesis text, in a presentation — consult this matrix.
2. **Find the relevant row** in Section 3 (the Validity Matrix) for the output or property in question.
3. **Use only the Allowed Wording** patterns. If the wording you want to use resembles anything in the Disallowed Wording column, stop and reformulate.
4. **Include the evidence level label** inline in the report, as demonstrated in Section 5.
5. **Cross-reference** the `master_plan.md` risk register for operational risks that interact with scientific validity (e.g., API failures, model version changes, data provenance gaps).

### Scope Boundaries

- This matrix covers all outputs that CathodeScope produces or will produce through Phase 6.
- It does NOT cover outputs from external tools used independently of CathodeScope workflows.
- It does NOT replace peer review or experimental validation — it defines the ceiling of what computational workflows can claim.

---

## 2. Evidence Level Definitions

CathodeScope assigns one of four evidence levels to every output. These levels are non-negotiable labels that travel with the data from computation through to the final report.

### Level A — Benchmarked

Outputs produced by benchmarked MVP workflows or retrieved from established reference sources. These can be stated directly in the thesis without additional caveats beyond identifying the method and source.

**Characteristics:**
- Produced by a workflow that has passed benchmark comparison against known reference materials
- Structural analysis outputs where MACE-relaxed results are within documented tolerance of Materials Project references
- Retrieved data from established reference sources (Materials Project) with documented provenance
- Reproducible: re-running the workflow on the same input produces the same output within numerical tolerance

**Sub-categories:**
- **A-retrieved**: Data retrieved from an established reference source (e.g., Materials Project crystal structure)
- **A-computed**: Data computed by a benchmarked CathodeScope workflow (e.g., MACE-relaxed structure)
- **A-compared**: Data produced by comparing computed results against references (e.g., lattice parameter deviation)

### Level B — Restricted Estimates

Outputs from workflows that produce quantitative estimates with known limitations. These must always include caveats and should be framed as screening estimates, never as definitive results.

**Characteristics:**
- The underlying method has known systematic biases or limited accuracy for the property in question
- Results are useful for screening and ranking but not for quantitative prediction
- Caveats are inseparable from the result — dropping the caveats makes the result misleading
- Comparison against experimental or higher-fidelity computational references is recommended but may not be available for all materials

### Level C — Proxies

Screening signals from lightweight computations. These cannot be presented as definitive results. They must be labeled as proxies, and follow-up with higher-fidelity methods is always recommended.

**Characteristics:**
- The computation provides directional information (e.g., "likely stable" vs. "likely unstable") but not quantitative reliability
- The method captures only a subset of the physics relevant to the property
- False positives and false negatives are expected at non-trivial rates
- Results are useful only as part of a multi-property screening workflow, not in isolation

### Level D — Disallowed

Claims that CathodeScope's methods cannot support. These must **never** appear in reports, thesis text, or any CathodeScope output.

**Characteristics:**
- Claims of experimental validation without experimental data
- Claims of discovery for known materials
- Claims of proof from computational evidence
- Claims of accuracy without specifying the reference
- Any claim that exceeds the evidence level of the constituent data

### Decision Flowchart

Use this flowchart to assign an evidence level to any CathodeScope output:

```
Is the value retrieved from an established reference source?
  YES --> Level A (retrieved)
  NO  --> Is it computed by a benchmarked CathodeScope workflow?
    YES --> Is the workflow part of the MVP benchmark core?
      YES --> Is the material from a benchmarked cathode family?
        YES --> Level A (computed)
        NO  --> Level B (restricted estimate, pending benchmark coverage)
      NO  --> Is it a restricted estimate with known caveats?
        YES --> Level B (restricted estimate)
        NO  --> Level C (proxy/screening signal)
    NO  --> Not a CathodeScope output (do not report)
```

When multiple evidence levels contribute to a single summary or recommendation, the summary **inherits the weakest constituent level**. A summary combining Level A and Level B data is labeled Level B. A summary including any Level C data is labeled Level C.

---

## 3. The Validity Matrix

### Part A: Overview Table

This condensed table provides a quick reference. For full specifications including allowed/disallowed wording, failure modes, and validation sources, see Part B below.

| # | Output / Property | Evidence Type | MVP Status | Confidence Label |
|---|---|---|---|---|
| 1 | Crystal Structure (Retrieved from MP) | A-retrieved | In MVP | MP-retrieved (Level A) |
| 2 | Normalized Crystal Structure | A-computed | In MVP | Normalized (Level A) |
| 3 | Relaxed Crystal Structure (MACE) | A-computed (benchmarked family) / B-restricted (other) | In MVP | MACE-relaxed (Level A if benchmarked family; Level B otherwise) |
| 4 | Relaxed Lattice Parameters | A-computed (benchmarked family) / B-restricted (other) | In MVP | MACE-computed (Level A if benchmarked family; Level B otherwise) |
| 5 | Relaxation Convergence Metadata | A-computed | In MVP | Convergence metadata (Level A) |
| 6 | Lattice Parameter Deviation from Reference | A-compared | In MVP | Reference comparison (Level A) |
| 7 | Bond Length and Coordination Comparison | A-compared | In MVP | Structural comparison (Level A) |
| 8 | Structural Symmetry Preservation | A-compared | In MVP | Symmetry check (Level A) |
| 9 | Average Voltage Estimate | B-restricted | Deferred to Phase 6 | Voltage screening estimate (Level B) |
| 10 | Thermodynamic Stability Proxy (Energy Above Hull) | C-proxy | Deferred | Stability proxy (Level C) |
| 11 | Li-ion Migration Barrier Estimate | C-proxy | Deferred | Transport proxy (Level C) |
| 12 | Dynamical Stability Proxy | C-proxy | Deferred | Dynamical proxy (Level C) |
| 13 | Ranking Recommendation | B-restricted / C-proxy | Deferred | Screening ranking (Level B/C) |
| 14 | Final Recommendation Summary | Inherits weakest | In MVP (Level A only) | Summary (inherits weakest) |

---

### Part B: Detailed Specifications

Each row below provides the complete nine-column specification for one CathodeScope output. These are the authoritative definitions.

---

#### Row 1: Crystal Structure (Retrieved from Materials Project)

| Field | Specification |
|---|---|
| **Evidence Type** | A-retrieved |
| **Typical Workflow** | `structural_analysis` --> `fetch` step |
| **Allowed Wording** | "Crystal structure retrieved from Materials Project (mp-XXXXX) computed using PBE+U methodology" |
| **Disallowed Wording** | "Experimental crystal structure", "Ground-truth structure", "Verified crystal structure" |
| **Validation Source** | Materials Project database with documented DFT methodology |
| **Failure Modes** | MP ID not found; API timeout; deprecated/updated entry; structure has warnings in MP; MP API version change breaks response format |
| **Confidence Label** | MP-retrieved (Level A) |
| **MVP Status** | In MVP |
| **Notes** | The Materials Project computes structures using DFT (PBE+U). These are computational references, not experimental measurements. Always cite the MP ID and the MP methodology version. Check the `is_stable` and `warnings` fields in the MP response. |

---

#### Row 2: Normalized Crystal Structure

| Field | Specification |
|---|---|
| **Evidence Type** | A-computed |
| **Typical Workflow** | `structural_analysis` --> `normalize` step |
| **Allowed Wording** | "Structure normalized to conventional standard setting using pymatgen" |
| **Disallowed Wording** | "Optimized structure", "Corrected structure" |
| **Validation Source** | Comparison of space group and Wyckoff positions before and after normalization |
| **Failure Modes** | Normalization changes space group unexpectedly; atom count mismatch between input and output; invalid structure output (overlapping atoms, unphysical cell parameters) |
| **Confidence Label** | Normalized (Level A) |
| **MVP Status** | In MVP |
| **Notes** | Normalization is a deterministic geometric transformation, not a physical optimization. It standardizes the unit cell representation but does not change the physics. If the space group changes, this indicates a problem with the input structure or the tolerance setting, not a discovery. |

---

#### Row 3: Relaxed Crystal Structure (MACE)

| Field | Specification |
|---|---|
| **Evidence Type** | A-computed |
| **Typical Workflow** | `structural_analysis` --> `relax` step |
| **Allowed Wording** | "Structure relaxed using MACE-MP-0 with convergence threshold fmax = X eV/Angstrom" |
| **Disallowed Wording** | "DFT-relaxed structure", "Experimentally validated structure", "Ground-state structure", "Optimized structure" (without specifying the method) |
| **Validation Source** | Compare relaxed lattice parameters against MP reference; deviation should be < 2% |
| **Failure Modes** | Non-convergence (fmax not reached within max steps); symmetry breaking (space group changes during relaxation); structural collapse (atoms overlap, unphysical bond lengths < 1.0 Angstrom); volume change > 10% from initial structure |
| **Confidence Label** | MACE-relaxed (Level A) |
| **MVP Status** | In MVP |
| **Notes** | MACE-MP-0 is a machine-learned interatomic potential trained on Materials Project DFT data. It reproduces PBE+U energetics for many systems but has known limitations for strongly correlated materials, surfaces, and compositions outside its training distribution. Always report the MACE model version and the convergence parameters. **Conditional trust note:** Level A is conditional on the material belonging to a benchmarked cathode family (layered oxide, olivine, spinel). Materials outside benchmarked families should be treated as Level B until benchmark coverage is extended to include them. |

---

#### Row 4: Relaxed Lattice Parameters

| Field | Specification |
|---|---|
| **Evidence Type** | A-computed |
| **Typical Workflow** | `structural_analysis` --> `relax` step (extracted from relaxed structure) |
| **Allowed Wording** | "Lattice parameters from MACE-MP-0 relaxation: a = X Angstrom, b = Y Angstrom, c = Z Angstrom" |
| **Disallowed Wording** | "Predicted lattice parameters", "Experimental lattice parameters" |
| **Validation Source** | Compare against MP reference lattice parameters; deviation < 2% per parameter |
| **Failure Modes** | Same as Row 3 (relaxation failures propagate to extracted parameters); additionally, confusion between primitive and conventional cell parameters |
| **Confidence Label** | MACE-computed (Level A) |
| **MVP Status** | In MVP |
| **Notes** | Lattice parameters are derived quantities from the relaxed structure. They inherit all failure modes of the relaxation itself. Always report whether values correspond to the primitive or conventional cell. **Conditional trust note:** Same as Row 3 — Level A is conditional on the material belonging to a benchmarked cathode family (layered oxide, olivine, spinel). Materials outside benchmarked families receive Level B until benchmark coverage is extended. |

---

#### Row 5: Relaxation Convergence Metadata

| Field | Specification |
|---|---|
| **Evidence Type** | A-computed |
| **Typical Workflow** | `structural_analysis` --> `relax` step (metadata) |
| **Allowed Wording** | "Relaxation converged in N steps with final fmax = X eV/Angstrom" |
| **Disallowed Wording** | "Optimization successful" (without convergence details) |
| **Validation Source** | fmax below threshold; energy monotonically decreased (or oscillated within tolerance) |
| **Failure Modes** | Max iterations reached without convergence; oscillating energy suggesting the optimizer is stuck in a basin; negative frequencies in post-relaxation check suggesting a saddle point rather than a minimum |
| **Confidence Label** | Convergence metadata (Level A) |
| **MVP Status** | In MVP |
| **Notes** | Convergence metadata is as important as the relaxed structure itself. A relaxation that reached max iterations is not converged, even if the final fmax is low-ish. Always report the number of steps, the final fmax, and whether convergence was achieved. Non-converged results must be flagged prominently. |

---

#### Row 6: Lattice Parameter Deviation from Reference

| Field | Specification |
|---|---|
| **Evidence Type** | A-compared |
| **Typical Workflow** | `structural_analysis` --> `compare` step |
| **Allowed Wording** | "Lattice parameter a deviates by X% from MP reference value (mp-XXXXX)" |
| **Disallowed Wording** | "Error in lattice parameter" (implies the reference is exact truth), "Lattice parameter matches experiment" |
| **Validation Source** | MP-computed reference values with documented methodology |
| **Failure Modes** | Wrong MP reference used (e.g., different polymorph); reference structure has been updated since retrieval; comparison uses wrong convention (primitive vs conventional cell); percentage deviation computed incorrectly (wrong denominator) |
| **Confidence Label** | Reference comparison (Level A) |
| **MVP Status** | In MVP |
| **Notes** | The word "deviation" is deliberate and preferred over "error". "Error" implies the reference is ground truth, but the MP reference is itself a DFT computation. The deviation is between two computational methods (MACE and PBE+U), not between computation and experiment. |

---

#### Row 7: Bond Length and Coordination Comparison

| Field | Specification |
|---|---|
| **Evidence Type** | A-compared |
| **Typical Workflow** | `structural_analysis` --> `compare` step (structural analysis) |
| **Allowed Wording** | "Average M-O bond length is X Angstrom (MP reference: Y Angstrom, deviation Z%)" |
| **Disallowed Wording** | "Correct bond lengths", "Bond lengths validated" |
| **Validation Source** | Bond lengths from MP reference structure; coordination numbers from crystal chemistry expectations |
| **Failure Modes** | Cutoff radius too large/small for neighbor detection; mixed oxidation states confuse bond analysis; disordered sites in the reference structure lead to ambiguous bond lengths; different site labeling between relaxed and reference structures |
| **Confidence Label** | Structural comparison (Level A) |
| **MVP Status** | In MVP |
| **Notes** | Bond length analysis depends on the neighbor-finding cutoff radius. Always report the cutoff used. Coordination numbers should be consistent with known crystal chemistry for the structure type (e.g., octahedral Co in layered LiCoO2 should have coordination number 6). **Phase 1 note:** Phase 1 uses global min/max bond length bounds (1.0–4.0 Å) as sanity checks, not per-element expected ranges. Per-family expected bond length ranges will be added in Phase 4. |

---

#### Row 8: Structural Symmetry Preservation

| Field | Specification |
|---|---|
| **Evidence Type** | A-compared |
| **Typical Workflow** | `structural_analysis` --> `validate` step |
| **Allowed Wording** | "Space group R-3m preserved after relaxation (symmetry tolerance = X Angstrom)" |
| **Disallowed Wording** | "Structure is correct", "Symmetry proved" |
| **Validation Source** | Space group analysis of relaxed structure using pymatgen with specified tolerance |
| **Failure Modes** | Symmetry broken to subgroup (may be physical or numerical artifact); tolerance-dependent results (different tolerances yield different space groups); pymatgen version differences in symmetry detection |
| **Confidence Label** | Symmetry check (Level A) |
| **MVP Status** | In MVP |
| **Notes** | Symmetry preservation is a necessary but not sufficient condition for a good relaxation. A relaxation that preserves symmetry but produces lattice parameters deviating > 2% from reference is still suspect. Always report the symmetry tolerance used, as results can be sensitive to this parameter. |

---

#### Row 9: Average Voltage Estimate

| Field | Specification |
|---|---|
| **Evidence Type** | B-restricted |
| **Typical Workflow** | `voltage_estimate` (future Phase 6 workflow) |
| **Allowed Wording** | "Screening estimate of average intercalation voltage based on MACE-computed energy difference between lithiated and delithiated structures" |
| **Disallowed Wording** | "Computed voltage", "Predicted operating voltage", "Electrochemical voltage" |
| **Validation Source** | Compare against experimental voltage from literature and MP-computed voltage |
| **Failure Modes** | Incorrect oxidation state assignment; delithiated structure unstable or collapses during relaxation; MACE energy error > 0.1 eV/atom accumulates in energy difference; phase transformations not captured (voltage profile assumes topotactic intercalation); entropic contributions neglected; voltage profile shape (plateau vs slope) not resolved by two-endpoint calculation |
| **Confidence Label** | Voltage screening estimate (Level B — requires deeper validation) |
| **MVP Status** | Deferred to Phase 6 |
| **Notes** | Average voltage is computed as V = -(E_lithiated - E_delithiated - n * E_Li_metal) / (n * e), where n is the number of Li atoms and e is the electron charge. This is a screening estimate because: (1) MACE energies have non-trivial errors that compound in energy differences, (2) the calculation assumes a single-phase reaction path, and (3) finite-temperature and kinetic effects are neglected. |

---

#### Row 10: Thermodynamic Stability Proxy (Energy Above Hull)

| Field | Specification |
|---|---|
| **Evidence Type** | C-proxy |
| **Typical Workflow** | `stability_proxy` (future workflow) |
| **Allowed Wording** | "Energy-above-hull proxy from MP phase diagram data suggests [stable/marginal/unstable] with E_hull = X eV/atom" |
| **Disallowed Wording** | "Thermodynamically stable", "Proved stability", "Stable material" |
| **Validation Source** | MP phase diagram data (which itself uses specific GGA+U methodology) |
| **Failure Modes** | Phase diagram incomplete (missing competing phases); GGA+U errors in energy differences between chemically dissimilar phases; novel compositions not in MP phase diagram; mixing GGA and GGA+U energies without correction; temperature-dependent stability not captured |
| **Confidence Label** | Stability proxy (Level C — screening signal only) |
| **MVP Status** | Deferred |
| **Notes** | Energy above hull from the MP phase diagram is itself a DFT-computed quantity with known limitations. For cathode materials, the relevant competing phases may include many polymorphs and decomposition products. A material with E_hull = 0 in the MP phase diagram is predicted stable by GGA+U, but this does not guarantee experimental synthesizability. This is a screening signal: useful for filtering obviously unstable candidates, not for confirming stability. |

---

#### Row 11: Li-ion Migration Barrier Estimate

| Field | Specification |
|---|---|
| **Evidence Type** | C-proxy |
| **Typical Workflow** | `transport_proxy` (future workflow) |
| **Allowed Wording** | "Lightweight migration barrier proxy of X eV from [method]. This is a screening signal, not a rigorous migration barrier calculation" |
| **Disallowed Wording** | "Migration barrier", "Diffusion barrier", "Validated transport property", "Ion conductivity" |
| **Validation Source** | Compare against NEB-computed barriers from literature where available |
| **Failure Modes** | Minimum-energy path not found; saddle point not converged; method not appropriate for the diffusion mechanism (e.g., concerted migration not captured by single-ion NEB); supercell too small to avoid periodic image interactions; MACE potential not accurate for transition state geometries (far from training data) |
| **Confidence Label** | Transport proxy (Level C — follow-up recommended) |
| **MVP Status** | Deferred |
| **Notes** | Li-ion transport is one of the most difficult properties to compute accurately. Even rigorous NEB calculations with DFT have significant uncertainty. A lightweight proxy (e.g., geometric analysis of diffusion channels, or a few-image MACE-NEB) provides only a rough screening signal. Results should be used to identify obviously blocked or obviously open diffusion pathways, not to quantify diffusivity. |

---

#### Row 12: Dynamical Stability Proxy

| Field | Specification |
|---|---|
| **Evidence Type** | C-proxy |
| **Typical Workflow** | `dynamics_proxy` (future workflow) |
| **Allowed Wording** | "Gamma-point phonon check shows [no imaginary frequencies / imaginary frequencies present]. This is a screening proxy, not a complete phonon stability analysis" |
| **Disallowed Wording** | "Dynamically stable", "Phonon-stable", "Proved dynamical stability" |
| **Validation Source** | Compare against full phonon dispersion calculations from literature where available |
| **Failure Modes** | Gamma-point check misses instabilities at other q-points (notably zone-boundary instabilities common in perovskites and other tilt systems); supercell too small for accurate force constants; numerical noise creates spurious imaginary modes (especially for low-frequency modes < 1 THz); MACE force accuracy insufficient for phonon calculations |
| **Confidence Label** | Dynamical proxy (Level C — screening signal only) |
| **MVP Status** | Deferred |
| **Notes** | A gamma-point phonon check tests only a single point in the Brillouin zone. Many known instabilities (e.g., antiferrodistortive tilts in perovskites, charge-density-wave instabilities) manifest at zone boundaries, not at gamma. A clean gamma-point check is necessary but far from sufficient for dynamical stability. This proxy is useful for catching gross instabilities (e.g., a structure that wants to collapse) but cannot confirm stability. |

---

#### Row 13: Ranking Recommendation

| Field | Specification |
|---|---|
| **Evidence Type** | B-restricted (when based on Level A and Level B data) or C-proxy (when including Level C inputs) |
| **Typical Workflow** | `ranking` (future workflow) |
| **Allowed Wording** | "Ranked by [specific metric] within the [family] family. Ranking is a screening tool, not a definitive assessment" |
| **Disallowed Wording** | "Best cathode material", "Optimal candidate", "Superior material" |
| **Validation Source** | Consistency with known literature rankings for benchmark materials |
| **Failure Modes** | Ranking based on single metric (misleading for multi-objective optimization); mixing evidence levels without disclosure; ranking order sensitive to small numerical differences within noise margin; missing important properties not included in ranking criteria (e.g., ranking by voltage without considering stability) |
| **Confidence Label** | Screening ranking (Level B/C — context-dependent) |
| **MVP Status** | Deferred |
| **Notes** | Rankings inherit the weakest evidence level of their inputs. A ranking that combines Level A structural data with Level C stability proxies is a Level C ranking overall. Rankings must always disclose: (1) which metrics were used, (2) the evidence level of each metric, (3) the material family or comparison set, and (4) the sensitivity of the ranking to small changes in input values. |

---

#### Row 14: Final Recommendation Summary

| Field | Specification |
|---|---|
| **Evidence Type** | Depends on constituent evidence levels (inherits the weakest level) |
| **Typical Workflow** | `report_generation` --> summary section |
| **Allowed Wording** | "Based on Level A structural analysis and Level B voltage screening, this material warrants further investigation" or "Based on Level A analysis only, [specific factual statement about structural comparison]" |
| **Disallowed Wording** | "CathodeScope recommends this material", "This material is suitable for battery applications", "Validated candidate" |
| **Validation Source** | All constituent analyses must be individually validated per their respective rows in this matrix |
| **Failure Modes** | Summary overclaims relative to constituent evidence; mixes evidence levels without disclosure; implies certainty beyond the evidence; uses language that suggests experimental validation; omits caveats from Level B or Level C constituents |
| **Confidence Label** | Summary (inherits weakest constituent level) |
| **MVP Status** | In MVP (for Level A summaries only) |
| **Notes** | The final summary is the most dangerous place for overclaiming because it is the most-read section of any report. Every factual claim in the summary must be traceable to a specific row in this matrix. The summary must explicitly state which evidence levels contribute to its conclusions. For the MVP, summaries are restricted to Level A evidence only (structural analysis and reference comparison). |

---

## 4. Wording Rules

The following rules apply to **all** CathodeScope outputs — every report, every log message, every thesis statement, every presentation slide. These are not style suggestions; they are scientific discipline requirements.

### Rule 1: Always State the Method

| Instead of | Write |
|---|---|
| "relaxed structure" | "structure relaxed using MACE-MP-0 (v0.3.6)" |
| "computed energy" | "energy computed using MACE-MP-0" |
| "normalized structure" | "structure normalized using pymatgen SpacegroupAnalyzer" |

**Rationale**: The method determines the reliability and reproducibility of the result. Omitting it makes the result unverifiable.

### Rule 2: Always State the Reference

| Instead of | Write |
|---|---|
| "compared against reference" | "compared against Materials Project mp-22526 (PBE+U)" |
| "matches known values" | "within 2% of MP-computed values for mp-22526" |
| "literature value" | "experimental value from [Author, Year] measured by [technique]" |

**Rationale**: "Reference" is meaningless without specifying which reference. Different references (experimental, DFT-GGA, DFT-GGA+U, hybrid functional) can disagree by several percent.

### Rule 3: Always State Thresholds

| Instead of | Write |
|---|---|
| "close to reference" | "within 2% of reference" |
| "good agreement" | "deviation < 1.5% for all lattice parameters" |
| "converged" | "converged to fmax = 0.005 eV/Angstrom in 23 steps" |

**Rationale**: "Close" and "good" are subjective. Thresholds are objective and reproducible.

### Rule 4: Always State the Evidence Level

Every quantitative result must carry its Level label (A, B, C) in the report. This is not optional decoration — it is part of the result.

| Instead of | Write |
|---|---|
| "Lattice parameter a = 2.821 Angstrom" | "[Level A] Lattice parameter a = 2.821 Angstrom (MACE-MP-0)" |
| "Estimated voltage: 3.9 V" | "[Level B] Voltage screening estimate: 3.9 V (MACE energy difference, caveats apply)" |

### Rule 5: Never Use "Validated" Without Specification

| Disallowed | Acceptable alternative |
|---|---|
| "Validated structure" | "Structure with lattice parameters within 2% of MP reference" |
| "Validated workflow" | "Workflow benchmarked against 5 known layered cathode materials with all deviations < 2%" |
| "Validated results" | "Results compared against MP references for LiCoO2, LiNiO2, and LiMnO2" |

**Rationale**: "Validated" without context is a vacuous claim. Validation is always relative to a specific reference, a specific metric, and a specific threshold.

### Rule 6: Never Use "Discovered" for Known Materials

| Disallowed | Acceptable alternative |
|---|---|
| "CathodeScope discovered that LiCoO2..." | "CathodeScope's analysis of LiCoO2 shows..." |
| "Novel finding" (for known material properties) | "Computed value consistent with / deviating from literature" |

**Rationale**: CathodeScope analyzes known materials. Discovery implies novelty that is not present when computing known properties of known materials.

### Rule 7: Never Use "Proved" for Computational Results

| Disallowed | Acceptable alternative |
|---|---|
| "Proved stable" | "Stability proxy suggests [stable/unstable] (Level C)" |
| "Proves the method works" | "Benchmark results consistent with references within specified thresholds" |

**Rationale**: Computational results provide evidence, not proof. Proof is a mathematical concept; physical and computational sciences deal in evidence and confidence levels.

### Rule 8: Never Use "Accurate" Without a Reference

| Disallowed | Acceptable alternative |
|---|---|
| "Accurate lattice parameters" | "Lattice parameters within 1% of MP reference" |
| "Accurate model" | "Model reproduces MP lattice parameters to within 2% for tested materials" |

**Rationale**: Accuracy is relative to a reference. Without specifying the reference, the claim is meaningless.

### Rule 9: Never Drop Caveats from Level B or C Results

Caveats are **part of the result**, not footnotes that can be omitted for brevity.

| Disallowed | Required |
|---|---|
| "Average voltage: 3.9 V" | "Average voltage screening estimate: 3.9 V [Level B]. Based on MACE energy difference between lithiated and delithiated endpoints. Does not account for phase transformations or kinetic effects. Requires validation against experimental voltage." |
| "Material is stable" | "Energy-above-hull proxy suggests stability (E_hull = 0.0 eV/atom from MP phase diagram) [Level C]. This is a screening signal based on GGA+U energetics and does not guarantee experimental synthesizability." |

### Rule 10: Never Present Proxy Results Alongside Benchmarked Results Without Labeling

When a report contains both Level A and Level C results, the difference must be visually and textually obvious.

| Disallowed | Required |
|---|---|
| Listing lattice parameters and stability proxy in the same table without labels | Separate sections with clear headers: "Structural Analysis [Level A]" and "Stability Screening [Level C]" |
| "Results: a = 2.821 Angstrom, E_hull = 0.0 eV/atom" | "[Level A] a = 2.821 Angstrom (MACE-MP-0). [Level C] E_hull proxy = 0.0 eV/atom (MP phase diagram, screening signal only)." |

---

## 5. How Evidence Labels Appear in Reports

The following mock excerpt demonstrates the required format for inline evidence labels in CathodeScope reports. This is not a suggestion — it is the required report format.

```markdown
## Structural Analysis: LiCoO2

### Retrieved Reference Data [Level A -- retrieved]
Crystal structure retrieved from Materials Project (mp-22526), computed using
PBE+U methodology (U_Co = 3.32 eV).
- Space group: R-3m (#166)
- Lattice parameters: a = 2.836 Angstrom, c = 14.083 Angstrom

### MACE Relaxation Results [Level A -- computed]
Structure relaxed using MACE-MP-0 (v0.3.6).
- Convergence: fmax = 0.005 eV/Angstrom reached in 23 steps
- Relaxed lattice parameters: a = 2.821 Angstrom, c = 14.052 Angstrom

### Reference Comparison [Level A -- compared]
- Lattice parameter a: deviation 0.53% from MP reference
- Lattice parameter c: deviation 0.22% from MP reference
- Cell volume deviation: 1.28% from MP reference
- Space group R-3m preserved (symmetry tolerance 0.1 Angstrom)
- All M-O bond lengths within expected range (1.9-2.1 Angstrom)

**Assessment**: Structural analysis consistent within benchmark
thresholds (benchmarked against 3 known cathode materials: LiCoO2,
LiFePO4, LiMn2O4). All evidence labels are Level A.
```

### Key Formatting Requirements

1. **Section headers** must include the evidence level in brackets: `[Level X -- sub-type]`
2. **The method and version** must appear in every computational section (e.g., "MACE-MP-0 (v0.3.6)")
3. **The MP ID** must appear in every reference data section (e.g., "mp-22526")
4. **Convergence details** must appear for every relaxation (steps, final fmax, whether convergence was achieved)
5. **Deviations** must be reported as percentages with the reference explicitly named
6. **The assessment paragraph** must summarize the evidence levels present and whether thresholds were met

### Example: Mixed Evidence Levels

When a future report includes multiple evidence levels, the formatting must make the level boundaries unmistakable:

```markdown
## Screening Report: LiNi0.8Co0.1Mn0.1O2

### Structural Analysis [Level A]
(... Level A content as above ...)

**All structural results are Level A (benchmarked).**

---

### Voltage Screening [Level B -- restricted estimate]
> IMPORTANT: The following is a screening estimate with known limitations.
> It is not a computed voltage and should not be cited as such.

Average intercalation voltage screening estimate: 3.85 V
- Method: MACE-MP-0 energy difference between lithiated and delithiated endpoints
- Known limitations: does not capture phase transformations, entropic effects,
  or voltage profile shape
- Comparison: experimental average voltage ~3.8 V (Ref: [Author, Year])
- Assessment: screening estimate within 0.05 V of experimental value for
  this material, but this level of agreement is not guaranteed for other
  compositions

**This result is Level B (restricted estimate). Caveats above are
inseparable from the result.**

---

### Stability Screening [Level C -- proxy]
> WARNING: The following is a screening proxy only. It does not establish
> thermodynamic stability.

Energy-above-hull proxy: 0.0 eV/atom (from MP phase diagram, GGA+U)
- This suggests thermodynamic stability within GGA+U accuracy
- Phase diagram may be incomplete for this composition
- Does not account for temperature-dependent stability

**This result is Level C (proxy/screening signal). Follow-up with
higher-fidelity methods is recommended.**

---

### Summary [Level B -- inherits from voltage screening]
Based on Level A structural analysis (all deviations < 2%) and Level B
voltage screening (estimate within range of experimental value), this
material warrants further investigation with higher-fidelity methods.
The Level C stability proxy is noted but does not elevate the
recommendation confidence.

**Overall evidence level: Level B (limited by voltage screening estimate).**
**The stability proxy (Level C) is reported for completeness but does not
contribute to the recommendation.**
```

---

## 6. Matrix Maintenance Rules

This matrix is a living document. It must be kept current as CathodeScope evolves. The following rules govern its maintenance.

### Rule 6.1: New Workflow Requirement

When a new workflow is added (Phases 5-6), the corresponding row(s) **must** be added to this matrix **before** the workflow is considered complete. A workflow without a validity matrix entry is not deployable.

**Process:**
1. Draft the new row(s) with all nine columns populated
2. Review allowed and disallowed wording for consistency with existing rows
3. Identify failure modes specific to the new workflow
4. Define the validation source and acceptance thresholds
5. Assign the evidence level using the decision flowchart in Section 2
6. Add the row(s) to both Part A (overview table) and Part B (detailed specifications)
7. Update the version number and date at the top of this document

### Rule 6.2: Phase Gate Verification

Each phase gate (as defined in `master_plan.md`) must include a verification step confirming that this matrix is current. The phase gate checklist should include:

- [ ] All workflows delivered in this phase have corresponding matrix rows
- [ ] All matrix rows for this phase's workflows have been reviewed for accuracy
- [ ] No new outputs are being generated without matrix entries
- [ ] Wording in reports and tests is consistent with the matrix

### Rule 6.3: Evidence Level Changes

If a row's evidence type changes (e.g., a Level C proxy is upgraded to Level B due to improved methodology, or a Level B estimate is downgraded to Level C due to discovered limitations), the following must occur:

1. The old evidence level must be recorded in the Notes field with a date
2. The rationale for the change must be documented
3. All existing reports using the old evidence level must be flagged for review
4. The version number of this document must be incremented

### Rule 6.4: Version History

| Version | Date | Change Description |
|---|---|---|
| 1.0.0 | 2026-03-10 | Initial matrix with 14 rows covering MVP and deferred workflows |

### Rule 6.5: Cross-References

This document is referenced by and must be consistent with:

- `master_plan.md` — phase gates, risk register, milestone definitions
- Report generation templates — inline evidence labels must match this matrix
- Benchmark validation scripts — threshold values must match this matrix
- Thesis text — all claims must be traceable to rows in this matrix

---

*This document is the authoritative reference for scientific validity claims in CathodeScope. When in doubt, check the matrix. When the matrix is silent, do not claim.*
