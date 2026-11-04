"""Test-scoped pytest configuration.

`test/unit/` is the suite CI runs (see .github/workflows/ci.yml). The modules
directly under `test/` are end-to-end checks that call the live OKX API and
need OKX_API_KEY / OKX_API_SECRET / OKX_PASSPHRASE from the environment or a
`.env` file, so they are skipped rather than failed when those are absent.
"""

import pathlib

import pytest

from test.config import get_api_credentials

_UNIT_DIR = pathlib.Path(__file__).parent / "unit"


def pytest_collection_modifyitems(config, items):
    api_key, api_secret, passphrase, _ = get_api_credentials()
    if api_key and api_secret and passphrase:
        return
    skip = pytest.mark.skip(reason="integration test: OKX credentials not configured")
    for item in items:
        if _UNIT_DIR not in item.path.parents:
            item.add_marker(skip)
