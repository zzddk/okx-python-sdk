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
from unittest.mock import patch

import pytest

from okx import MarketData, PublicData
from okx import consts as c
from okx.Account import AccountAPI
from okx.BlockTrading import BlockTradingAPI
from okx.Trade import TradeAPI

from .endpoints import DEFAULTED_COLLECTIONS, ENDPOINTS
from .fakes import FakeTransport, assert_request
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


# A representative slice of endpoints where callers pass arguments
# positionally. The expected mapping is written out, not derived from the
# signature, so reordering a parameter or renaming it fails here.
POSITIONAL = [
    pytest.param(
        AccountAPI, 'set_leverage', ('10', 'cross', 'BTC-USDT'),
        {'lever': '10', 'mgnMode': 'cross', 'instId': 'BTC-USDT'},
        id='AccountAPI.set_leverage'),
    pytest.param(
        AccountAPI, 'get_positions', ('SWAP', 'BTC-USDT-SWAP', 'p1'),
        {'instType': 'SWAP', 'instId': 'BTC-USDT-SWAP', 'posId': 'p1'},
        id='AccountAPI.get_positions'),
    pytest.param(
        AccountAPI, 'get_leverage', ('cross', 'BTC', 'BTC-USDT'),
        {'mgnMode': 'cross', 'ccy': 'BTC', 'instId': 'BTC-USDT'},
        id='AccountAPI.get_leverage'),
    pytest.param(
        TradeAPI, 'place_order', ('BTC-USDT', 'cash', 'buy', 'limit', '1'),
        {'instId': 'BTC-USDT', 'tdMode': 'cash', 'side': 'buy',
         'ordType': 'limit', 'sz': '1'},
        id='TradeAPI.place_order'),
    pytest.param(
        TradeAPI, 'cancel_order', ('BTC-USDT', 'o1', 'c1'),
        {'instId': 'BTC-USDT', 'ordId': 'o1', 'clOrdId': 'c1'},
        id='TradeAPI.cancel_order'),
    pytest.param(
        MarketData.MarketAPI, 'get_candlesticks', ('BTC-USDT', '1m', '2m', '1H', '100'),
        {'instId': 'BTC-USDT', 'after': '1m', 'before': '2m',
         'bar': '1H', 'limit': '100'},
        id='MarketAPI.get_candlesticks'),
    pytest.param(
        PublicData.PublicAPI, 'get_instruments', ('SPOT', 'BTC', 'BTC-USDT', 'BTC-USDT-SWAP'),
        {'instType': 'SPOT', 'uly': 'BTC', 'instId': 'BTC-USDT',
         'instFamily': 'BTC-USDT-SWAP'},
        id='PublicAPI.get_instruments'),
]


@pytest.mark.parametrize('cls, name, arguments, expected', POSITIONAL)
def test_representative_endpoints_keep_their_positional_order(cls, name, arguments, expected):
    transport = FakeTransport()
    getattr(cls(transport), name)(*arguments)
    assert len(transport.calls) == 1
    sent = transport.calls[0][2] or {}
    assert {parameter: sent.get(parameter) for parameter in expected} == expected


def test_the_table_covers_every_public_method():
    declared = {(cls, name) for cls, rows in ENDPOINTS.items() for name in rows}
    actual = set(ALL_API_METHODS)
    assert sorted(actual - declared, key=lambda item: (item[0].__name__, item[1])) == []
    assert sorted(declared - actual, key=lambda item: (item[0].__name__, item[1])) == []


@pytest.mark.parametrize(
    'cls, name, keys', DEFAULTED_COLLECTIONS,
    ids=[f'{cls.__name__}.{name}' for cls, name, _ in DEFAULTED_COLLECTIONS])
def test_collection_parameters_default_to_an_empty_list(cls, name, keys):
    transport = FakeTransport()
    getattr(cls(transport), name)()
    assert len(transport.calls) == 1, f'{cls.__name__}.{name} sent {len(transport.calls)} requests'
    params = transport.calls[0][2]
    assert {key: params[key] for key in keys} == {key: [] for key in keys}


@patch.object(BlockTradingAPI, 'request')
def test_create_rfq_with_explicit_none_does_not_send_legs(mock_request):
    mock_request.return_value = {'code': '0'}
    BlockTradingAPI(FakeTransport()).create_rfq(legs=None)
    assert_request(
        mock_request, c.POST, c.CREATE_RFQ,
        {'counterparties': [], 'anonymous': 'false', 'allowPartialExecution': 'false'})
