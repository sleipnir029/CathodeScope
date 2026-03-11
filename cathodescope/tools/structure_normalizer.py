"""Structure normalizer tool.

Converts retrieved structures to conventional standard cells
using pymatgen SpacegroupAnalyzer.get_conventional_standard_structure().

Implemented in T-09.
"""

from typing import Any

from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from cathodescope.models.provenance import create_provenance
from cathodescope.models.results import ErrorRecord, ToolResult

_TOOL_VERSION = "0.1.0"


def normalize(
    structure_dict: dict[str, Any],
    mp_id: str | None = None,
    formula: str | None = None,
) -> ToolResult:
    """Normalize a pymatgen structure dict to the conventional standard cell.

    Loads the structure from a pymatgen ``Structure.as_dict()`` representation,
    applies ``SpacegroupAnalyzer.get_conventional_standard_structure()``, and
    returns a :class:`~cathodescope.models.results.ToolResult` containing the
    conventional cell and symmetry metadata.

    Evidence type is ``'A-computed'`` per the scientific validity matrix
    (conventional cell is a deterministic, code-reproducible transformation).

    Args:
        structure_dict: pymatgen ``Structure.as_dict()`` payload.
        mp_id: Optional Materials Project identifier to embed in output data.
        formula: Optional chemical formula string to embed in output data.
            Defaults to the reduced formula of the conventional structure.

    Returns:
        A :class:`~cathodescope.models.results.ToolResult` with
        ``status='success'`` on success or ``status='failure'`` with a
        ``ComputationError`` on any exception.
    """
    try:
        structure = Structure.from_dict(structure_dict)
        analyzer = SpacegroupAnalyzer(structure)
        conventional = analyzer.get_conventional_standard_structure()

        data: dict[str, Any] = {
            "mp_id": mp_id,
            "formula": formula or str(conventional.composition.reduced_formula),
            "space_group": analyzer.get_space_group_symbol(),
            "space_group_number": analyzer.get_space_group_number(),
            "n_atoms": len(conventional.sites),
            "structure": conventional.as_dict(),
        }

        return ToolResult(
            tool_name="structure_normalizer",
            status="success",
            data=data,
            evidence_type="A-computed",
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="structure_normalizer",
                tool_version=_TOOL_VERSION,
            ),
        )

    except Exception as exc:  # noqa: BLE001
        return ToolResult(
            tool_name="structure_normalizer",
            status="failure",
            error=ErrorRecord(
                error_type="ComputationError",
                message=str(exc),
                source="structure_normalizer",
            ),
            provenance=create_provenance(
                created_by="cathodescope",
                tool_name="structure_normalizer",
                tool_version=_TOOL_VERSION,
            ),
        )
