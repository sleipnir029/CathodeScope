"""CanonicalMaterial and NormalizedQuery pydantic models.

Implements:
- NormalizedQuery: first object created in any pipeline run from user input.
- CanonicalMaterial: canonical material representation used by all pipeline tools.
- classify_family(): assigns material family from space group and composition.

Implemented in T-03 and T-08b.
"""
