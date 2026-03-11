"""Evidence label assignment logic.

Single source of truth for evidence label assignment.
Maps workflow steps to evidence labels per scientific_validity_matrix.md Section 3.
Implements summary inheritance: all-A → A, any-B → B, any-C → C.

Implemented in T-13.
"""
