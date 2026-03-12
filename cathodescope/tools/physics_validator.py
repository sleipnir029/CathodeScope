"""Physics validator tool.

Wraps structural checks, convergence checks, and evidence labeling
into a single ToolResult conforming to the universal tool contract.

Implemented in T-14.
"""

from typing import Any

from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from cathodescope.config.settings import ValidationConfig
from cathodescope.models.material import CanonicalMaterial
from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ToolResult
from cathodescope.validation import CheckResult
from cathodescope.validation.convergence import run_convergence_checks
from cathodescope.validation.evidence import assign_evidence_labels
from cathodescope.validation.structural import run_structural_checks

_TOOL_VERSION = "0.1.0"

# Check names whose failure sets overall_sanity=False (critical path).
_CRITICAL_CHECKS: frozenset[str] = frozenset(
    {"bond_lengths", "atom_overlap", "fmax", "step_count", "symmetry_preserved"}
)


def validate(
    context: dict[str, Any],
    material: CanonicalMaterial,
    config: ValidationConfig | None = None,
) -> ToolResult:
    """Validate a relaxed structure using structural, convergence, and symmetry checks.

    Accepts accumulated workflow step results (context dict) together with the
    CanonicalMaterial record.  Delegates to the validation layer for all checks
    and to validation.evidence for evidence label assignment.

    Args:
        context: Dict of accumulated workflow step results.  Expected keys:

            - ``relaxed_structure``: pymatgen Structure serialised via
              :meth:`pymatgen.core.structure.Structure.as_dict`.
            - ``convergence_info``: Dict produced by
              :func:`cathodescope.tools.structure_relaxer.relax` containing
              ``converged``, ``steps``, ``energy_history``, and ``fmax_history``.
            - ``comparison_result`` *(optional)*: Data payload from
              :func:`cathodescope.tools.reference_comparator.compare`,
              containing ``symmetry_preserved``, ``reference_space_group``,
              and ``relaxed_space_group``.  When present the symmetry check
              reuses these values instead of recomputing them.

        material: CanonicalMaterial record for the material being validated.
        config: Optional :class:`~cathodescope.config.settings.ValidationConfig`
            with bond-length thresholds.  Defaults to
            ``ValidationConfig()`` (min 1.0 Å, max 4.0 Å).

    Returns:
        A :class:`~cathodescope.models.results.ToolResult` with
        ``evidence_type='A-compared'`` and ``data`` containing:

        - ``checks``: List of :class:`~cathodescope.validation.CheckResult`
          dicts (structural + convergence + symmetry).
        - ``evidence_labels``: List of evidence label dicts from
          :func:`~cathodescope.validation.evidence.assign_evidence_labels`.
        - ``overall_sanity``: ``True`` only if all critical checks pass.

        Non-critical check failures are surfaced as ``warnings``.
    """
    if config is None:
        config = ValidationConfig()

    prov = create_provenance(
        created_by="cathodescope",
        tool_name="physics_validator",
        tool_version=_TOOL_VERSION,
        config_snapshot={
            "min_bond": config.min_bond,
            "max_bond": config.max_bond,
        },
    )

    relaxed_structure: dict[str, Any] = context.get("relaxed_structure", {})
    convergence_info: dict[str, Any] = context.get("convergence_info", {})
    comparison_result: dict[str, Any] | None = context.get("comparison_result")

    # --- Delegate to validation layer ----------------------------------------
    structural = run_structural_checks(
        relaxed_structure,
        min_bond=config.min_bond,
        max_bond=config.max_bond,
    )
    convergence = run_convergence_checks(convergence_info)
    symmetry = _check_symmetry(relaxed_structure, material, comparison_result)

    all_checks: list[CheckResult] = structural + convergence + [symmetry]

    # --- Overall sanity: all critical checks must pass -----------------------
    overall_sanity: bool = all(
        c["passed"] for c in all_checks if c["check_name"] in _CRITICAL_CHECKS
    )

    # --- Soft failures become warnings ---------------------------------------
    warnings: list[str] = [
        c["message"]
        for c in all_checks
        if not c["passed"] and c["check_name"] not in _CRITICAL_CHECKS
    ]

    # --- Evidence labels (per scientific_validity_matrix.md Row 8) -----------
    is_benchmarked: bool = material.family != "other"
    evidence_labels = assign_evidence_labels(
        [("validated_structure", "validate")],
        material_family=material.family,
        is_benchmarked_family=is_benchmarked,
    )

    return ToolResult(
        tool_name="physics_validator",
        status="success",
        data={
            "checks": list(all_checks),
            "evidence_labels": evidence_labels,
            "overall_sanity": overall_sanity,
        },
        evidence_type="A-compared",
        provenance=prov,
        warnings=warnings,
    )


def _check_symmetry(
    relaxed_structure: dict[str, Any],
    material: CanonicalMaterial,
    comparison_result: dict[str, Any] | None,
) -> CheckResult:
    """Return a CheckResult for space-group preservation after relaxation.

    When ``comparison_result`` is provided (from a prior reference_comparator
    step), reuses the ``symmetry_preserved``, ``reference_space_group``, and
    ``relaxed_space_group`` values to avoid recomputing.  Otherwise determines
    both space groups from the raw structure dicts using SpacegroupAnalyzer.

    Args:
        relaxed_structure: Serialised pymatgen Structure dict for the relaxed
            structure.
        material: CanonicalMaterial containing the reference structure dict.
        comparison_result: Optional data payload from reference_comparator.

    Returns:
        A :class:`~cathodescope.validation.CheckResult` with
        ``check_name='symmetry_preserved'``.
    """
    if comparison_result is not None:
        sym_preserved: bool = bool(comparison_result.get("symmetry_preserved", True))
        ref_sg: str = str(comparison_result.get("reference_space_group", "unknown"))
        rel_sg: str = str(comparison_result.get("relaxed_space_group", "unknown"))
    else:
        try:
            ref_s = Structure.from_dict(material.structure)
            ref_sg = SpacegroupAnalyzer(ref_s).get_space_group_symbol()
        except Exception:
            ref_sg = "unknown"

        try:
            if relaxed_structure:
                rel_s = Structure.from_dict(relaxed_structure)
                rel_sg = SpacegroupAnalyzer(rel_s).get_space_group_symbol()
            else:
                rel_sg = "unknown"
        except Exception:
            rel_sg = "unknown"

        sym_preserved = (ref_sg == rel_sg) and (ref_sg != "unknown")

    if sym_preserved:
        return CheckResult(
            check_name="symmetry_preserved",
            category="structural",
            passed=True,
            value=rel_sg,
            threshold=ref_sg,
            message=f"Space group preserved after relaxation: {rel_sg}.",
        )
    return CheckResult(
        check_name="symmetry_preserved",
        category="structural",
        passed=False,
        value=rel_sg,
        threshold=ref_sg,
        message=(
            f"Space group changed from {ref_sg} to {rel_sg} after relaxation. "
            "Relaxation may have broken crystallographic symmetry."
        ),
    )
