# Subject-Matter Expert Onboarding

**Audience:** Software engineers joining CathodeScope who do not yet have domain expertise in battery or materials science.

**Purpose:** Provide the conceptual grounding needed to make sound engineering decisions when building, testing, and extending CathodeScope workflows. This is a working reference, not a textbook.

**Last updated:** 2026-03-10

---

## Table of Contents

1. [What CathodeScope Is and Is Not](#1-what-cathodescope-is-and-is-not)
2. [Li-ion Battery Fundamentals for Engineers](#2-li-ion-battery-fundamentals-for-engineers)
3. [The Three Benchmark Cathode Families](#3-the-three-benchmark-cathode-families)
4. [Structure Relaxation: What It Means and Why It Matters](#4-structure-relaxation-what-it-means-and-why-it-matters)
5. [MACE: The Machine-Learning Interatomic Potential](#5-mace-the-machine-learning-interatomic-potential)
6. [Materials Project: The Reference Database](#6-materials-project-the-reference-database)
7. [The Validity Ladder: Level A Outputs vs. Estimates vs. Proxies](#7-the-validity-ladder-level-a-outputs-vs-estimates-vs-proxies)
8. [Common Scientific Pitfalls for Engineers](#8-common-scientific-pitfalls-for-engineers)
9. [Glossary](#9-glossary)

---

## 1. What CathodeScope Is and Is Not

CathodeScope is a reproducible scientific workflow platform for benchmarked Li-ion cathode screening, with agent orchestration layered on top of deterministic, benchmarked workflows. The thesis-core does **not** claim full autonomous materials discovery. Understanding the boundary between what the system does and what it does not do is essential for every contributor.

| CathodeScope **IS** | CathodeScope **IS NOT** |
|---|---|
| A reproducible scientific workflow platform for benchmarked cathode screening | An autonomous materials discovery engine |
| A system that compares computed structures against established computational reference data | A replacement for DFT or experimental validation |
| Extensible toward agent orchestration and advanced workflows | Making claims about unknown or hypothetical materials in its thesis-core |

**Key implications for engineers:**

- Every workflow output must trace back to a reference or a benchmarked computational step. If a result cannot be compared to an established reference source, it is not a thesis-core claim.
- Agent orchestration is a layer that coordinates benchmarked workflows. The agents do not invent new science; they sequence and parameterize deterministic steps.
- When in doubt about whether a feature crosses the boundary from "benchmarked screening" into "discovery claim," raise it. The validity ladder (Section 7) is the arbiter.

> **Cross-references:** `docs/architecture.md` (system design and workflow layering), `docs/master_plan.md` (phased roadmap and scope boundaries).

---

## 2. Li-ion Battery Fundamentals for Engineers

### What a lithium-ion battery is

A lithium-ion battery is an electrochemical cell with four essential components:

| Component | Role | Typical Materials |
|---|---|---|
| **Cathode** (positive electrode) | Hosts lithium ions; determines the cell's voltage and capacity | LiCoO2, LiFePO4, LiMn2O4, NMC, NCA |
| **Anode** (negative electrode) | Stores lithium during charge | Graphite, silicon, lithium metal |
| **Electrolyte** | Conducts Li+ ions between electrodes; must be electronically insulating | Organic liquid (e.g., LiPF6 in EC/DMC), solid-state alternatives |
| **Separator** | Physically prevents electrode contact while allowing ion transport | Porous polymer membrane (PE, PP) |

During **discharge**, lithium ions flow from the anode through the electrolyte to the cathode, while electrons flow through the external circuit (doing useful work). During **charge**, the process reverses under an applied voltage.

### Why the cathode matters

The cathode is the performance-limiting component in most commercial Li-ion cells. It determines:

- **Capacity** — how many lithium ions can be stored per unit mass
- **Voltage** — the electrochemical potential difference that drives the cell
- **Cost** — cathode materials (cobalt, nickel) dominate cell cost
- **Safety** — thermal stability of the cathode governs runaway risk

This is why CathodeScope focuses on cathode screening: improving cathode selection has the highest leverage on overall cell performance.

### The intercalation mechanism

Most cathode materials operate by **intercalation**: lithium ions reversibly insert into and extract from a host crystal lattice without destroying the crystal framework. Think of it as guests (Li+) checking into and out of a hotel (the crystal structure) — the hotel remains standing.

During charge, Li+ ions are extracted from the cathode lattice, travel through the electrolyte, and intercalate into the anode. During discharge, the reverse occurs. The structural integrity of the cathode during repeated cycling is critical for battery longevity.

### Key performance metrics

| Metric | Definition | Typical Range (cathodes) |
|---|---|---|
| **Theoretical capacity** (mAh/g) | Maximum charge stored per gram if all Li is extracted | 140--280 mAh/g |
| **Average voltage** (V vs. Li/Li+) | Mean electrochemical potential during discharge, measured against a Li metal reference | 2.5--4.5 V |
| **Energy density** (Wh/kg) | Capacity x voltage; the single most important figure of merit | 350--800 Wh/kg (material level) |
| **Cycle stability** | Capacity retained after N charge/discharge cycles | >80% after 500--2000 cycles |

### What "screening" means

Screening is the computational step before synthesis. The question is: *"Given a candidate cathode material, is it worth the time and money to synthesize it in the lab and test it electrochemically?"*

Screening does not prove a material works. It eliminates candidates that are unlikely to work, based on computed properties compared to known references. CathodeScope's MVP focuses on structural screening: does the relaxed structure of a candidate remain physically reasonable and consistent with its expected crystal family?

---

## 3. The Three Benchmark Cathode Families

CathodeScope's MVP validates workflows against three structurally distinct cathode families. These were chosen because they span the major commercial cathode types, have extensive reference data, and exercise different aspects of the computational pipeline (1D, 2D, and 3D lithium transport).

> **Cross-reference:** `docs/benchmark_spec.md` for material IDs, thresholds, and pass/fail criteria.

---

### 3.1 Layered Oxides

**Archetype:** LiCoO2 (lithium cobalt oxide)

**Crystal system:** Hexagonal | **Space group:** R-3m (#166)

**Structure:** Layered oxides derive from the rock-salt structure. Alternating layers of lithium ions and transition-metal oxide (MO2) slabs stack along the c-axis. The oxygen ions form a close-packed framework, with Li and the transition metal (Co, Ni, Mn) occupying octahedral sites in separate layers.

```
  ... O - M - O - Li - O - M - O - Li - O ...
       (MO2 slab)  (Li layer)  (MO2 slab)
```

**Li transport:** Two-dimensional diffusion within the lithium layers. Ions hop between octahedral sites through adjacent tetrahedral sites within each Li plane.

**Commercial relevance:** The dominant cathode chemistry in consumer electronics (smartphones, laptops, tablets). Variants include:
- **NMC** (LiNi_xMn_yCo_zO2) — tunable Ni:Mn:Co ratio to balance energy, stability, and cost
- **NCA** (LiNi_xCo_yAl_zO2) — high energy density, used in some EV applications

**Key properties:**
- High energy density (among the highest for commercial cathodes)
- Moderate thermal stability (less safe than olivines at high state of charge)
- Sensitive to Li/Ni site mixing (cation disorder), which degrades performance

**Why it is in the benchmark:** The most-studied cathode family in computational and experimental literature. Extensive reference data from Materials Project and thousands of published DFT studies make it the natural first validation target.

---

### 3.2 Olivines / Polyanion Cathodes

**Archetype:** LiFePO4 (lithium iron phosphate)

**Crystal system:** Orthorhombic | **Space group:** Pnma (#62)

**Structure:** The olivine framework consists of corner-sharing FeO6 octahedra and PO4 tetrahedra. The strong covalent P--O bonds within the phosphate groups stabilize the oxygen framework, which is a key reason olivines do not release oxygen under thermal abuse (unlike layered oxides). Li ions occupy chains of edge-sharing octahedral sites along the b-axis.

**Li transport:** One-dimensional channels along the b-axis. This restricts Li mobility to a single crystallographic direction, making olivine transport highly sensitive to channel-blocking defects.

**Commercial relevance:** The dominant cathode chemistry in electric vehicles (especially Chinese EV market) and grid-scale energy storage. Chosen for:
- Excellent thermal stability and safety
- Very long cycle life (>3000 cycles in commercial cells)
- Low cost (iron and phosphate are abundant)

**Key properties:**
- Lower energy density compared to layered oxides
- Flat voltage plateau at approximately 3.4 V vs. Li/Li+
- Outstanding structural stability during cycling

**Why it is in the benchmark:** Structurally very different from layered oxides (1D vs. 2D transport, polyanion framework vs. simple oxide), with extensive reference data. Tests whether the pipeline handles a fundamentally different crystal chemistry.

---

### 3.3 Spinels

**Archetype:** LiMn2O4 (lithium manganese oxide)

**Crystal system:** Cubic | **Space group:** Fd-3m (#227)

**Structure:** A three-dimensional framework of edge-sharing MnO6 octahedra that form a robust 3D network. Lithium occupies tetrahedral 8a sites in the fully lithiated state. The oxygen ions form a cubic close-packed arrangement with Mn on half the octahedral sites.

**Li transport:** Three-dimensional diffusion through interconnected pathways. Li hops through a tetrahedral-octahedral-tetrahedral (8a-16c-8a) network, giving spinels excellent rate capability.

**Commercial relevance:** Used in power tools, some EV applications (Nissan Leaf early models), and blended cathode formulations.

**Key properties:**
- Good rate capability owing to 3D Li transport
- Suffers from **Mn dissolution** into the electrolyte, especially at elevated temperatures
- **Jahn-Teller distortion** at high depth of discharge (when Mn3+ concentration increases) causes a cubic-to-tetragonal phase transition and capacity fade

**Why it is in the benchmark:** The 3D diffusion topology is distinct from both 1D (olivine) and 2D (layered). The known scientific challenges (Mn dissolution, Jahn-Teller distortion) provide real test cases for detecting when the computational model struggles — convergence failures or unusual relaxed geometries in spinels are scientifically meaningful, not just engineering bugs.

---

### Summary Comparison

| Property | Layered (LiCoO2) | Olivine (LiFePO4) | Spinel (LiMn2O4) |
|---|---|---|---|
| Space group | R-3m (#166) | Pnma (#62) | Fd-3m (#227) |
| Li transport | 2D (layers) | 1D (channels) | 3D (network) |
| Energy density | High | Moderate | Moderate |
| Safety | Moderate | Excellent | Good |
| Key challenge | Cation disorder | Channel blocking | Mn dissolution, Jahn-Teller |
| Primary market | Consumer electronics | EVs, grid storage | Power tools, blended cathodes |

---

## 4. Structure Relaxation: What It Means and Why It Matters

Structure relaxation is the central computational operation in CathodeScope's MVP. If you understand one scientific concept deeply, make it this one.

### The problem

Crystal structures retrieved from databases (such as the Materials Project) or from experimental measurements are often idealized or correspond to a specific computational methodology. They may not represent the minimum-energy configuration for the interatomic potential CathodeScope uses (MACE). To make a meaningful comparison, the structure must first be relaxed using the same model that will be used for all downstream analysis.

### What relaxation does

Relaxation is an iterative optimization that adjusts a crystal structure to minimize its total energy according to a given interatomic potential:

1. **Start** with an initial structure (atomic positions + lattice parameters).
2. **Compute** forces on every atom and stresses on the unit cell using the interatomic potential (MACE).
3. **Move** atoms in the direction that reduces forces; adjust lattice parameters to reduce stress.
4. **Repeat** until convergence.

### What changes during relaxation

| Quantity | What happens |
|---|---|
| Atomic positions | Shift to lower-energy sites within the unit cell |
| Lattice parameters (a, b, c) | Expand or contract to minimize stress |
| Lattice angles (alpha, beta, gamma) | May adjust (especially in low-symmetry systems) |
| Total energy | Decreases monotonically toward a local minimum |
| Symmetry | May be preserved or may break (both are meaningful) |

### Convergence

The optimization iterates until the maximum force on any atom falls below a defined threshold. In CathodeScope's MVP:

- **Convergence criterion:** fmax < 0.01 eV/Angstrom (the maximum force component on any atom)
- **Maximum iterations:** defined per workflow to prevent runaway calculations

A structure is "converged" when forces are below threshold. The number of steps to reach convergence is itself a diagnostic: a structure that takes many steps or fails to converge is telling you something scientifically meaningful.

### Why it matters for CathodeScope

The relaxed structure is the **primary computed artifact** of the MVP workflow. The core validation step is:

> Compare the relaxed structure against the reference structure from Materials Project.

If lattice parameters deviate by less than a defined threshold (e.g., 2%), the workflow confirms that MACE reproduces the known structure for this material. This comparison is the foundation of every claim CathodeScope makes at validity Level A.

### Common failure modes

Engineers should recognize and handle these appropriately — they are scientific results, not just bugs:

| Failure Mode | What Happens | What It Means |
|---|---|---|
| **Structure collapse** | Atoms overlap; unphysically short bond lengths appear | The model cannot represent this material's bonding correctly |
| **Symmetry breaking** | Space group changes unexpectedly during relaxation | The model finds a lower-symmetry minimum; may indicate model limitation or a real instability |
| **Non-convergence** | fmax does not drop below threshold within max iterations | The potential energy surface is difficult for the optimizer; the model may be poorly suited to this chemistry |
| **Unphysical bond lengths** | Bond distances far outside expected ranges (e.g., Li-O < 1.5 Angstrom or > 3.0 Angstrom) | Sanity check failure; the relaxed structure is not physically meaningful |
| **Large volume change** | Unit cell volume changes by more than 5--10% | May indicate a phase transformation or model instability |

All failure modes must be logged with full metadata. A failure is a valid workflow result — it tells us the model's boundary.

---

## 5. MACE: The Machine-Learning Interatomic Potential

### What MACE is

MACE (Multi-ACE, or more precisely, the MACE architecture) is a machine-learning interatomic potential (MLIP) based on a message-passing equivariant graph neural network. Given a set of atoms and their positions, MACE predicts:

- **Energy** of the configuration (eV)
- **Forces** on each atom (eV/Angstrom)
- **Stresses** on the unit cell (eV/Angstrom^3)

These are the same quantities that DFT computes, but MACE produces them orders of magnitude faster.

### How it works (conceptual model for engineers)

Think of MACE as a learned function over atomic graphs:

1. **Atoms are nodes** in a graph. Each node has features (element type, local geometry).
2. **Bonds are edges** connecting atoms within a cutoff radius. Edge features encode distances and directions.
3. **Message passing** iterates: each atom updates its representation by aggregating information from its neighbors. Multiple rounds of message passing allow the network to capture multi-body interactions.
4. **Equivariance** means the model respects the symmetries of physics — rotating or translating the entire structure produces correspondingly rotated/translated predictions, by construction (not by data augmentation).
5. **Readout** produces per-atom energies that sum to the total energy; forces are obtained as the gradient of total energy with respect to atomic positions.

### Why MACE instead of DFT

| Property | DFT | MACE |
|---|---|---|
| Accuracy | Gold standard (within its approximations) | Near-DFT quality for trained chemistries |
| Cost per structure | Hours to days on HPC clusters | Seconds to minutes on a single GPU or CPU |
| Scaling | O(N^3) with number of electrons | O(N) with number of atoms |
| Training data required | None (first-principles) | Large dataset of DFT calculations |

For CathodeScope's screening purpose, MACE provides the right trade-off: fast enough to screen many structures, accurate enough that relaxed structures can be meaningfully compared to DFT references.

### The MACE-MP-0 foundation model

CathodeScope uses the **MACE-MP-0** foundation model, which is pre-trained on the Materials Project dataset. Key characteristics:

- **Training data:** Structures and DFT energies/forces/stresses from the Materials Project (covering most of the periodic table)
- **Coverage:** Broad but uneven — elements and structure types that are well-represented in MP have better accuracy
- **Availability:** Open-source, with pre-trained checkpoints distributed by the MACE developers

### What CathodeScope uses MACE for

- **MVP (current):** Structure relaxation of benchmark cathode materials
- **Future phases:** Energy differences between lithiated and delithiated structures for voltage estimation; potentially forces for migration barrier estimates

### Limitations engineers must know

These are not edge cases — they are fundamental characteristics that affect every result:

1. **Inherited DFT biases.** MACE learns from DFT data. If the DFT training data has a systematic error (and it does — GGA+U has known limitations), MACE reproduces that error. MACE cannot be more accurate than its training data.

2. **Non-uniform accuracy across chemistries.** Some elements and structure types have thousands of training examples; others have dozens. Accuracy for cobalt oxides (heavily studied) will generally exceed accuracy for rare-earth borides (sparse in training data).

3. **Extrapolation risk.** MACE has never "seen" structures that differ significantly from its training distribution. Predictions for truly novel compositions or extreme conditions (very high pressure, exotic coordination environments) are extrapolations and must be treated with skepticism.

4. **Not ground truth.** MACE outputs should always be compared against reference data. A MACE-relaxed structure is a prediction, not a measurement. The comparison to the MP reference is what gives the result scientific meaning.

5. **Model versioning matters.** Different MACE checkpoints can give different results. CathodeScope must pin the exact model version and record it as provenance metadata.

> **Cross-reference:** `docs/scientific_validity_matrix.md` for the property-by-property assessment of what MACE can and cannot reliably compute for CathodeScope's purposes.

---

## 6. Materials Project: The Reference Database

### What it is

The **Materials Project** (MP) is the largest open computational materials database, maintained by Lawrence Berkeley National Laboratory (LBNL). It contains data on approximately 150,000+ inorganic compounds, computed using a consistent DFT methodology.

Website: https://materialsproject.org

### Data available

| Data Type | Description | CathodeScope Use |
|---|---|---|
| Crystal structures | Relaxed atomic positions and lattice parameters | **Primary** — retrieved as reference structures |
| Formation energies | Energy relative to elemental references | Retrieved for metadata and future phases |
| Material IDs | Unique identifiers in `mp-XXXXX` format | Used to track provenance |
| Band gaps | Electronic band gap (PBE level) | Not used in MVP |
| Elastic properties | Bulk/shear modulus | Not used in MVP |
| Electronic structure | Band structure, density of states | Not used in MVP |

### The MP API

Programmatic access is provided through the `mp-api` Python client:

- Requires an **API key** (free registration at materialsproject.org)
- Returns structures as `pymatgen` `Structure` objects
- Supports queries by material ID, formula, crystal system, and many other fields
- **Rate-limited** — CathodeScope caches retrieved data to minimize API calls

### Methodology

All MP structures are computed with a consistent DFT methodology:

- **Functional:** PBE (Perdew-Burke-Ernzerhof) with Hubbard U corrections for transition metals (GGA+U)
- **U values:** Specific, documented values for each transition metal (e.g., U = 3.32 eV for Co in oxides)
- **Pseudopotentials:** PAW (projector augmented wave) from the VASP library
- **Convergence:** Standardized k-point density and energy cutoffs

This consistency is what makes MP useful as a reference: all structures are computed the same way, so comparisons between materials are internally consistent even if absolute values carry systematic errors.

### Why MP qualifies as a Level A reference source

MP qualifies as a Level A reference in CathodeScope's validity framework because it provides:

- **Consistent methodology** — every structure computed the same way
- **Well-documented provenance** — methodology, software versions, and parameters are published
- **Community scrutiny** — widely used and reviewed by the materials science community
- **Standardized identifiers** — each material has a unique mp-id for unambiguous reference

"Level A reference" means "established computational reference suitable for benchmark comparison," not "experimentally verified truth."

### Limitations

1. **MP structures are DFT-relaxed, not experimental.** They represent the minimum-energy configuration according to PBE+U, which may differ from experimentally measured structures (typically by 1--3% in lattice parameters).

2. **Systematic errors from functional choice.** GGA+U has known biases: it tends to over-delocalize electrons, underestimate band gaps, and its accuracy for formation energies varies by chemistry. The specific U values chosen affect computed lattice parameters and energies.

3. **Not all materials are experimentally verified.** MP contains hypothetical structures generated by substitution algorithms. These may never have been synthesized. CathodeScope's benchmark materials are well-known experimentally, but engineers should be aware that not all MP entries carry the same level of experimental backing.

4. **Database updates change reference values.** MP periodically recomputes entries with improved methodology or corrected parameters. For reproducibility, CathodeScope must **pin the API version** and cache retrieved data with timestamps.

> **Cross-reference:** `docs/scientific_validity_matrix.md`, Level A (retrieved reference data).

---

## 7. The Validity Ladder: Level A Outputs vs. Estimates vs. Proxies

The validity ladder is CathodeScope's framework for classifying every output by its scientific trustworthiness. It exists to prevent overclaiming — the single most dangerous failure mode for a thesis built on computational predictions.

Every output CathodeScope produces must be labeled with its validity level. No output may be presented at a higher level than warranted.

---

### Level A — Benchmarked (MVP outputs)

**What qualifies:** Retrieved or computed by benchmarked MVP workflows with full provenance.

| Sub-category | Examples | Allowed Wording |
|---|---|---|
| **Retrieved** | MP metadata, benchmark labels, literature reference values, material identifiers | "retrieved from [source]" |
| **Computed** | Normalized structure, relaxed structure, relaxation metadata (steps, final energy, fmax), deterministic workflow outputs | "computed by CathodeScope using [model version]" |
| **Compared** | Structure vs. reference deviations, family consistency checks, convergence diagnostics, sanity checks | "compared against [reference]", "consistent within [threshold]" |

**Concrete example:**

> "The relaxed lattice parameter a = 2.82 Angstrom, compared to the MP reference a = 2.84 Angstrom (deviation 0.7%). This is within the 2% threshold defined for the layered oxide benchmark."

**What makes Level A trustworthy:**
- Full provenance chain (input structure source, model version, workflow version, parameters)
- Deterministic workflow (same inputs always produce same outputs)
- Comparison against a known reference with a defined threshold
- All metadata logged and auditable

---

### Level B — Restricted Estimates

**What qualifies:** Outputs computed by benchmarked workflows in a narrow, well-defined scope. Allowed in later phases, not in the MVP thesis-core.

| Output Type | Scope Restriction |
|---|---|
| Average voltage estimate | Only for supported benchmark chemistries with reference voltage data |
| Family-constrained ranking | Only within a single cathode family, not across families |
| Limited heuristic classification | Only with explicit uncertainty bounds and caveats |

**Allowed wording:** "screening estimate," "restricted workflow estimate," "requires deeper validation."

**Concrete example:**

> "The estimated average intercalation voltage is 3.9 V based on the energy difference between lithiated and delithiated structures. This is a screening estimate requiring experimental verification."

**What distinguishes Level B from Level A:**
- The underlying physical quantity (e.g., voltage) depends on energy differences, which amplify model errors
- Validation against reference is less direct (comparing a derived quantity, not a primary observable)
- The scope is explicitly restricted to prevent generalization beyond supported cases

---

### Level C — Proxies

**What qualifies:** Screening signals computed by lightweight methods. Planned from the beginning as part of the roadmap, but never claimed as thesis-core Level A outputs.

| Proxy | Method | What It Signals |
|---|---|---|
| Stability proxy | Energy above hull comparison using MP data | Thermodynamic plausibility (not proof of stability) |
| Dynamical stability proxy | Gamma-point phonon check | Absence of obvious dynamical instability (not proof of stability) |
| Transport proxy | Lightweight migration barrier estimate (e.g., NEB or nudged-elastic-band-lite) | Whether Li mobility is plausible (not a benchmark-compared barrier) |

**Allowed wording:** "proxy," "screening signal," "follow-up recommended."

**Concrete example:**

> "The energy-above-hull proxy from MP data suggests marginal thermodynamic stability (E_hull = 0.025 eV/atom). This is a screening signal, not a proof of stability. Follow-up with higher-fidelity methods is recommended."

**What distinguishes Level C from Level B:**
- The methodology is inherently approximate (gamma-point only, not full phonon spectrum; hull distance from a database, not a bespoke calculation)
- The output is a flag, not a measurement
- No quantitative threshold is claimed as definitive

---

### Level D — Disallowed Claims

**Never allowed as thesis-core claims, regardless of workflow phase:**

| Disallowed Claim | Why It Is Disallowed |
|---|---|
| "Discovered a new stable cathode" | Discovery requires experimental validation; CathodeScope screens, it does not discover |
| "Validated migration barrier" from lightweight MD | A lightweight estimate is a proxy (Level C), not a validated barrier |
| "Proved thermodynamic stability" of hypothetical compounds using database comparison alone | Energy above hull is a necessary but not sufficient condition; many other factors affect stability |
| "Proved dynamical stability" from lightweight checks alone | Gamma-point phonon checks miss instabilities at other q-points; full phonon spectrum required |
| Any claim of experimental-grade accuracy | CathodeScope operates entirely in the computational domain |

### Why the ladder matters for thesis defense

Thesis examiners will probe the boundary between what was computed and what was claimed. The validity ladder pre-empts overreach by:

- Making every output's trustworthiness explicit and auditable
- Providing clear wording guidelines that prevent accidental overclaiming
- Separating the MVP thesis-core (Level A) from future extensions (Levels B and C)
- Defining a bright line (Level D) that is never crossed

When in doubt, assign the output the **lower** validity level. It is always safe to underclaim.

> **Cross-reference:** `docs/scientific_validity_matrix.md` for the full property-by-property table mapping each computed quantity to its validity level, allowed wording, and required caveats.

---

## 8. Common Scientific Pitfalls for Engineers

These are mistakes that competent engineers make when they first work with computational materials science. Each one has caused real problems in real projects.

### 1. Confusing DFT accuracy with experimental accuracy

DFT is a theoretical approximation, not a measurement. Agreement with experiment is often within 1--3% for lattice parameters, but can be much worse for energies (formation energies may err by 50--200 meV/atom), band gaps (GGA underestimates by 30--50%), and other properties. When you see a DFT result, do not mentally equate it with what a diffractometer or calorimeter would measure.

### 2. Treating database values as ground truth

Materials Project values are computed, not measured. They carry systematic errors from the DFT functional used (PBE+U). An MP formation energy is the result of a specific computational methodology — it is a prediction, not an observation. Treat MP data as a consistent, well-documented reference, not as absolute truth.

### 3. Assuming a relaxed structure is "correct"

Relaxation finds a local minimum of the energy surface for a given interatomic potential. That local minimum:
- Depends on the potential used (MACE vs. DFT vs. a different MLIP)
- Depends on the starting configuration
- May not correspond to the global minimum
- Must be compared to a reference to be scientifically meaningful

A relaxed structure is a prediction. Its value comes from comparison, not from the relaxation itself.

### 4. Ignoring convergence failures

A relaxation that does not converge is a **scientific result**, not just a bug. It tells you that the model struggles with this material — the potential energy surface may be flat, rugged, or poorly described by the model. Log it, report it, and do not silently retry with loosened thresholds. The failure is data.

### 5. Confusing precision with accuracy

Floating-point arithmetic gives you 15 decimal places. That does not mean the result is accurate to 15 decimal places. A lattice parameter reported as 2.819437 Angstrom has a model accuracy of perhaps +/-0.03 Angstrom. Reporting excessive decimal places creates a false impression of certainty. Report results to the number of significant figures warranted by the model's known accuracy.

### 6. Assuming model transferability

A model that is highly accurate for LiCoO2 (a well-studied layered oxide) may perform poorly for a novel Ni-rich NMC composition or an entirely different crystal family. MACE's accuracy is not uniform across chemistry space. Always check benchmark performance for the specific chemistry you are computing before trusting the results.

### 7. Overstating computational predictions

There is a critical difference between:
- "The proxy suggests the material may be stable" (correct, Level C)
- "The material is stable" (overclaim, Level D)

Every computed property is a prediction with uncertainty. The wording must reflect that uncertainty. If you find yourself writing "is" or "proves" about a computational result, rewrite with "suggests," "indicates," or "is consistent with."

### 8. Ignoring systematic errors

MACE and DFT have **systematic biases** — errors that affect all results consistently in the same direction. This is different from random noise. For example, if GGA+U consistently overestimates lattice parameters for a given chemistry by 1%, this error does not cancel when you average over many materials. Systematic errors propagate into derived quantities (voltages, energy differences) and can accumulate. Be aware that "more data" does not fix systematic bias.

---

## 9. Glossary

Alphabetically ordered. Each definition is scoped to CathodeScope's context.

**Anode** — The negative electrode of a battery. During discharge, lithium ions are released from the anode and travel to the cathode. Typically graphite in commercial Li-ion cells.

**ASE (Atomic Simulation Environment)** — A Python library for setting up, running, and analyzing atomistic simulations. CathodeScope uses ASE as the interface between crystal structures and the MACE calculator for relaxation workflows.

**Band gap** — The energy difference between the top of the valence band and the bottom of the conduction band in a solid. Determines electronic conductivity. Not a primary CathodeScope output, but available in MP metadata.

**Capacity** — The amount of electric charge a cathode can store per unit mass, typically expressed in mAh/g. Theoretical capacity is calculated from the number of extractable Li ions and the molecular weight.

**Cathode** — The positive electrode of a battery. The component CathodeScope screens. Hosts lithium ions during discharge and releases them during charge.

**CIF (Crystallographic Information File)** — A standardized text file format for describing crystal structures, including lattice parameters, space group, and atomic coordinates. One of several structure file formats CathodeScope may handle.

**Convergence** — The state reached when an iterative optimization (e.g., structure relaxation) meets its termination criteria. In CathodeScope, convergence means the maximum force on any atom is below fmax threshold.

**Coordination number** — The number of nearest-neighbor atoms surrounding a central atom. For example, Li in octahedral coordination has a coordination number of 6. Used in sanity checks for relaxed structures.

**Crystal structure** — The periodic arrangement of atoms in a solid, defined by a unit cell (lattice parameters + atomic positions) and a space group (symmetry operations). The fundamental data object in CathodeScope.

**DFT (Density Functional Theory)** — A quantum-mechanical method for computing the electronic structure and total energy of atomic systems from first principles. The gold standard for computational materials science, but computationally expensive. MACE is trained on DFT data.

**Electrolyte** — The medium that conducts lithium ions between cathode and anode. Must be ionically conducting but electronically insulating. Typically a lithium salt dissolved in an organic solvent.

**Energy above hull** — The energy difference between a compound and the thermodynamic convex hull of competing phases. A value of zero means the compound is on the hull (thermodynamically stable); positive values indicate metastability. Used as a stability proxy (Level C) in CathodeScope.

**Energy density** — Energy stored per unit mass (Wh/kg) or volume (Wh/L). The product of capacity and average voltage. The primary figure of merit for comparing cathode materials.

**Formation energy** — The energy of a compound relative to its constituent elements in their standard states. Negative formation energy indicates the compound is stable with respect to decomposition into elements.

**Intercalation** — The reversible insertion of lithium ions into a host crystal lattice. The primary mechanism by which most cathode materials operate. The host structure is preserved during intercalation (unlike conversion or alloying reactions).

**Interatomic potential** — A mathematical function or model that computes the energy and forces of an atomic system as a function of atomic positions. MACE is a machine-learned interatomic potential. Classical examples include Lennard-Jones and Buckingham potentials.

**Jahn-Teller distortion** — A geometric distortion of a crystal that occurs when a transition-metal ion has a degenerate electronic ground state. In LiMn2O4, Mn3+ (d4) is Jahn-Teller active, causing a cooperative cubic-to-tetragonal distortion at high Mn3+ concentration that degrades cycling performance.

**Lattice parameters** — The six quantities (a, b, c, alpha, beta, gamma) that define the size and shape of a crystallographic unit cell. Three lengths (in Angstrom) and three angles (in degrees). The primary quantities compared between relaxed and reference structures in CathodeScope.

**Layered oxide** — A cathode crystal structure family where lithium ions and transition-metal oxide layers alternate in a stacked arrangement. Archetype: LiCoO2. See Section 3.1.

**MACE** — A message-passing equivariant graph neural network that serves as a machine-learning interatomic potential. CathodeScope uses the MACE-MP-0 foundation model for structure relaxation. See Section 5.

**Materials Project** — An open database of computed materials properties maintained by Lawrence Berkeley National Laboratory. CathodeScope's primary source of reference crystal structures and metadata. See Section 6.

**Migration barrier** — The energy barrier a lithium ion must overcome to hop between adjacent sites in a crystal. Determines ionic conductivity. A Level C proxy in CathodeScope, not a Level A output.

**mp-id** — A unique identifier assigned to each material in the Materials Project database, in the format `mp-XXXXX` (e.g., mp-22526 for LiCoO2). Used in CathodeScope for provenance tracking.

**NCA** — LiNi_xCo_yAl_zO2, a nickel-rich layered oxide cathode material. High energy density variant used in some EV applications.

**NMC** — LiNi_xMn_yCo_zO2, a layered oxide cathode material with tunable composition. The most commercially important cathode family by market share, balancing energy density, stability, and cost.

**Olivine** — A cathode crystal structure family with the orthorhombic Pnma space group and a polyanion framework. Archetype: LiFePO4. See Section 3.2.

**Phonon** — A quantized lattice vibration in a crystal. Phonon calculations probe dynamical stability: imaginary phonon frequencies indicate a structural instability. Gamma-point phonon checks are a Level C proxy in CathodeScope.

**POSCAR** — A file format used by the VASP DFT code to specify crystal structures. Contains lattice vectors and atomic coordinates. One of several structure file formats in the computational materials ecosystem.

**Polyanion** — A complex anion group such as PO4^3-, SO4^2-, or SiO4^4- that forms part of the cathode crystal framework. The strong covalent bonds within polyanion groups stabilize the oxygen framework, improving thermal safety. Olivines are the most prominent polyanion cathode family.

**Provenance** — The complete record of how a result was produced: input data sources, software versions, model versions, parameters, and workflow steps. CathodeScope requires full provenance for all Level A outputs to ensure reproducibility.

**Pymatgen** — Python Materials Genomics, a Python library for materials analysis. Used in CathodeScope for crystal structure manipulation, symmetry analysis, and interfacing with the Materials Project API.

**Relaxation** — The iterative optimization of atomic positions and lattice parameters to minimize total energy according to an interatomic potential. The core computational operation in CathodeScope's MVP. See Section 4.

**Rock salt** — A crystal structure type (NaCl prototype, space group Fm-3m) where cations and anions alternate on a face-centered cubic lattice. Layered oxides are derived from the rock-salt structure by ordering cations into distinct layers.

**Separator** — A porous membrane between the cathode and anode that prevents electronic short circuits while allowing lithium-ion transport through its pores. Typically made of polyethylene or polypropylene.

**Space group** — One of 230 possible symmetry groups that describe the full set of symmetry operations (translations, rotations, reflections, inversions) of a three-dimensional crystal structure. Identified by a Hermann-Mauguin symbol (e.g., R-3m) and a number (e.g., #166).

**Spinel** — A cathode crystal structure family with the cubic Fd-3m space group and a 3D framework of edge-sharing transition-metal oxide octahedra. Archetype: LiMn2O4. See Section 3.3.

**Supercell** — A larger periodic cell constructed by replicating the unit cell along one or more crystallographic directions. Used when the physics requires a cell larger than the primitive unit cell (e.g., for defect calculations or certain relaxation studies).

**Unit cell** — The smallest repeating unit that, when translated periodically in three dimensions, reproduces the entire crystal. Defined by lattice parameters and the positions of atoms within it.

**Voltage** — In the battery context, the electrochemical potential difference between cathode and anode, measured in volts (V). Often reported vs. Li/Li+ (lithium metal reference). Determined by the energy difference between lithiated and delithiated cathode structures. A Level B output in CathodeScope.

**Wyckoff position** — A set of symmetrically equivalent atomic sites within a space group, labeled by a letter (e.g., 4a, 8d). Specifying which Wyckoff positions atoms occupy is a compact way to describe a crystal structure. Used in structure validation to check that atoms remain on expected sites after relaxation.

---

*This document is a living reference. Update it as CathodeScope evolves and as new domain concepts become relevant to the engineering team.*
