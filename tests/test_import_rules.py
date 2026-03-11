"""Import rule enforcement tests for CathodeScope.

T-00: Placeholder for the two required scaffold tests.
Full import rule enforcement (via ast.parse) implemented in T-27.
"""


def test_package_importable() -> None:
    """cathodescope imports successfully and exposes __version__."""
    import cathodescope

    assert hasattr(cathodescope, "__version__")
    assert cathodescope.__version__ == "0.1.0"


def test_all_subpackages_importable() -> None:
    """Every cathodescope subpackage imports without error."""
    import cathodescope.app  # noqa: F401
    import cathodescope.benchmark  # noqa: F401
    import cathodescope.config  # noqa: F401
    import cathodescope.models  # noqa: F401
    import cathodescope.provenance  # noqa: F401
    import cathodescope.reporting  # noqa: F401
    import cathodescope.tools  # noqa: F401
    import cathodescope.validation  # noqa: F401
    import cathodescope.workflows  # noqa: F401
