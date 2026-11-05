"""Table-driven coverage of the REST endpoint surface.

`endpoints.ENDPOINTS` is the one place that says which HTTP method and path each
API method targets, and which parameter names it sends. This module turns each
row into a test: call the method with one sentinel value per parameter, then
check the request the transport would send.

A row is wrong, or the implementation drifted from it, when either:

- the request does not match (method, path), or
- the sent parameters differ from the declared names, or
- the declared names differ from the method signature (a parameter was added,
  removed or renamed without updating the table).
"""
import inspect

import pytest

from .endpoints import ENDPOINTS
from .fakes import FakeTransport
from .test_contract import ALL_API_METHODS

# Parameters whose request key differs from the argument name.
ALIASES = {'from_': 'from', 'froms': 'from'}

# The spec that marks an endpoint forwarding the caller's object unchanged.
PAYLOAD = 'PAYLOAD'

ROWS = [
    pytest.param(cls, name, http_method, path, spec, id=f'{cls.__name__}.{name}')
    for cls, rows in ENDPOINTS.items()
    for name, (http_method, path, spec) in rows.items()
]


def _arguments(method):
    """One sentinel per parameter, so an argument cannot be confused with a default."""
    return {
        parameter.name: f'<{parameter.name}>'
        for parameter in inspect.signature(method).parameters.values()
        if parameter.name != 'self'
    }


def _declared_keys(spec):
    if spec.startswith('['):
        spec = spec[1:-1]
    return spec.split()


def _sent(cls, name, arguments):
    transport = FakeTransport()
    getattr(cls(transport), name)(**arguments)
    assert len(transport.calls) == 1, f'{cls.__name__}.{name} sent {len(transport.calls)} requests'
    http_method, path, params = transport.calls[0]
    return http_method, path, params


@pytest.mark.parametrize('cls, name, http_method, path, spec', ROWS)
def test_endpoint_sends_what_the_table_declares(cls, name, http_method, path, spec):
    method = getattr(cls, name)
    arguments = _arguments(method)
    sent_method, sent_path, sent = _sent(cls, name, arguments)

    assert (sent_method, sent_path) == (http_method, path)

    if spec == PAYLOAD:
        alias, payload = next(iter(arguments.items()))
        assert sent == payload, f'{cls.__name__}.{name} rewrote its {alias} payload'
        return

    if sent is None:
        sent = {}

    declared = _declared_keys(spec)
    assert len(declared) == len(set(declared)), f'{cls.__name__}.{name} lists a parameter twice'
    expected_keys = {ALIASES.get(parameter, parameter) for parameter in arguments}
    assert set(declared) == expected_keys, (
        f'{cls.__name__}.{name}: table lists {sorted(declared)}, '
        f'signature has {sorted(expected_keys)}'
    )

    if spec.startswith('['):
        assert isinstance(sent, list) and len(sent) == 1, f'{cls.__name__}.{name} does not send a one-element list'
        sent = sent[0]

    expected = {ALIASES.get(parameter, parameter): value for parameter, value in arguments.items()}
    assert sent == expected


def test_the_table_covers_every_public_method():
    declared = {(cls, name) for cls, rows in ENDPOINTS.items() for name in rows}
    actual = set(ALL_API_METHODS)
    assert sorted(actual - declared, key=lambda item: (item[0].__name__, item[1])) == []
    assert sorted(declared - actual, key=lambda item: (item[0].__name__, item[1])) == []
