"""
Contract tests for the REST API surface.

These tests do not mock individual client methods. They invoke every public
method on every *API class, capture the (HTTP method, path) pair that would be
sent to OKX, and check it against the declared path constants. This is the
layer that catches a shadowed constant (two names with the same value being
defined twice) or a method pointing at a path that is not in consts.py.

Mirror: okx/*.py -> test/unit/okx/test_contract.py
"""

import ast
import importlib
import inspect
import pathlib
from collections import Counter
from unittest.mock import MagicMock

import pytest

import okx
from okx import consts

OKX_ROOT = pathlib.Path(okx.__file__).parent

# Constants that are intentionally not dispatched by an *API method:
# - SERVER_TIMESTAMP_URL has no API-method binding (server-time correction is not implemented).
# - LIQUIDATION_ORDERS has no binding yet (tracked separately).
_CONSTS_WITHOUT_API_METHOD = {"SERVER_TIMESTAMP_URL", "LIQUIDATION_ORDERS"}

_ENDPOINT_PATHS = {
    value
    for value in vars(consts).values()
    if isinstance(value, str) and value.startswith("/api/")
}


def _iter_api_modules():
    for path in sorted(OKX_ROOT.rglob("*.py")):
        relative = path.relative_to(OKX_ROOT)
        if relative.parts[0] == "websocket" or path.name == "__init__.py":
            continue
        yield importlib.import_module("okx." + ".".join(relative.with_suffix("").parts))


def _iter_api_methods():
    for module in _iter_api_modules():
        for class_name, cls in vars(module).items():
            if not inspect.isclass(cls) or not class_name.endswith("API"):
                continue
            if cls.__module__ != module.__name__:
                continue
            for method_name, method in vars(cls).items():
                if method_name.startswith("_") or not inspect.isfunction(method):
                    continue
                yield cls, method_name


def _capture_requests(cls, method_name):
    """Invoke a method with dummy arguments and return its (method, path) pairs."""
    method = getattr(cls, method_name)
    signature = inspect.signature(method)

    positional = []
    keyword = {}
    for parameter in list(signature.parameters.values())[1:]:
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        value = MagicMock(name=parameter.name)
        if parameter.kind == parameter.KEYWORD_ONLY:
            keyword[parameter.name] = value
        else:
            positional.append(value)

    calls = []
    instance = object.__new__(cls)
    instance._request = lambda http_method, path, params=None: (
        calls.append((http_method, path)) or {"code": "0"}
    )

    method(instance, *positional, **keyword)
    return calls


def _const_source_files():
    """Every module that declares constants (the package wiring is excluded)."""
    consts_dir = OKX_ROOT / "consts"
    return sorted([consts_dir / "http.py", *sorted((consts_dir / "endpoints").glob("*.py"))])


def _const_assignments():
    for path in _const_source_files():
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        yield path.name, target.id


ALL_API_METHODS = sorted(
    _iter_api_methods(), key=lambda item: (item[0].__name__, item[1])
)


def test_constant_names_are_unique():
    """A later definition must never silently shadow an earlier one."""
    duplicates = sorted(
        name for name, count in Counter(name for _, name in _const_assignments()).items() if count > 1
    )
    assert duplicates == []


def test_constant_names_are_unique_across_modules():
    """Merging the subpackage must not let one module shadow another."""
    seen = {}
    clashes = []
    for module_name, name in _const_assignments():
        if name in seen and seen[name] != module_name:
            clashes.append((name, seen[name], module_name))
        seen[name] = module_name
    assert clashes == []


@pytest.mark.parametrize(
    "cls, method_name",
    ALL_API_METHODS,
    ids=[f"{cls.__name__}.{name}" for cls, name in ALL_API_METHODS],
)
def test_api_method_uses_a_declared_endpoint(cls, method_name):
    calls = _capture_requests(cls, method_name)
    assert calls, f"{cls.__name__}.{method_name} issued no request"
    for http_method, path in calls:
        assert http_method in (consts.GET, consts.POST)
        assert path in _ENDPOINT_PATHS, (
            f"{cls.__name__}.{method_name} requests {path!r}, "
            "which is not a path declared in okx/consts"
        )


def test_every_declared_endpoint_is_reachable():
    reached = {
        path
        for cls, method_name in ALL_API_METHODS
        for _, path in _capture_requests(cls, method_name)
    }
    unreachable = sorted(
        name
        for name, value in vars(consts).items()
        if name not in _CONSTS_WITHOUT_API_METHOD
        and isinstance(value, str)
        and value.startswith("/api/")
        and value not in reached
    )
    assert unreachable == []
