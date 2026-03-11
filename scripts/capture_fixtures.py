"""One-time fixture capture script.

Fetches MP API responses for the 3 benchmark materials and saves them as JSON fixtures.
Run once with a valid MP_API_KEY to populate tests/fixtures/mp_responses/.
Do NOT run in CI — fixtures are committed to version control.

Usage:
    MP_API_KEY=<your_key> python scripts/capture_fixtures.py

Implemented in T-07.
"""

# Implementation in T-07.
