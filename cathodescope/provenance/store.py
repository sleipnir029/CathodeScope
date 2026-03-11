"""Artifact store.

Implements ArtifactStore with write/read/exists/verify_integrity methods.
Directory layout per artifact_schema.md Section 3.
Artifacts are read-only after write (except cache directory).

Implemented in T-06.
"""
