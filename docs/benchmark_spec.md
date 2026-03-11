# CathodeScope Benchmark Specification

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active — Thesis-Critical Document
**Cross-References**: `master_plan.md` (benchmark philosophy), `architecture.md` (error handling), `artifact_schema.md` (BenchmarkRow, ErrorRecord), `scientific_validity_matrix.md` (evidence labels)

---

## 1. Benchmark Philosophy

Benchmarking known materials first is the foundation of trust.

Without benchmarks, CathodeScope is just a script — a collection of tools strung together with no evidence that the outputs mean anything. Benchmarks establish a documented, reproducible, and transparent record of the system's behavior against known materials. Every claim CathodeScope makes about a material is only as credible as the benchmark results that back the workflow that produced it.

The benchmark set must be **narrow and representative**, not aspirational. Three materials, chosen to span the structural diversity of commercial cathode families, are sufficient for the MVP. These are materials for which community-consensus reference data exists — structures, lattice parameters, space groups, voltages, and modeling behavior that have been studied extensively for decades. There is no ambiguity about what the "right answer" should look like for these materials.

The system is designed to be **extensible toward unknown-material benchmarks later**, but unknown-material screening is not thesis-core. The benchmark tests whether CathodeScope produces results consistent with Materials Project references within defined thresholds, with consistent evidence labeling and full reproducibility. Once that baseline is established, the platform can be extended to materials where the answers are not known in advance.

**Core principle**: if CathodeScope cannot produce results consistent with known references for known materials, nothing else it produces should be relied upon.

Cross-reference: `master_plan.md` benchmark philosophy section.

---

## 2. Cathode Families

CathodeScope's benchmark set spans the three major commercial cathode families. These families were selected because they represent the dominant crystal chemistries in Li-ion batteries, they are structurally diverse (covering 1D, 2D, and 3D Li diffusion), and they have extensive reference data in the literature and in the Materials Project database.

### 2.1 Layered Oxides

- **Crystal system**: Hexagonal
- **Space group**: R-3m (#166)
- **General formula**: LiMO2 (M = transition metal)
- **Structural characteristic**: Alternating Li layers and transition-metal-oxide (MO2) layers in a rock-salt-derived framework. The structure can be understood as a distorted rock salt where Li and M ions order into alternating (111) planes of the cubic rock-salt parent structure, producing a layered arrangement with the trigonal R-3m symmetry.
- **Li diffusion dimensionality**: 2D (within Li layers). Li ions hop between octahedral sites within the Li slab via tetrahedral intermediate sites. The MO2 slabs act as barriers to inter-layer diffusion.
- **Representative material**: LiCoO2
- **Why included in benchmark**: Most commercially important cathode family. Most extensively studied cathode chemistry in history. Provides the "hydrogen atom" test case — if CathodeScope cannot handle LiCoO2, it cannot handle anything. The layered R-3m structure is geometrically simple, the Co3+/Co4+ redox is well-characterized, and decades of DFT and experimental data provide unambiguous reference points.
- **Variants (not in MVP benchmark)**: NMC (LiNi_xMn_yCo_zO2), NCA (LiNi_xCo_yAl_zO2), LiNiO2

### 2.2 Olivines / Polyanion Cathodes

- **Crystal system**: Orthorhombic
- **Space group**: Pnma (#62)
- **General formula**: LiMPO4 (M = Fe, Mn, Co, Ni)
- **Structural characteristic**: Corner-sharing MO6 octahedra and PO4 tetrahedra form a robust three-dimensional framework. The strong P-O covalent bonds within the phosphate tetrahedra stabilize the oxygen framework, providing exceptional thermal and electrochemical stability. Li ions occupy the M1 site (octahedral) and form one-dimensional chains along the b-axis.
- **Li diffusion dimensionality**: 1D (channels along b-axis). Li ions migrate through a curved path between adjacent M1 sites along the [010] direction. The one-dimensional nature makes the material sensitive to channel-blocking defects.
- **Representative material**: LiFePO4
- **Why included**: Structurally very different from layered oxides (orthorhombic vs hexagonal, 1D vs 2D diffusion, polyanion framework vs simple oxide). Second most commercially important cathode family. Dominates the EV and grid storage markets. Extensive reference data available from both experiment and computation. The polyanion framework introduces chemical complexity (P-O bonds, mixed coordination environments) that tests whether the workflow handles more than simple binary oxides.
- **Variants (not in MVP)**: LiMnPO4, LiCoPO4, LiNiPO4

### 2.3 Spinels

- **Crystal system**: Cubic
- **Space group**: Fd-3m (#227)
- **General formula**: LiM2O4 (M = transition metal)
- **Structural characteristic**: 3D framework of edge-sharing MO6 octahedra. Li occupies tetrahedral 8a sites in the fully lithiated phase. The spinel framework provides an interconnected three-dimensional network of tetrahedral-octahedral-tetrahedral pathways for Li diffusion, giving the structure excellent rate capability. The cubic symmetry means all three crystallographic directions are equivalent.
- **Li diffusion dimensionality**: 3D. Li hops between tetrahedral 8a sites through intermediate octahedral 16c sites. The three-dimensional connectivity provides multiple equivalent diffusion pathways and makes the structure tolerant to point defects that would block 1D channels.
- **Representative material**: LiMn2O4
- **Why included**: Third major commercial cathode family. 3D diffusion is structurally distinct from 1D (olivine) and 2D (layered). The Mn chemistry introduces a genuine scientific challenge: Mn3+ is Jahn-Teller active (high-spin d4 electronic configuration), which can cause cooperative tetragonal distortion of the cubic structure upon deep discharge. Mn dissolution into the electrolyte is a known degradation mechanism. These real scientific complexities provide meaningful test cases for whether MACE captures subtle electronic-structure-driven phenomena.
- **Variants (not in MVP)**: LiNi0.5Mn1.5O4 (high-voltage spinel, ordered P4332 or disordered Fd-3m)

### Family Comparison Table

| Property | Layered Oxide | Olivine | Spinel |
|---|---|---|---|
| Space group | R-3m (#166) | Pnma (#62) | Fd-3m (#227) |
| Crystal system | Hexagonal | Orthorhombic | Cubic |
| Li diffusion | 2D (within Li layers) | 1D (b-axis channels) | 3D (tetrahedral network) |
| Representative | LiCoO2 | LiFePO4 | LiMn2O4 |
| Typical voltage | ~3.9 V vs Li/Li+ | ~3.4 V vs Li/Li+ | ~4.0 V vs Li/Li+ |
| Key strength | High energy density | Safety and stability | Rate capability |
| Key challenge | Thermal stability | Low energy density | Mn dissolution |
| Framework type | Simple oxide | Polyanion (PO4) | Simple oxide |
| Active redox | Co3+/Co4+ | Fe2+/Fe3+ | Mn3+/Mn4+ |
| Commercial status | Dominant in consumer electronics | Dominant in EVs and grid | Niche / declining |

---

## 3. Shortlisted Materials

The initial benchmark set consists of exactly three materials. Each material represents one cathode family. Together, they span the structural diversity of commercial cathode chemistry: hexagonal, orthorhombic, and cubic crystal systems; 2D, 1D, and 3D Li diffusion; simple oxides and polyanion frameworks; and three different transition-metal redox couples.

The values listed here are approximate for documentation purposes. The authoritative reference for deviation calculations is always the value retrieved at runtime from the Materials Project API.

### 3.1 LiCoO2

| Field | Value |
|---|---|
| Formula | LiCoO2 |
| Materials Project ID | mp-22526 |
| Space group | R-3m (#166) |
| Crystal system | Hexagonal |
| Family | Layered oxide |
| MP lattice parameters | a ~ 2.836 A, c ~ 14.083 A (approximate; authoritative values are fetched from MP at runtime via `mp_client`) |
| Experimental voltage | ~3.9 V vs Li/Li+ |
| Key reference | Mizushima et al. (1980) — original discovery of electrochemical Li deintercalation from LiCoO2 |

**Selection rationale:** The "hydrogen atom" of cathode science. LiCoO2 is the most-studied cathode material in history. It was the first commercialized Li-ion cathode (Sony, 1991) and remains the reference point against which all other cathode materials are compared. If CathodeScope cannot handle LiCoO2 — retrieve its structure, relax it, compare against references, and produce a schema-conformant, evidence-labeled report — the system is fundamentally broken. This material is the minimum viable test of pipeline correctness.

**Known modeling considerations:** Co3+/Co4+ oxidation states are well-captured by standard DFT with Hubbard U correction, and MACE-MP-0 (trained on Materials Project DFT data) is expected to produce a relaxed structure within defined threshold tolerances of the MP reference. The layered R-3m structure is geometrically simple: a single lattice parameter ratio (c/a) largely characterizes the structure quality. The hexagonal symmetry with only two independent lattice parameters (a and c) makes deviation analysis straightforward. No known pathological modeling issues for the ground-state structure.

---

### 3.2 LiFePO4

| Field | Value |
|---|---|
| Formula | LiFePO4 |
| Materials Project ID | mp-19017 |
| Space group | Pnma (#62) |
| Crystal system | Orthorhombic |
| Family | Olivine / polyanion |
| MP lattice parameters | a ~ 10.332 A, b ~ 6.008 A, c ~ 4.692 A (approximate; authoritative values are fetched from MP at runtime via `mp_client`) |
| Experimental voltage | ~3.4 V vs Li/Li+ |
| Key reference | Padhi et al. (1997) — original report of reversible Li extraction from LiFePO4 |

**Selection rationale:** Structurally very different from LiCoO2. The orthorhombic Pnma symmetry, polyanion (PO4) framework, and 1D Li diffusion channels test whether CathodeScope's workflow generalizes beyond hexagonal layered oxides. If the system handles both LiCoO2 and LiFePO4 correctly, it demonstrates structural generality across two fundamentally different crystal chemistries. LiFePO4 is commercially dominant in the EV and grid storage markets, ensuring abundant reference data for validation. The three independent lattice parameters (a, b, c) provide a more stringent structural test than the two-parameter hexagonal case.

**Known modeling considerations:** The polyanion framework (PO4 tetrahedra) adds chemical complexity beyond simple binary oxides. The P-O bonds are strongly covalent, and the accuracy of these bonds affects the overall structural relaxation. Fe2+/Fe3+ redox is well-characterized and should be accessible to MACE. The Pnma structure has more atoms in the conventional cell than R-3m LiCoO2 (28 atoms vs 12 atoms in the conventional cell), which tests the workflow's handling of larger unit cells. The strong P-O covalent bonds provide a local structural rigidity that should be well-captured by the MACE potential.

---

### 3.3 LiMn2O4

| Field | Value |
|---|---|
| Formula | LiMn2O4 |
| Materials Project ID | mp-18767 |
| Space group | Fd-3m (#227) |
| Crystal system | Cubic |
| Family | Spinel |
| MP lattice parameters | a ~ 8.245 A (cubic, a = b = c; approximate; authoritative values are fetched from MP at runtime via `mp_client`) |
| Experimental voltage | ~4.0 V vs Li/Li+ |
| Key reference | Thackeray et al. (1983) — original report of Li intercalation into the spinel Mn2O4 framework |

**Selection rationale:** Completes the structural diversity trifecta. The cubic Fd-3m spinel structure with 3D Li diffusion is fundamentally different from both the 2D layered oxide and the 1D olivine. More importantly, LiMn2O4 presents a genuine scientific challenge that the other two benchmark materials do not: Mn3+ is Jahn-Teller active (high-spin d4, one electron in the doubly degenerate eg orbital), which can cause cooperative tetragonal distortion of the cubic lattice upon lithiation beyond Li1Mn2O4 to Li2Mn2O4. In the benchmark composition (LiMn2O4), the mixed Mn3+/Mn4+ valence state creates a more complex electronic structure than the single-valence Co3+ in LiCoO2 or Fe2+ in LiFePO4. This tests whether MACE captures physics driven by electronic structure effects that are not purely geometric.

**Known modeling considerations:** The Jahn-Teller distortion of Mn3+ can manifest as subtle local distortions even in the nominally cubic phase. The mixed Mn3+/Mn4+ oxidation state (average Mn3.5+ in stoichiometric LiMn2O4) may challenge MACE accuracy, as charge ordering and Jahn-Teller effects are electronic-structure phenomena that ML potentials capture only indirectly through their training data. The cubic Fd-3m structure has 56 atoms in the conventional cell, making it the largest unit cell in the benchmark set. This is intentionally a harder test case than LiCoO2 — a partial success or soft failure on LiMn2O4 would still be a scientifically informative benchmark result.

---

### 3.4 Fourth Material (Placeholder)

To be added after pipeline stability is demonstrated on the first three materials. The fourth material is not part of the MVP benchmark and is not required for any phase gate through Phase 4.

**Candidates:**

- **LiNiO2**: Layered oxide variant notorious for modeling difficulty. Ni3+ is Jahn-Teller active (low-spin d7), and LiNiO2 exhibits Li/Ni site disorder (Ni migrating into the Li layer) that is difficult to capture with ground-state DFT or ML potentials. This would stress-test the pipeline against a material known to be problematic for computational methods.

- **LiMnPO4**: Olivine variant. Would test within-family generalization — can the workflow that handles LiFePO4 also handle a different olivine without code changes? LiMnPO4 has a higher voltage (~4.1 V) but is less studied than LiFePO4, so reference data is somewhat sparser.

- **LiNi1/3Mn1/3Co1/3O2 (NMC-111)**: Ternary layered oxide. Would test multi-metal handling — can the workflow handle a material with three transition metals on the same sublattice? NMC-111 also introduces site disorder considerations (Ni/Mn/Co distribution).

**Selection criterion:** The fourth material must add scientific challenge without requiring new code paths in the MVP workflow. It should use the same structural_analysis workflow, the same metric table, and the same reporting template. If handling the fourth material requires workflow modifications, those modifications indicate that the MVP workflow is insufficiently general, which is itself a valuable finding.

---

## 4. What Each Benchmark Run Records

Every benchmark run produces a structured record (see `artifact_schema.md`, BenchmarkRow) containing the metrics defined in the table below. No metric is optional. Metrics with a success criterion of "Informational" are recorded but not used to determine the pass/fail status of the benchmark.

| Metric | Type | Description | Success Criterion (Phase 1) |
|---|---|---|---|
| `input_resolution` | bool | Was the formula/ID correctly resolved to a CanonicalMaterial? | Must be `true` |
| `structure_retrieval` | bool | Was the MP structure successfully retrieved via the API? | Must be `true` |
| `structure_normalization` | bool | Was the structure correctly normalized to conventional standard setting? | Must be `true` |
| `space_group_input` | string | Space group of the input structure (before relaxation) | Informational |
| `relaxation_convergence` | bool | Did MACE relaxation converge within the configured maximum steps? | `fmax` < configured threshold |
| `relaxation_steps` | int | Number of relaxation iterations to reach convergence (or max_steps if not converged) | < `max_steps` configuration |
| `final_fmax` | float (eV/A) | Maximum force on any atom after relaxation | < 0.01 eV/A (default) |
| `final_energy` | float (eV) | Total energy of the relaxed structure (MACE potential energy) | Informational |
| `lattice_param_deviation_a` | float (%) | Percentage deviation of relaxed lattice parameter `a` from MP reference | < 2% |
| `lattice_param_deviation_b` | float (%) | Percentage deviation of relaxed lattice parameter `b` from MP reference | < 2% |
| `lattice_param_deviation_c` | float (%) | Percentage deviation of relaxed lattice parameter `c` from MP reference | < 2% |
| `volume_deviation` | float (%) | Percentage deviation of relaxed cell volume from MP reference volume | < 5% |
| `symmetry_preserved` | bool | Did the space group survive relaxation (same space group before and after)? | Should be `true` |
| `space_group_output` | string | Space group of the relaxed structure (after relaxation) | Informational |
| `min_bond_length` | float (A) | Shortest interatomic distance in the relaxed structure | > 1.0 A |
| `max_bond_length` | float (A) | Longest relevant metal-oxygen bond in the relaxed structure | < 4.0 A for M-O |
| `evidence_labeling_complete` | bool | Are all outputs in the report correctly evidence-labeled per the scientific validity matrix? | Must be `true` |
| `report_generated` | bool | Was the full report (both JSON and Markdown) produced without errors? | Must be `true` |
| `runtime_seconds` | float | Wall-clock time for the entire workflow from input resolution to report generation | Informational |
| `workflow_version` | string | Version string of the workflow used for this run | Informational |
| `angle_deviation_alpha` | float (degrees) | Absolute deviation of angle α from MP reference | < 1° for Full Success |
| `angle_deviation_beta` | float (degrees) | Absolute deviation of angle β from MP reference | < 1° for Full Success |
| `angle_deviation_gamma` | float (degrees) | Absolute deviation of angle γ from MP reference | < 1° for Full Success |
| `symprec_used` | float (Å) | Symmetry tolerance used for space group analysis | Informational |

**Note on metric count:** 24 metrics total are recorded per benchmark run (20 original + 3 angle deviations + `symprec_used`). All metrics are mandatory — no metric is optional. `runtime_seconds`, `workflow_version`, and `symprec_used` are informational and do not contribute to pass/fail classification.

**Notes on specific metrics:**

- **Lattice parameter deviations** are computed as `|relaxed - reference| / reference * 100`. The reference is the Materials Project computed value, not an experimental value. This is a comparison between two computational methods (MACE and PBE+U), not between computation and experiment.

- **Volume deviation** is not simply the sum of lattice parameter deviations. For non-cubic systems, angle changes also contribute to volume changes. Volume deviation is computed directly from the cell volumes.

- **Symmetry preservation** uses pymatgen's `SpacegroupAnalyzer` with the default symmetry tolerance (0.1 A). The tolerance used must be recorded in the provenance record. A symmetry break may be physical (the relaxation found a lower-symmetry minimum) or numerical (the tolerance is too tight for the numerical precision of the relaxation). Both cases are informative.

- **Bond length bounds** are sanity checks, not precision metrics. A minimum bond length below 1.0 A indicates atomic overlap (structural collapse). A maximum M-O bond length above 4.0 A indicates that the coordination environment has been disrupted. These are hard failures if violated.

- **Evidence labeling completeness** is verified by checking that every section of the generated report carries an evidence level label consistent with the scientific validity matrix. This is a structural check on the report, not a scientific check on the results.

Cross-reference: `artifact_schema.md` BenchmarkRow for the storage format, `scientific_validity_matrix.md` for evidence label definitions.

---

## 5. Success and Failure Categories

Every benchmark run is classified into exactly one of the following five categories. Classification is deterministic: given the metric values, the category is unambiguous. No run is left unclassified, and no result is silently discarded.

### Full Success

All metrics pass their success criteria. The report is generated without errors. All evidence labels are present and consistent with the scientific validity matrix. The relaxed structure preserves the input space group, all lattice parameter deviations are below 2%, volume deviation is below 5%, all bond lengths are within hard bounds (min > 1.0 A, max M-O < 4.0 A), and the workflow converged within the configured step limit.

This is the target outcome. A Full Success on a benchmark material means CathodeScope's structural analysis workflow produces results consistent with Materials Project references for that material.

### Partial Success

The workflow completed end-to-end — all steps executed, a report was generated, and all evidence labels are present. However, one or more metrics are outside ideal thresholds but within acceptable bounds. For example:

- Lattice parameter deviation > 2% but < 5%
- Volume deviation > 5% but < 10%
- Relaxation converged but required more steps than expected (> 0.8 * max_steps)
- Bond lengths are within hard bounds (1.0–4.0 A) (Phase 1 binary check — does not distinguish Full from Partial; per-family expected ranges deferred to Phase 4)

A Partial Success is still a valid scientific result. It means the MACE model is less accurate for this particular material or structure type, which is itself useful information. The result is stored, reported, and included in benchmarks. It is not treated as a failure of the system — it is a characterization of the model's accuracy.

### Soft Failure

The workflow completed but with warnings that require human review before the results should be relied upon for further analysis. Examples:

- Symmetry broken during relaxation (space group reduced to a subgroup, e.g., R-3m to C2/m)
- Borderline convergence: fmax at step limit > threshold but < 2 × threshold
- Bond lengths within hard bounds (> 1.0 A, < 4.0 A) (Phase 1 binary check — bond lengths do not contribute to Soft Failure classification; per-family expected ranges deferred to Phase 4)
- Evidence labeling incomplete or inconsistent in the generated report
- Relaxation oscillating (energy not monotonically decreasing) but eventually converging

Soft Failure results are stored in full and flagged for review. They may indicate a genuine limitation of the MACE model, a problem with the input structure, or a numerical issue with the relaxation parameters. Human judgment is required to interpret them.

### Hard Failure

The workflow could not complete. A step produced an unrecoverable error, and no final report was generated (or the report is incomplete). Examples:

- Relaxation diverged: atoms overlapping (bond lengths < 0.5 A), structure collapsed
- MACE produced NaN energies or forces
- Materials Project structure retrieval failed due to invalid MP ID or deprecated entry
- Structure normalization produced an invalid structure (zero volume, overlapping atoms)
- Total energy diverged to positive infinity during relaxation
- Cell volume changed by > 50% during relaxation (structural collapse or explosion)

Partial results up to the failure point are stored. The failure is classified according to the error taxonomy in `artifact_schema.md` (ErrorRecord) and recorded in the benchmark row. A Hard Failure on a benchmark material is a valuable result — it indicates a limitation of the model or method that must be understood and documented.

### Infrastructure Failure

A failure unrelated to the science. The workflow was unable to execute not because of a scientific problem but because of an environmental or system issue. Examples:

- Network timeout during Materials Project API call
- Disk full during artifact write
- Python dependency import error (missing or incompatible package)
- Out-of-memory during MACE calculation
- File permission error when writing to the artifacts directory
- API rate limit exceeded

Infrastructure Failures are retryable. They do not reflect on the scientific capability of the system. They are logged, classified as infrastructure failures, and the benchmark run can be retried once the infrastructure issue is resolved. Infrastructure Failures are tracked separately from scientific failures in benchmark statistics.

### Classification Rules

1. Every run must be classified into exactly one category. No run is left unclassified.
2. Every failure must be stored, never silently discarded. A Hard Failure is data, not an embarrassment.
3. Classification is determined by the worst metric outcome: if any single metric triggers a Hard Failure condition (e.g., NaN energy), the entire run is Hard Failure regardless of other metrics.
4. Infrastructure Failures take precedence: if the workflow could not execute due to infrastructure issues, the run is Infrastructure Failure regardless of any partial scientific results.
5. Among scientific outcomes, the hierarchy is: Full Success > Partial Success > Soft Failure > Hard Failure. A single Soft Failure metric in an otherwise Full Success run makes the overall classification Soft Failure.

### Formal Threshold Table

The following table defines the quantitative boundaries for each result category. Classification is determined by the worst metric outcome across all columns.

| Metric | Full Success | Partial Success | Soft Failure | Hard Failure | Infrastructure Failure |
|---|---|---|---|---|---|
| Lattice param deviation (a, b, c) | < 2% | 2–5% | 5–10% | > 10% or NaN | N/A (run did not execute) |
| Volume deviation | < 5% | 5–10% | 10–20% | > 20% or NaN | N/A |
| Angle deviation (α, β, γ) | < 1° | 1–3° | > 3° | Structure collapsed | N/A |
| Symmetry | Preserved | Preserved | Broken to subgroup | Indeterminate / collapsed | N/A |
| Bond lengths (M-O) | Within 1.0–4.0 Å | Within 1.0–4.0 Å | — (binary check in Phase 1) | < 1.0 Å (overlap) or > 4.0 Å | N/A |
| Convergence | fmax < threshold within max_steps | Converged but steps > 0.8 * max_steps | fmax at step limit > threshold but < 2 × threshold | fmax at step limit ≥ 2 × threshold, or energy diverged (NaN/Inf/collapse) | N/A |
| Evidence labeling | All labels present and consistent | All labels present and consistent | Incomplete or inconsistent | Report not generated | N/A |
| Report generation | JSON + Markdown produced | JSON + Markdown produced | Produced with warnings | Not produced | N/A |

**Note on bond lengths:** Bond length classification is pass/fail in Phase 1 — Full Success and Partial Success share the same criterion (all within 1.0–4.0 Å). Per-family expected bond length ranges will be added in Phase 4.

**Bond length classification note (Phase 1):** Bond lengths are a binary pass/fail gate in Phase 1. Within 1.0–4.0 Å = pass (no impact on Full/Partial/Soft classification). Below 1.0 Å or above 4.0 Å = Hard Failure. Bond lengths do not contribute to Full/Partial/Soft distinction. Per-family expected bond length ranges will replace this binary check in Phase 4.

**Symmetry tolerance protocol (Phase 1):** Symmetry is checked at two tolerances: `symprec=0.1 Å` (standard) and `symprec=0.01 Å` (strict). The standard check determines the benchmark classification. The strict check is recorded as an informational diagnostic. If the standard check shows preservation but the strict check shows breaking, a warning is logged: 'Symmetry preservation is tolerance-dependent for this structure.' This warning does not affect classification but is included in the report.

**Reading this table:** A run is classified by its worst column. For example, if lattice deviation is < 2% (Full Success) but angle deviation is 2° (Partial Success), the overall classification is Partial Success. Infrastructure Failure takes precedence over all scientific outcomes — if the run could not execute due to network, disk, or dependency issues, no scientific classification applies.

**Relationship to WorkflowResult.status**: The `WorkflowResult.status` field reflects pipeline execution outcomes (step completion, crashes, warnings). The `BenchmarkRow.status` field is determined independently by applying the formal threshold table above to the recorded metrics. These two status values may differ — for example, a workflow may complete successfully (`WorkflowResult.status: success`) but produce lattice deviations exceeding 2%, resulting in `BenchmarkRow.status: partial_success`. The benchmark runner must apply `classify_benchmark_status(metrics)` independently of the workflow status.

**Failure taxonomy cross-reference:** The failure taxonomy (retrieval_failure, convergence_failure, validation_failure, artifact_failure, unknown_failure) is defined in `architecture.md` Section 4.8.

Cross-reference: `architecture.md` error handling strategy, `artifact_schema.md` ErrorRecord and WorkflowResult status enum.

---

## 6. Phase 1 Benchmark Criteria (MVP)

The MVP benchmark is intentionally minimal. Its purpose is to demonstrate that CathodeScope can run a single workflow against a small set of known materials and produce reproducible, evidence-labeled results consistent with known references. It is not a comprehensive evaluation of MACE accuracy or a survey of cathode chemistry.

### Scope

- **Materials**: 3 (LiCoO2, LiFePO4, LiMn2O4)
- **Workflow**: 1 (`structural_analysis`)
- **Metrics**: As defined in Section 4 (all metrics recorded; threshold-bearing metrics evaluated)

### Overall Success Criterion

At least **2 of 3 materials** achieve **Full Success**; the third achieves at least **Partial Success**.

This criterion acknowledges that LiMn2O4 (the spinel with Jahn-Teller active Mn3+) may be a harder case for MACE than LiCoO2 or LiFePO4. A Partial Success on LiMn2O4 with Full Success on the other two is a scientifically honest and acceptable MVP outcome. It demonstrates that the workflow works correctly and that the MACE model's accuracy varies by material — which is itself a valid scientific finding.

### Reproducibility Criterion

Re-running the benchmark produces the **same result category** for each material. Exact numerical values may differ at the floating-point level (due to non-determinism in numerical libraries, thread scheduling, etc.), but:

- A material that achieved Full Success must achieve Full Success on re-run
- A material that achieved Partial Success must achieve Partial Success on re-run
- Lattice parameter deviations must agree to within 0.1% between runs (this tolerance is a starting estimate pending empirical justification during Phase 1 implementation)
- The same space group must be reported before and after relaxation on every run

**Empirical validation procedure:** During Phase 1, run LiCoO2 relaxation 5 times on the reference machine with identical configuration. Compute the standard deviation of lattice parameter deviations across runs. Set the reproducibility tolerance to `max(0.1%, 3 × observed_std_dev)`. Document the observed variance and the resulting tolerance. If `observed_std_dev > 0.033%` (i.e., 3σ exceeds 0.1%), update the tolerance with empirical justification before the Phase 1 gate review.

If the reproducibility criterion fails, this indicates a non-determinism bug in the workflow or in the MACE implementation, which must be investigated before the benchmark can be considered passed.

**Boundary buffer policy:** When a metric value falls within 0.2 percentage points of a classification boundary (e.g., lattice deviation between 1.8% and 2.2% near the 2% Full/Partial boundary), the material is classified at the better category but flagged as 'boundary-proximate.' Reproducibility is assessed on the flagged classification, not the raw category. If the material is consistently boundary-proximate across runs (same flag), reproducibility is satisfied even if the raw metric oscillates across the boundary.

**MACE model variant (Phase 1):** All Phase 1 benchmark runs use MACE-MP-0-medium. The exact model variant, checkpoint hash, and compute device are recorded in provenance. Switching to a different MACE-MP-0 variant (small or large) constitutes a configuration change and requires a new benchmark run series.

**Reference data pinning:** Benchmark reference data is pinned at the first successful retrieval. All subsequent benchmark runs for the same material use cached data from the original retrieval. Cache TTL does not apply to benchmark reference data. If reference data must be updated (e.g., Materials Project corrects a known error), a new benchmark run series is created with a version bump and the reference change is documented in the decision log.

### Evidence Labeling Criterion

All outputs in all reports have expected evidence labels per the scientific validity matrix (`scientific_validity_matrix.md`). Specifically:

- Retrieved MP data is labeled `[Level A -- retrieved]`
- MACE-relaxed structures are labeled `[Level A -- computed]`
- Reference comparisons (lattice deviations, symmetry checks) are labeled `[Level A -- compared]`
- No output is unlabeled
- No output carries an evidence level higher than what the validity matrix permits
- The summary section inherits the weakest constituent evidence level

### What Phase 1 Does NOT Require

- **All 3 materials achieving Full Success.** Partial Success on 1 material is acceptable and scientifically informative.
- **Specific numerical accuracy targets beyond the threshold table.** The thresholds in Section 4 define pass/fail. There is no "extra credit" for achieving tighter deviations.
- **Performance benchmarks.** Runtime is recorded but not judged. A slow but threshold-conformant run passes; a fast but threshold-violating run fails.
- **Comparison against experimental data.** All comparisons are against Materials Project computed references. Experimental comparison is deferred to Phase 4+.
- **Voltage estimation.** Voltage benchmarking requires the delithiated structure workflow, which is not part of the MVP.
- **Stability assessment.** Neither thermodynamic nor dynamical stability is evaluated in Phase 1.

---

## 7. What Is Intentionally Excluded from the Benchmark (and Why)

Each exclusion below is a deliberate design decision, not an oversight. The rationale is documented so that future contributors understand why these items are absent and when they should be added.

### Experimental Reference Comparison

**Excluded.** Experimental lattice parameters vary with measurement conditions: temperature (thermal expansion), pressure (compressibility), sample quality (defect concentration, stoichiometry deviations), and measurement technique (X-ray vs neutron diffraction, single crystal vs powder). A single "experimental value" does not exist for most materials — instead, there is a range of reported values across the literature.

Materials Project computed values (PBE+U, 0 K, ideal stoichiometry) provide a **consistent, reproducible reference baseline**. Comparing MACE against MP-PBE+U is a well-defined computational benchmark: both methods operate on the same idealized system (0 K, no defects, no thermal effects), so deviations reflect differences between the methods, not differences between computation and reality.

Experimental comparison is a Phase 4+ enhancement. It will be added after the computational pipeline is stable, and it will require careful documentation of which experimental values are used, from which source, measured under what conditions, and with what reported uncertainties.

### Voltage Benchmarking

**Excluded.** Voltage estimation requires computing the energy difference between lithiated and delithiated structures:

V = -(E_lithiated - E_delithiated - n * E_Li_metal) / (n * e)

This requires: (1) a delithiated structure (e.g., CoO2 for LiCoO2), (2) relaxation of the delithiated structure, (3) a reference energy for Li metal, and (4) careful handling of the energy difference, which amplifies any per-atom errors in the MACE potential.

The delithiated structure workflow is not part of the MVP. Voltage benchmarking enters in Phase 6, after the structural analysis pipeline is proven stable and the delithiated structure workflow has been implemented and separately benchmarked.

### Stability Benchmarking (Thermodynamic)

**Excluded.** Thermodynamic stability assessment requires comparing the material's energy against all competing phases in the relevant composition space. This means constructing (or retrieving) the convex hull of the Li-Co-O (or Li-Fe-P-O, or Li-Mn-O) phase diagram and computing the energy above the hull.

This requires: (1) energies of all competing phases (potentially dozens of compounds), (2) consistent energy references across all phases (mixing DFT functionals or mixing MACE with DFT energies introduces systematic errors), and (3) phase diagram construction tools. These capabilities are beyond MVP scope and are labeled as proxy evidence (Level C) in the scientific validity matrix even when eventually implemented, because the underlying DFT phase diagrams have known limitations.

### Stability Benchmarking (Dynamical)

**Excluded.** Dynamical stability assessment requires phonon calculations — at minimum a gamma-point frequency check, ideally the full phonon dispersion across the Brillouin zone. Phonon calculations require: (1) accurate force constants from finite displacements or density-functional perturbation theory, (2) supercells large enough to converge the force constant matrix, and (3) post-processing to extract frequencies and check for imaginary modes.

These calculations are computationally expensive (the supercell requirement multiplies the system size), scientifically complex (interpreting imaginary modes requires domain expertise), and produce results that are at best Level C proxy evidence per the scientific validity matrix. A gamma-point check can miss zone-boundary instabilities. Full dispersion is expensive and may exceed MACE's force accuracy for the small displacements required.

### Timing/Performance Benchmarks

**Excluded as a success criterion.** Runtime is recorded in every benchmark run (`runtime_seconds` metric) but is NOT used to determine pass/fail. Correctness first, performance optimization later.

A slow but threshold-conformant run is better than a fast but threshold-violating one. Performance optimization is a Phase 7 activity (paper polish). During the MVP and thesis-core phases, the only performance requirement is that benchmark runs complete in a reasonable time for a development workflow (minutes, not hours, for a single material). This is not formalized as a threshold because hardware varies.

Informational timing target: single-material pipeline should complete in < 10 minutes wall-clock on the reference development machine (CPU-only). Exceeding this triggers performance investigation but does not constitute a benchmark failure.

### Multi-Configuration Benchmarking

**Excluded.** Only the ground-state structure from the Materials Project is used for each benchmark material. The following are all deferred:

- **Polymorphs**: Different crystal structures of the same composition (e.g., layered vs spinel LiMnO2). Would require polymorph enumeration and energy ranking.
- **Defect structures**: Vacancies, antisites, interstitials. Would require defect generation, supercell construction, and defect formation energy calculation.
- **Surface structures**: Surface slabs with various terminations and coverages. Would require slab generation and surface energy calculation.
- **Magnetic orderings**: Different spin configurations (ferromagnetic, antiferromagnetic, ferrimagnetic). Would require magnetic ordering enumeration and energy comparison.

Each of these would require additional workflow logic, additional reference data, and additional metrics. They are valuable extensions but are not MVP-scope.

### Statistical Uncertainty Quantification

**Excluded.** MACE does not natively provide prediction uncertainty (error bars on energies or forces). Quantifying the uncertainty of ML potential predictions is an active research area with approaches including:

- **Ensemble methods**: Training multiple MACE models and using the spread of predictions as an uncertainty estimate
- **Dropout-based uncertainty**: Not applicable to the MACE architecture
- **Calibration studies**: Comparing MACE predictions against DFT for a test set and deriving empirical error distributions

None of these are implemented in the MACE-MP-0 release used by CathodeScope. This is a known limitation, documented in the scientific validity matrix but not solved by the MVP. The benchmark thresholds in Section 4 serve as empirical accuracy bounds (e.g., < 2% lattice deviation) but are not formal uncertainty estimates.

### Cross-Model Comparison

**Excluded.** Comparing MACE against other ML interatomic potentials (e.g., M3GNet, CHGNet, SevenNet) or against direct DFT calculations (PBE+U, SCAN, hybrid functionals) would be valuable for a publication but is not required for the MVP benchmark.

The MVP benchmark establishes that CathodeScope produces results consistent with Materials Project references using MACE-MP-0. Cross-model comparison is a Phase 7 (paper polish) activity that would strengthen the publication but does not affect the thesis-core demonstration of the reproducible workflow platform. If performed, cross-model results would be presented as supplementary material showing where MACE-MP-0 sits relative to other methods, not as a core benchmark requirement.

---

## Cross-Reference Index

| Topic | Related Document |
|---|---|
| Benchmark philosophy and phase gates | `master_plan.md` |
| System architecture and error handling | `architecture.md` |
| BenchmarkRow, BenchmarkSummary, ErrorRecord schemas | `artifact_schema.md` |
| Evidence level definitions and validity ladder | `scientific_validity_matrix.md` |
| Allowed and disallowed wording for benchmark claims | `scientific_validity_matrix.md` Section 4 |
| Report formatting with evidence labels | `scientific_validity_matrix.md` Section 5 |
| WorkflowResult status enum and step results | `artifact_schema.md` Section 2.2 |
| Provenance tracking for benchmark runs | `artifact_schema.md` Section 2.5 |
| Directory layout for benchmark artifacts | `artifact_schema.md` Section 3 |

---

*This document defines what CathodeScope benchmarks, why it benchmarks those specific materials, what it measures, and how it classifies results. Every number in a benchmark report traces back to a metric in this specification. Every pass/fail judgment traces back to a threshold in this specification. When in doubt, consult the tables.*
