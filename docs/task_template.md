# CathodeScope — Task Card Template

**Version**: 1.0.0
**Last Updated**: 2026-03-11
**Purpose**: Standard template for each coding session. Fill in before starting work on any task.

---

## Task Card

### Task ID
> T-XX

### Context
> What this task builds on and why it is being done now. Reference the epic, the wave, and the information dependencies that make this task ready.

### Objective
> One sentence: what does "done" look like?

### Dependencies
> List all task IDs that must be complete before starting this task. Verify each is marked Done in `task_board.md`.

| Dependency | Status |
|------------|--------|
| T-XX | Done / Todo |

### Files to Inspect Before Starting
> Read these files first to understand existing code and contracts.

| File | Why |
|------|-----|
| `path/to/file.py` | Reason for reading |

### Tests to Write First (RED Phase)
> List every test function to write before any production code. Each test must fail when first written.

```
test_function_name_1()
    → Expected behavior description
test_function_name_2()
    → Expected behavior description
```

### Implementation Notes
> Key design decisions, patterns to follow, things to watch for.

- Note 1
- Note 2

### Acceptance Criteria
> All of these must be true for the task to be marked Done.

- [ ] All tests listed above are written and passing
- [ ] `ruff check` passes on all new/modified files
- [ ] `mypy` passes on all new files (`--strict` for `models/`)
- [ ] All public functions have docstrings
- [ ] No `# TODO` comments remain
- [ ] Import rules from `dependency_graph.md` Section 6 respected
- [ ] (Task-specific criteria)

### Scientific Review
> Does this task require a scientific review checkpoint?

| Required | Checkpoint | What to verify | Reference |
|----------|------------|----------------|-----------|
| Yes / No | Description | What to check | Document section |

### Risks
> What could go wrong? What would block progress?

| Risk | Mitigation |
|------|------------|
| Description | Action |

### Completion Checklist
> Check off as you go during the session.

- [ ] Read all files listed in "Files to Inspect"
- [ ] Confirmed all dependencies are Done
- [ ] **RED**: Tests written and failing — committed with `test:` prefix
- [ ] **GREEN**: Production code written, tests passing — committed with `feat:` prefix
- [ ] **REFACTOR**: Code cleaned up, tests still passing — committed with `refactor:` prefix
- [ ] `ruff check` passes
- [ ] `mypy` passes
- [ ] Acceptance criteria verified
- [ ] Scientific review completed (if required)
- [ ] Task status updated in `task_board.md` to Done
- [ ] Next task identified

---

## Commit Convention

| Phase | Prefix | Example |
|-------|--------|---------|
| RED (failing tests) | `test:` | `test: add ProvenanceRecord creation and serialization tests` |
| GREEN (passing code) | `feat:` | `feat: implement ProvenanceRecord model with all fields` |
| REFACTOR (cleanup) | `refactor:` | `refactor: extract provenance factory helper` |
| Bug fix | `fix:` | `fix: correct ISO8601 timestamp format in ProvenanceRecord` |

---

## Session Report (fill after completing)

### What was done
> Brief summary of what was implemented.

### Tests added
> Count of new tests, all passing.

### Next task
> Which task to start next, based on `task_sequence_summary.md`.

### Blockers encountered
> Any issues that slowed progress or remain unresolved.

### Time spent
> Actual hours.

---

*Fill this template at the start of each coding session. It ensures you read the right files, write tests first, and follow the RED/GREEN/REFACTOR discipline.*
