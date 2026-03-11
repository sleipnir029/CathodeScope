# CathodeScope Technology Stack

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Active — Implementation Planning Document
**Cross-References**: `architecture.md` (Section 8, component specs), `master_plan.md` (MVP definition, phase roadmap), `artifact_schema.md` (serialization, storage)

---

## 1. Programming Language

| Decision | Python 3.11+ |
|----------|--------------|
| **Rationale** | Stated in `architecture.md` Section 8. Python is the lingua franca of computational materials science. pymatgen, ASE, and mace-torch are all Python-native. Type hints are mandatory throughout (`architecture.md` Section 8). Python 3.11+ provides performance improvements over 3.10, better error messages, and `tomllib` in the standard library for reading `pyproject.toml`. |
| **Alternatives considered** | Julia (strong scientific computing, but pymatgen/ASE/MACE ecosystem is Python); Rust (performance, but ecosystem mismatch); C++ (ASE/MACE wrappers exist, but development speed too slow for thesis timeline). |
| **Tradeoffs** | Python is slower than compiled languages for numerical work, but MACE and pymatgen handle the heavy computation in C/C++/Fortran under the hood. Python's role is orchestration, I/O, and validation — not number crunching. |
| **MVP-critical** | Yes. Everything depends on this. |

**Assumption**: The development machine runs macOS (Darwin). CI will target Linux (Ubuntu). Both must be supported.

---

## 2. Environment and Package Management

| Decision | `uv` for dependency management + `pyproject.toml` for project metadata + `venv` for isolation |
|----------|------|
| **Rationale** | `uv` is a fast, Rust-based Python package installer and resolver that replaces pip + pip-tools. `pyproject.toml` is the PEP 621 standard for project metadata and is referenced in `architecture.md` Section 8 (version pinning). A virtual environment (`venv`) ensures isolation from system Python. |
| **Alternatives considered** | pip + requirements.txt (functional but no resolver, lock file management is manual); conda (heavy, slow, conflicts with pip-installed scientific packages); poetry (mature but slower than uv, adds complexity). |
| **Tradeoffs** | `uv` is newer and may have edge cases with complex scientific packages (mace-torch depends on PyTorch). Fallback: use pip directly with a pinned `requirements.txt` generated from `pyproject.toml`. |
| **MVP-critical** | Yes. Reproducible environments are required for provenance (`artifact_schema.md` Section 2.5 — `ProvenanceRecord.dependencies`). |

**Fallback**: If `uv` causes issues with mace-torch or PyTorch installation, fall back to `pip install -e ".[dev]"` with a `pyproject.toml` that declares all dependencies. The lock file can be generated with `pip freeze > requirements.lock`.

**Lock file strategy**: Pin all dependency versions in a lock file and commit it. The `ProvenanceRecord.dependencies` field captures the exact versions at runtime, but the lock file ensures anyone can reproduce the environment.

---

## 3. Scientific Libraries

### 3.1 pymatgen (Python Materials Genomics)

| Decision | pymatgen, latest stable, pinned in lock file |
|----------|------|
| **Rationale** | Listed in `architecture.md` Section 8. CathodeScope uses pymatgen for: crystal structure representation (`Structure`), symmetry analysis (`SpacegroupAnalyzer`), structure I/O (`as_dict()` serialization per `artifact_schema.md`), neighbor-finding for bond length analysis, and conventional cell standardization. pymatgen is the de facto standard library for computational materials science in Python. |
| **Used by** | `structure_normalizer`, `reference_comparator`, `physics_validator`, `mp_client` (indirectly, via mp-api), `models/material.py` (Structure serialization). |
| **MVP-critical** | Yes. Core dependency for structure manipulation and comparison. |

### 3.2 ASE (Atomic Simulation Environment)

| Decision | ASE, latest stable, pinned in lock file |
|----------|------|
| **Rationale** | Listed in `architecture.md` Section 8. ASE provides the interface between pymatgen structures and the MACE calculator. CathodeScope uses ASE for: FIRE optimizer (default, per `architecture.md` Section 4.4.3), FrechetCellFilter for cell relaxation, and the `Calculator` interface that MACE implements. |
| **Used by** | `structure_relaxer` exclusively. No other module imports ASE directly. |
| **MVP-critical** | Yes. Required for MACE-based relaxation. |

### 3.3 mace-torch (MACE-MP-0)

| Decision | mace-torch, pinned to a specific version recorded in provenance |
|----------|------|
| **Rationale** | Listed in `architecture.md` Section 8. MACE-MP-0 is the machine-learning interatomic potential used for all structure relaxations. The model checkpoint version is especially critical: different checkpoints produce different energies and forces (`architecture.md` Section 8, version pinning note). |
| **Used by** | `structure_relaxer` exclusively. |
| **Installation note** | mace-torch depends on PyTorch. The PyTorch version must be compatible with the MACE version. CPU-only PyTorch is sufficient for MVP (benchmark materials have small unit cells: 12-56 atoms). GPU support is a later-phase optimization. |
| **MVP-critical** | Yes. The core computational engine. |

**Assumption**: MACE-MP-0 foundation model checkpoint is available for download. The exact checkpoint path is configured via `RelaxationConfig.mace_model_path` (`architecture.md` Section 4.4.3).

### 3.4 mp-api (Materials Project API Client)

| Decision | mp-api, latest stable, pinned in lock file |
|----------|------|
| **Rationale** | Listed in `architecture.md` Section 8. The official Python client for the Materials Project REST API. Returns structures as pymatgen `Structure` objects natively. Supports queries by material ID, formula, and other fields. |
| **Used by** | `mp_client` tool exclusively. |
| **MVP-critical** | Yes. Required for retrieving reference structures and metadata. |

**Assumption**: An MP API key is available. The key is stored as an environment variable (`MP_API_KEY`), never in code or configuration files committed to version control.

### 3.5 numpy

| Decision | numpy, version constrained by pymatgen/ASE/MACE compatibility |
|----------|------|
| **Rationale** | Transitive dependency of pymatgen, ASE, and mace-torch. Also used directly for numerical comparisons in `reference_comparator` and `physics_validator` (deviation calculations, force array processing). |
| **Used by** | Multiple modules, primarily through pymatgen and ASE. |
| **MVP-critical** | Yes (transitive). |

---

## 4. Data Modeling and Validation

| Decision | pydantic v2+ |
|----------|------|
| **Rationale** | Listed in `architecture.md` Section 8. All data models are defined as pydantic `BaseModel` subclasses with strict validation (`architecture.md` Sections 4.2, 4.3, 9). Pydantic provides: JSON serialization/deserialization aligned with `artifact_schema.md`, schema validation at construction time, type coercion with clear error messages, and `.model_dump()` / `.model_validate()` for artifact I/O. |
| **Alternatives considered** | Python dataclasses (no validation, no JSON schema generation); attrs (less ecosystem support for JSON serialization); marshmallow (separate schema/model definitions, more boilerplate). |
| **Tradeoffs** | pydantic v2 is a significant rewrite from v1. Must use v2+ syntax (`model_dump` not `dict`, `model_validate` not `parse_obj`). v2 is faster than v1 due to Rust-based core. |
| **MVP-critical** | Yes. Every data record in `artifact_schema.md` maps to a pydantic model. |

---

## 5. Serialization and Storage

| Decision | JSON for all artifact serialization; local filesystem for storage |
|----------|------|
| **Rationale** | JSON is specified in `artifact_schema.md` Section 1 ("JSON-serializable: Every record can be serialized to JSON") and `architecture.md` Section 8 ("Serialization: JSON, standard library"). Local filesystem storage is specified in `architecture.md` Section 4.6 ("Storage backend (MVP): Local filesystem under the `artifacts/` directory"). |
| **Alternatives considered** | SQLite (queryable, but adds complexity and a dependency for MVP); HDF5 (good for large numerical data, but overkill for structure JSON and metadata); YAML (more readable than JSON but slower parsing and no standard library support). |
| **Tradeoffs** | JSON files are human-readable and diff-friendly but not queryable without loading. For the MVP benchmark set (3 materials), this is a non-issue. Database-backed storage is a deferred extension (`architecture.md` Section 4.6, deferred). |
| **File conventions** | 2-space indentation, lowercase filenames with underscores, UUIDs for IDs (`artifact_schema.md` Section 3). |
| **MVP-critical** | Yes. |

---

## 6. Configuration and Secrets

| Decision | pydantic v2+ models + JSON config files; environment variables for secrets |
|----------|------|
| **Rationale** | `architecture.md` Section 8 specifies pydantic v2+ models for configuration, consistent with the project-wide decision to use pydantic for all data modeling (Section 4). Defaults live in code (`config/defaults.py`), overrides come from JSON config files (`config/settings.py`). Secrets (MP API key) use environment variables — never committed to version control. |
| **Config structure** | |

```
config/
  defaults.py          # Default values for all parameters (fmax, max_steps, tolerances, etc.)
  settings.py          # Loads JSON config, merges with defaults, validates with pydantic
```

| **Secrets management** | `MP_API_KEY` environment variable. Checked at startup by `mp_client`. Clear error message if missing. |
| **MVP-critical** | Yes. Configuration drives relaxation parameters, comparison thresholds, and benchmark behavior. |

**Assumption**: No cloud-based secret management needed for MVP. Environment variables suffice.

---

## 7. Testing Stack

| Decision | pytest + pytest-cov |
|----------|------|
| **Rationale** | pytest is listed in `architecture.md` Section 8. pytest-cov provides coverage reporting aligned with the Phase 4 gate criterion (> 80% coverage for core modules, `master_plan.md` Section 5, Phase 4). |
| **Test organization** | Per `architecture.md` Section 9: `tests/unit/` (one test file per source module), `tests/integration/` (end-to-end workflow tests), `tests/fixtures/` (mock MP responses, reference structures, configs). |
| **Mocking strategy** | Mock MP API responses with cached JSON fixtures for offline testing. Mock MACE calculator for unit tests (return pre-computed relaxation results). Integration tests use real MACE but cached MP data. |
| **Alternatives considered** | unittest (standard library but verbose); hypothesis (property-based testing — useful but not MVP-critical, can be added incrementally). |
| **MVP-critical** | Yes. Tests are Phase 1 deliverables (`master_plan.md` Section 5, Phase 1 gate: "Unit tests pass for each module"). |

**Optional addition**: `hypothesis` for property-based testing of validation logic (e.g., "any structure with bond length < 1.0 A fails the sanity check"). Not MVP-critical but valuable for Phase 4 hardening.

---

## 8. Logging and Observability

| Decision | Python `logging` standard library; structured JSON log entries |
|----------|------|
| **Rationale** | No external logging framework needed for MVP. Python's `logging` module is sufficient. Structured JSON log entries enable post-hoc analysis of workflow execution without parsing free-form text (`architecture.md` Rule 2: "No free-form text dependencies"). |
| **Log levels** | `DEBUG` for step-level detail (force values, iteration counts); `INFO` for workflow-level events (step started/completed, material processed); `WARNING` for soft failures and threshold exceedances; `ERROR` for hard failures and exceptions. |
| **Alternatives considered** | structlog (nice API for structured logging, but adds a dependency); loguru (popular but non-standard); ELK stack (overkill for thesis project). |
| **MVP-critical** | Yes, but minimal. Logging supports debugging and provenance. The `ProvenanceRecord` (`artifact_schema.md` Section 2.5) is the primary audit trail, not logs. |

---

## 9. Reporting and Presentation

| Decision | Markdown for reports (string rendering); JSON for machine-readable reports |
|----------|------|
| **Rationale** | `architecture.md` Section 8 specifies Markdown for human-readable reports and Section 4.7 specifies that the JSON report is the primary artifact, with Markdown derived from it. Reports follow the evidence label format in `scientific_validity_matrix.md` Section 5. |
| **Future (Phase 3/7)** | Streamlit or similar for interactive dashboard. This is explicitly deferred — `master_plan.md` Section 4 defers Web UI to Phase 3 (minimal) and Phase 7 (polish). No UI framework is chosen now. |
| **Alternatives considered** | HTML templates (more formatting control but adds Jinja2 dependency); LaTeX (publication-quality but slow iteration); Jupyter notebooks (interactive but not reproducible CLI pipeline output). |
| **MVP-critical** | Yes. Report generation is a Phase 1 deliverable. |

---

## 10. CI/CD and Developer Tooling

| Decision | ruff + mypy + pre-commit + GitHub Actions |
|----------|------|
| **Rationale** | These tools enforce code quality standards aligned with the project's emphasis on reproducibility and correctness. |

### 10.1 ruff

| Role | Linter + formatter (replaces flake8, isort, black) |
|------|------|
| **Rationale** | Single tool for linting and formatting. Extremely fast (Rust-based). Configured via `pyproject.toml`. |
| **MVP-critical** | Recommended from Phase 1, not a gate criterion. |

### 10.2 mypy

| Role | Static type checker |
|------|------|
| **Rationale** | `architecture.md` Section 8 mandates type hints throughout. mypy enforces this at CI time. Catches type mismatches between tool inputs and outputs, ensuring I/O contracts (Section 5 of architecture) are respected. |
| **Configuration** | `strict` mode for `cathodescope/models/`. Gradual strictness for other packages. |
| **MVP-critical** | Recommended from Phase 1. Becomes critical at Phase 4 (hardening). |

### 10.3 pre-commit

| Role | Git hook manager for ruff + mypy checks before commit |
|------|------|
| **Rationale** | Prevents broken code from entering the repository. Runs ruff format check and ruff lint on staged files. |
| **MVP-critical** | Recommended but not a Phase 1 gate criterion. |

### 10.4 GitHub Actions

| Role | CI pipeline: test, lint, type-check on push/PR |
|------|------|
| **Rationale** | Automated quality gate. Runs `pytest`, `ruff check`, `mypy` on every push. Ensures the benchmark can run in CI (with cached MP responses and MACE fixtures). |
| **MVP-critical** | Set up in Phase 1, becomes critical at Phase 2 (benchmark must be reproducible in CI). |

---

## 11. Summary: MVP-Critical vs. Later-Phase

| Technology | MVP-Critical | Phase Introduced |
|------------|-------------|-----------------|
| Python 3.11+ | Yes | Phase 1 |
| uv / pip + pyproject.toml | Yes | Phase 1 |
| pymatgen | Yes | Phase 1 |
| ASE | Yes | Phase 1 |
| mace-torch (MACE-MP-0) | Yes | Phase 1 |
| mp-api | Yes | Phase 1 |
| numpy | Yes (transitive) | Phase 1 |
| pydantic v2+ | Yes | Phase 1 |
| JSON serialization | Yes | Phase 1 |
| Local filesystem storage | Yes | Phase 1 |
| pydantic v2+ models + JSON config | Yes | Phase 1 |
| Environment variables for secrets | Yes | Phase 1 |
| pytest + pytest-cov | Yes | Phase 1 |
| Python logging (structured) | Yes | Phase 1 |
| Markdown reports | Yes | Phase 1 |
| ruff | Recommended | Phase 1 |
| mypy | Recommended | Phase 1, critical at Phase 4 |
| pre-commit | Recommended | Phase 1 |
| GitHub Actions | Recommended | Phase 1, critical at Phase 2 |
| hypothesis | Optional | Phase 4 |
| Streamlit / web UI | No | Phase 3/7 |
| Database storage backend | No | Post-MVP |

---

## 12. Explicit Assumptions

1. **macOS development, Linux CI.** The developer's machine runs macOS (Darwin). CI runs on Ubuntu. Both must work.
2. **CPU-only MACE for MVP.** Benchmark materials have small unit cells (12-56 atoms). GPU acceleration is not needed for MVP correctness or performance.
3. **MP API key available.** A valid Materials Project API key is available as an environment variable.
4. **MACE-MP-0 checkpoint downloadable.** The pre-trained MACE-MP-0 foundation model checkpoint is publicly available.
5. **Internet access for initial MP retrieval.** After first retrieval, cached responses enable offline development (`artifact_schema.md` Section 5).
6. **No Docker for MVP.** A virtual environment with pinned dependencies is sufficient. Docker containerization is a Phase 4+ reproducibility enhancement.

---

## Cross-Reference Index

| Topic | Related Document | Section |
|-------|-----------------|---------|
| Technology stack (authoritative) | `architecture.md` | Section 8 |
| Repository structure | `architecture.md` | Section 9 |
| Version pinning and provenance | `artifact_schema.md` | Section 2.5 |
| Caching strategy | `artifact_schema.md` | Section 5 |
| Test coverage target | `master_plan.md` | Phase 4 gate criteria |
| Report format specification | `scientific_validity_matrix.md` | Section 5 |
| Benchmark reproducibility | `benchmark_spec.md` | Section 6 |

---

*Every technology choice in this document traces back to a requirement in the source documents. No choice is aspirational — each is justified by what the MVP needs to work.*
