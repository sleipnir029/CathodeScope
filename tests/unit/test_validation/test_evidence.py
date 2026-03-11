"""Unit tests for cathodescope.validation.evidence.

14 evidence label tests for T-13.
"""

from cathodescope.validation.evidence import (
    assign_evidence_label,
    assign_evidence_labels,
    compute_summary_evidence_level,
)

# ---------------------------------------------------------------------------
# Per-step label assignment
# ---------------------------------------------------------------------------


def test_label_retrieved_data_as_a_retrieved() -> None:
    label = assign_evidence_label("retrieved_structure", "fetch_structure")
    assert label["evidence_type"] == "A-retrieved"


def test_label_normalized_structure_as_a_computed() -> None:
    label = assign_evidence_label("normalized_structure", "normalize")
    assert label["evidence_type"] == "A-computed"


def test_label_relaxed_structure_as_a_computed() -> None:
    label = assign_evidence_label(
        "relaxed_structure",
        "relax",
        material_family="layered_oxide",
        is_benchmarked_family=True,
    )
    assert label["evidence_type"] == "A-computed"


def test_label_comparison_result_as_a_compared() -> None:
    label = assign_evidence_label("comparison_result", "compare_reference")
    assert label["evidence_type"] == "A-compared"


def test_label_validation_result_as_a_compared() -> None:
    label = assign_evidence_label("validation_result", "validate")
    assert label["evidence_type"] == "A-compared"


def test_label_relaxed_structure_as_b_restricted_for_non_benchmarked_family() -> None:
    label = assign_evidence_label(
        "relaxed_structure",
        "relax",
        material_family="other",
        is_benchmarked_family=False,
    )
    assert label["evidence_type"] == "B-restricted"


# ---------------------------------------------------------------------------
# Label dict structure
# ---------------------------------------------------------------------------


def test_assign_evidence_labels_returns_list_of_label_dicts() -> None:
    labels = assign_evidence_labels(
        [
            ("retrieved_structure", "fetch_structure"),
            ("normalized_structure", "normalize"),
        ]
    )
    assert isinstance(labels, list)
    assert len(labels) == 2
    assert all(isinstance(lbl, dict) for lbl in labels)


def test_evidence_label_dict_has_output_name() -> None:
    label = assign_evidence_label("retrieved_structure", "fetch_structure")
    assert "output_name" in label
    assert label["output_name"] == "retrieved_structure"


def test_evidence_label_dict_has_evidence_type() -> None:
    label = assign_evidence_label("retrieved_structure", "fetch_structure")
    assert "evidence_type" in label
    assert isinstance(label["evidence_type"], str)


def test_evidence_label_dict_has_rationale() -> None:
    label = assign_evidence_label("retrieved_structure", "fetch_structure")
    assert "rationale" in label
    assert isinstance(label["rationale"], str)
    assert len(label["rationale"]) > 0


# ---------------------------------------------------------------------------
# Summary inheritance
# ---------------------------------------------------------------------------


def test_label_summary_all_level_a_returns_level_a() -> None:
    labels = ["A-retrieved", "A-computed", "A-compared"]
    assert compute_summary_evidence_level(labels) == "A"


def test_label_summary_mixed_a_and_b_returns_level_b() -> None:
    labels = ["A-retrieved", "A-computed", "B-restricted"]
    assert compute_summary_evidence_level(labels) == "B"


def test_label_summary_any_level_c_returns_level_c() -> None:
    labels = ["A-retrieved", "B-restricted", "C-proxy"]
    assert compute_summary_evidence_level(labels) == "C"


def test_label_summary_inherits_weakest_level() -> None:
    # A-computed + C-proxy: C wins (skips B entirely)
    labels = ["A-computed", "C-proxy"]
    assert compute_summary_evidence_level(labels) == "C"
