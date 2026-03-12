"""Evidence label assignment logic.

Single source of truth for evidence label assignment.
Maps workflow steps to evidence labels per scientific_validity_matrix.md Section 3.
Implements summary inheritance: all-A → A, any-B → B, any-C → C.

Implemented in T-13.
"""

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Workflow step names that map to a known evidence type.
_STEP_EVIDENCE_MAP: dict[str, str] = {
    "fetch_structure": "A-retrieved",
    "normalize": "A-computed",
    "relax": "A-computed",  # conditional: see assign_evidence_label
    "compare_reference": "A-compared",
    "validate": "A-compared",
}

#: Human-readable rationale strings keyed by step name (benchmarked path).
_STEP_RATIONALE_MAP: dict[str, str] = {
    "fetch_structure": (
        "Crystal structure retrieved from Materials Project "
        "(established reference source). "
        "Per scientific_validity_matrix.md Row 1."
    ),
    "normalize": (
        "Structure normalized to conventional standard setting using pymatgen "
        "SpacegroupAnalyzer (deterministic geometric transformation). "
        "Per scientific_validity_matrix.md Row 2."
    ),
    "relax": (
        "Structure relaxed using MACE-MP-0 (benchmarked MVP workflow, benchmarked "
        "cathode family). "
        "Per scientific_validity_matrix.md Row 3."
    ),
    "compare_reference": (
        "Lattice parameter and volume deviations computed against Materials Project "
        "PBE+U reference values. "
        "Per scientific_validity_matrix.md Row 6."
    ),
    "validate": (
        "Structural symmetry and bond-length checks compared against expected values "
        "for the benchmarked crystal family. "
        "Per scientific_validity_matrix.md Row 8."
    ),
}

#: Rationale override for non-benchmarked relax results.
_RELAX_RESTRICTED_RATIONALE = (
    "Material family is not in the benchmarked set (layered_oxide, olivine_polyanion, "
    "spinel). Relaxation result is a restricted estimate pending benchmark coverage "
    "extension. "
    "Per scientific_validity_matrix.md Row 3 (conditional trust note)."
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def assign_evidence_label(
    output_name: str,
    step_name: str,
    material_family: str = "",
    is_benchmarked_family: bool = True,
) -> dict[str, str]:
    """Assign an evidence label for a single workflow step output.

    Maps a workflow step name to an evidence type per the scientific validity
    matrix (Section 3 Part A, rows 1–8). For the ``relax`` step, the label
    is conditional: benchmarked cathode families (layered_oxide,
    olivine_polyanion, spinel) receive ``A-computed``; all others receive
    ``B-restricted``.

    Args:
        output_name: Human-readable name of the output being labeled
            (e.g., ``"relaxed_structure"``).
        step_name: Workflow step name. Must be one of: ``fetch_structure``,
            ``normalize``, ``relax``, ``compare_reference``, ``validate``.
        material_family: Cathode material family string (e.g.,
            ``"layered_oxide"``). Informational only — ``is_benchmarked_family``
            governs the conditional downgrade logic.
        is_benchmarked_family: Whether the material belongs to a benchmarked
            cathode family. When ``False`` and ``step_name`` is ``"relax"``,
            the evidence type is downgraded to ``B-restricted``.

    Returns:
        Dict with three string keys: ``output_name``, ``evidence_type``,
        and ``rationale``.

    Raises:
        ValueError: If ``step_name`` is not in the known step-to-label map.
    """
    if step_name not in _STEP_EVIDENCE_MAP:
        raise ValueError(
            f"Unknown step name: {step_name!r}. "
            f"Known steps: {sorted(_STEP_EVIDENCE_MAP)}"
        )

    evidence_type = _STEP_EVIDENCE_MAP[step_name]
    rationale = _STEP_RATIONALE_MAP[step_name]

    if step_name == "relax" and not is_benchmarked_family:
        evidence_type = "B-restricted"
        rationale = _RELAX_RESTRICTED_RATIONALE

    return {
        "output_name": output_name,
        "evidence_type": evidence_type,
        "rationale": rationale,
    }


def assign_evidence_labels(
    step_assignments: list[tuple[str, str]],
    material_family: str = "",
    is_benchmarked_family: bool = True,
) -> list[dict[str, str]]:
    """Assign evidence labels for a list of (output_name, step_name) pairs.

    Convenience wrapper around :func:`assign_evidence_label` for processing
    multiple steps in one call.

    Args:
        step_assignments: List of ``(output_name, step_name)`` tuples.
        material_family: Cathode material family string.
        is_benchmarked_family: Whether the material belongs to a benchmarked
            cathode family.

    Returns:
        List of label dicts in the same order as the input pairs.
    """
    return [
        assign_evidence_label(
            output_name=output_name,
            step_name=step_name,
            material_family=material_family,
            is_benchmarked_family=is_benchmarked_family,
        )
        for output_name, step_name in step_assignments
    ]


def compute_summary_evidence_level(labels: list[str]) -> str:
    """Compute the summary evidence level as the weakest constituent level.

    Evidence levels in descending strength: A > B > C. The summary inherits
    the weakest level present across all constituent labels.

    Args:
        labels: List of evidence type strings, e.g.
            ``["A-retrieved", "A-computed", "B-restricted"]``.

    Returns:
        Single-character level string: ``"A"``, ``"B"``, or ``"C"``.
    """
    if not labels:
        return "A"

    if any(lbl.startswith("C") for lbl in labels):
        return "C"
    if any(lbl.startswith("B") for lbl in labels):
        return "B"
    return "A"
