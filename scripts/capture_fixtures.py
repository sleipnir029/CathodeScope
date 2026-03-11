"""One-time fixture capture script.

Fetches MP API responses for the 3 benchmark materials and saves them as JSON
fixtures. Run once with a valid MP_API_KEY to populate
``tests/fixtures/mp_responses/``.

Do NOT run in CI — fixtures are committed to version control.

Usage::

    MP_API_KEY=<your_key> python scripts/capture_fixtures.py

Implemented in T-07.
"""

import json
import os
import sys
from pathlib import Path

# Ensure the repo root is on sys.path when executed directly.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from cathodescope.tools.mp_client import CathodescopeMPClient  # noqa: E402

_BENCHMARK_MATERIALS = ["mp-22526", "mp-19017", "mp-18767"]
_OUTPUT_DIR = _REPO_ROOT / "tests" / "fixtures" / "mp_responses"


def main() -> None:
    """Capture fixture JSON files for all benchmark materials."""
    api_key = os.environ.get("MP_API_KEY", "").strip()
    if not api_key:
        print("ERROR: MP_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Use a temporary cache dir so we don't pollute the artifact cache.
    cache_dir = _REPO_ROOT / "artifacts" / "cache" / "mp_capture_tmp"

    client = CathodescopeMPClient(api_key=api_key, cache_dir=cache_dir)

    for mp_id in _BENCHMARK_MATERIALS:
        print(f"Fetching {mp_id}…")
        result = client.fetch_by_mp_id(mp_id)
        if result.status != "success" or result.data is None:
            msg = result.error.message if result.error else "unknown error"
            print(f"  FAILED: {msg}", file=sys.stderr)
            continue

        out_path = _OUTPUT_DIR / f"{mp_id}.json"
        out_path.write_text(json.dumps(result.data, indent=2), encoding="utf-8")
        print(f"  Saved → {out_path.relative_to(_REPO_ROOT)}")

    print("Done.")


if __name__ == "__main__":
    main()
