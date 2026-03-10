# CathodeScope Dependency Graph

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active — Implementation Planning Document
**Cross-References**: `architecture.md` (Diagram 3, Section 8, Section 9), `artifact_schema.md` (data records, directory layout), `master_plan.md` (Section 11, implementation order)

---

## 1. Internal Module Dependency Graph

Expanded from `architecture.md` Diagram 3. Arrows point from the dependent module to the module it depends on.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FOUNDATION LAYER                             │
│                                                                     │
│  models/material.py ─────── models/results.py ─────── models/provenance.py
│       │                          │                          │        │
│       │                    models/reports.py                │        │
│       │                          │                          │        │
│       └──────────────────────────┼──────────────────────────┘        │
│                                  │                                   │
│                        config/defaults.py                            │
│                        config/settings.py                            │
│                                  │                                   │
└──────────────────────────────────┼───────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    v              v              v
┌─────────────────────────────────────────────────────────────────────┐
│                         TOOL LAYER                                  │
│                                                                     │
│  tools/mp_client.py          depends on: models/*, config/*         │
│       │                                                             │
│       v                                                             │
│  tools/structure_normalizer.py   depends on: models/*               │
│       │                                                             │
│       v                                                             │
│  tools/structure_relaxer.py      depends on: models/*, config/*     │
│       │                                                             │
│       v                                                             │
│  tools/reference_comparator.py   depends on: models/*               │
│       │                                                             │
│       v                                                             │
│  tools/physics_validator.py      depends on: models/*, validation/* │
│       │                                                             │
│       v                                                             │
│  tools/report_generator.py       depends on: models/*, reporting/*  │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          v               v               v
┌─────────────────────────────────────────────────────────────────────┐
│                      VALIDATION LAYER                               │
│                                                                     │
│  validation/structural.py        depends on: models/*               │
│  validation/convergence.py       depends on: models/*               │
│  validation/family_specific.py   depends on: models/*               │
│  validation/evidence.py          depends on: models/*               │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────────────┐
│                      REPORTING LAYER                                │
│                                                                     │
│  reporting/json_report.py        depends on: models/*               │
│  reporting/markdown_report.py    depends on: models/*,              │
│                                               reporting/json_report │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                              │
│                                                                     │
│  workflows/base.py               depends on: models/*               │
│  workflows/engine.py             depends on: models/*, tools/*,     │
│                                               validation/*          │
│  workflows/structural_analysis.py                                   │
│                                  depends on: workflows/engine.py,   │
│                                               tools/*               │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                                 │
│                                                                     │
│  provenance/store.py             depends on: models/*               │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────────────┐
│                     BENCHMARK LAYER                                 │
│                                                                     │
│  benchmark/runner.py             depends on: workflows/*, models/*, │
│                                               provenance/*          │
│  benchmark/registry.py           depends on: models/*               │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                               │
│                                                                     │
│  app/cli.py                      depends on: workflows/*,           │
│                                               benchmark/*           │
│                                                                     │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          v
┌─────────────────────────────────────────────────────────────────────┐
│                   AGENT LAYER (FUTURE - Phase 5)                    │
│                                                                     │
│  agent/*                         depends on: workflows/engine.py,   │
│                                               models/*              │
│                                  does NOT depend on: tools/*        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Critical dependency rules** (from `architecture.md`):
1. `models/*` is the only package every other package may import from.
2. Tools do not import from each other. Each tool is standalone.
3. The agent depends on `workflows/engine.py`, never on `tools/*` directly.
4. Validation modules depend only on `models/*`. They are pure functions.
5. Reporting modules depend only on `models/*` (and `reporting/json_report` for the Markdown renderer).

---

## 2. External Library Dependency Graph

Which CathodeScope modules depend on which external libraries:

```
                    pymatgen              ASE                mace-torch
                       │                  │                      │
        ┌──────────────┼──────────┐       │                      │
        │              │          │       │                      │
        v              v          v       v                      v
   mp_client    normalizer   comparator  relaxer             relaxer
                   │                      │                      │
                   v                      v                      v
              validator              (via ASE Calculator interface)
                   │
                   v
              (SpacegroupAnalyzer,
               Structure, as_dict)
```

### Dependency matrix:

| Module | pymatgen | ASE | mace-torch | mp-api | pydantic | numpy |
|--------|----------|-----|------------|--------|----------|-------|
| `models/*` | Yes (Structure serialization) | No | No | No | Yes (BaseModel) | No |
| `config/*` | No | No | No | No | Yes (validation) | No |
| `tools/mp_client` | Yes (Structure) | No | No | Yes | No | No |
| `tools/structure_normalizer` | Yes (SpacegroupAnalyzer) | No | No | No | No | No |
| `tools/structure_relaxer` | Yes (Structure conversion) | Yes (Atoms, FIRE, FrechetCellFilter) | Yes (MACECalculator) | No | No | Yes (forces array) |
| `tools/reference_comparator` | Yes (Structure, neighbor lists) | No | No | No | No | Yes (deviations) |
| `tools/physics_validator` | Yes (SpacegroupAnalyzer) | No | No | No | No | Yes (checks) |
| `tools/report_generator` | No | No | No | No | No | No |
| `validation/*` | Yes (structure analysis) | No | No | No | No | Yes (thresholds) |
| `reporting/*` | No | No | No | No | No | No |
| `workflows/*` | No (delegates to tools) | No | No | No | No | No |
| `provenance/store` | No | No | No | No | No | No |
| `benchmark/*` | No (delegates to workflows) | No | No | No | No | No |

**Key insight**: Only `tools/structure_relaxer.py` depends on ASE and mace-torch. This isolation means that MACE issues (installation, compatibility, model loading) are contained within a single module.

---

## 3. Runtime Dependency Graph

What must be available at execution time for the pipeline to function:

```
┌─────────────────────────────────────────────┐
│              RUNTIME REQUIREMENTS            │
│                                              │
│  Python 3.11+                               │
│       │                                      │
│       ├── pymatgen (installed)               │
│       ├── ASE (installed)                    │
│       ├── mace-torch (installed)             │
│       │       │                              │
│       │       └── PyTorch (installed)        │
│       ├── mp-api (installed)                 │
│       ├── pydantic v2+ (installed)           │
│       └── numpy (installed, compatible)      │
│                                              │
│  MACE-MP-0 model checkpoint                 │
│       │                                      │
│       └── File on disk at configured path    │
│           (RelaxationConfig.mace_model_path) │
│                                              │
│  Materials Project API key                   │
│       │                                      │
│       └── Environment variable: MP_API_KEY   │
│           (required for live retrieval;      │
│            not needed if running from cache) │
│                                              │
│  Filesystem permissions                      │
│       │                                      │
│       ├── Read: fixtures/, cache/            │
│       └── Write: artifacts/ directory        │
│                                              │
│  Network access (optional after caching)     │
│       │                                      │
│       └── Required for initial MP retrieval  │
│           Cached responses enable offline    │
│           development after first run        │
│                                              │
└─────────────────────────────────────────────┘
```

### Startup validation checklist:

Before the first workflow runs, verify:

1. Python version >= 3.11
2. All required packages importable (pymatgen, ase, mace, mp-api, pydantic)
3. MACE checkpoint file exists at configured path
4. MP_API_KEY environment variable set (or cached responses exist)
5. `artifacts/` directory exists and is writable
6. Dependency versions match lock file (provenance accuracy)

---

## 4. Data Artifact Dependency Graph

How data artifacts depend on each other throughout a workflow run. This is the provenance DAG (`artifact_schema.md` Section 2.5: `parent_ids` field).

```
User Input (formula: "LiCoO2")
    │
    v
NormalizedQuery
    │
    ├──────────────────────┐
    v                      v
CanonicalMaterial    MP API Response (cached)
    │                      │
    ├──────────────────────┘
    │
    v
original.json (as-retrieved structure)
    │
    v
normalized.json (conventional cell)
    │
    v
relaxed.json (MACE-relaxed structure)
    │
    ├─────────────────────────────────┐
    v                                 v
WorkflowResult                  Comparison data
    │  (all StepResults)              │
    │                                 v
    ├─────────────────────── Validation data
    │                           (evidence labels)
    v
ReportRecord (report.json)
    │
    v
report.md (human-readable)
    │
    v
BenchmarkRow (if part of benchmark)
    │
    v
BenchmarkSummary (aggregated across materials)
```

### Artifact dependency rules:

1. Every artifact's `ProvenanceRecord.parent_ids` links to its input artifacts.
2. The chain is: `CanonicalMaterial` -> `original.json` -> `normalized.json` -> `relaxed.json` -> `WorkflowResult` -> `ReportRecord` -> `BenchmarkRow`.
3. Breaking any link in this chain is a provenance gap (Risk 9 in `risk_heatmap.md`).
4. All artifacts are immutable once written (`artifact_schema.md` Section 6).

---

## 5. Minimal Boot Path for MVP

The absolute minimum needed to run LiCoO2 end-to-end (the acceptance test from `master_plan.md` Section 3):

```
REQUIRED FILES (in build order):

1. pyproject.toml                          # Dependencies
2. cathodescope/models/material.py         # CanonicalMaterial, NormalizedQuery
3. cathodescope/models/results.py          # ToolResult, WorkflowResult, StepResult, ErrorRecord
4. cathodescope/models/provenance.py       # ProvenanceRecord
5. cathodescope/models/reports.py          # ReportRecord, ReportSection
6. cathodescope/config/defaults.py         # Default parameters
7. cathodescope/config/settings.py         # Config loading
8. cathodescope/tools/mp_client.py         # MP structure retrieval
9. cathodescope/tools/structure_normalizer.py  # Conventional cell
10. cathodescope/tools/structure_relaxer.py    # MACE relaxation
11. cathodescope/tools/reference_comparator.py # Deviation calculation
12. cathodescope/tools/physics_validator.py    # Sanity checks + evidence labels
13. cathodescope/tools/report_generator.py     # Report generation
14. cathodescope/validation/structural.py      # Bond length checks
15. cathodescope/validation/convergence.py     # fmax checks
16. cathodescope/validation/evidence.py        # Evidence label assignment
17. cathodescope/reporting/json_report.py      # JSON report construction
18. cathodescope/reporting/markdown_report.py  # Markdown rendering
19. cathodescope/workflows/engine.py           # Workflow execution
20. cathodescope/workflows/structural_analysis.py  # Step sequence
21. cathodescope/provenance/store.py           # Artifact persistence

REQUIRED RUNTIME:

- Python 3.11+
- All packages from pyproject.toml installed
- MACE-MP-0 checkpoint on disk
- MP_API_KEY in environment (or cached mp-22526 response)
- Writable artifacts/ directory

REQUIRED FIXTURES (for offline development):

- tests/fixtures/mp_responses/mp-22526.json
```

**Count**: 21 source files + 1 config file + 1 fixture = 23 files minimum.

**Estimated lines of code**: ~2000-3000 lines (excluding tests), based on:
- Models: ~400 lines (pydantic definitions)
- Config: ~100 lines
- Tools: ~800 lines (6 tools, ~130 lines each)
- Validation: ~300 lines
- Reporting: ~200 lines
- Workflows: ~200 lines (engine + structural_analysis definition)
- Provenance: ~150 lines

---

## 6. Import Dependency Rules (Enforced)

These rules prevent circular dependencies and maintain the layered architecture:

| Module | May Import From | Must NOT Import From |
|--------|----------------|---------------------|
| `models/*` | Standard library, pydantic, pymatgen (Structure only) | Any `cathodescope` module |
| `config/*` | `models/*`, standard library, pydantic | `tools/*`, `workflows/*`, `validation/*` |
| `tools/*` | `models/*`, `config/*`, external libs (pymatgen, ASE, mace-torch, mp-api) | Other `tools/*` modules, `workflows/*`, `benchmark/*` |
| `validation/*` | `models/*`, pymatgen, numpy | `tools/*`, `workflows/*`, `config/*` |
| `reporting/*` | `models/*` | `tools/*`, `workflows/*`, `validation/*` |
| `workflows/*` | `models/*`, `tools/*`, `validation/*` | `benchmark/*`, `app/*`, `agent/*` |
| `provenance/*` | `models/*` | Everything else |
| `benchmark/*` | `models/*`, `workflows/*`, `provenance/*` | `tools/*` directly, `agent/*` |
| `app/*` | `workflows/*`, `benchmark/*` | `tools/*` directly |
| `agent/*` (future) | `models/*`, `workflows/engine.py` | `tools/*` directly |

**Enforcement**: mypy and import linter rules in CI. A tool importing from another tool is a code review rejection.

---

## Cross-Reference Index

| Topic | Related Document | Section |
|-------|-----------------|---------|
| Module dependency graph (authoritative) | `architecture.md` | Diagram 3 |
| Technology stack | `architecture.md` | Section 8 |
| Repository structure | `architecture.md` | Section 9 |
| Data record schemas | `artifact_schema.md` | Section 2 |
| Directory layout for artifacts | `artifact_schema.md` | Section 3 |
| Provenance record and parent_ids | `artifact_schema.md` | Section 2.5 |
| Implementation order | `implementation_order.md` | Section 2 |
| I/O contracts between modules | `architecture.md` | Section 5 |

---

*Every dependency in this document traces back to `architecture.md` Diagram 3. The dependency graph is the skeleton of the codebase — get it wrong and everything built on it is unstable.*
