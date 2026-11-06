"""Logging contract: the whole SDK uses one standard-library logging setup."""

import asyncio
import io
import json
import logging

import httpx
import pytest

from okxsdk import transport, utils
from okxsdk.websocket.WsBaseAsync import WsBaseAsync
from okxsdk.websocket.WsPublicAsync import WsPublicAsync

from .fakes import mock_transport
from .websocket.fakes import FakeConnector, FakeSocket


class _CapturingHandler(logging.Handler):
    """Collect the fully formatted messages emitted to a logger."""

    def __init__(self) -> None:
        super().__init__()
        self.messages = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


@pytest.mark.parametrize("module", [transport, utils])
def test_sdk_loggers_are_stdlib(module):
    assert isinstance(module.logger, logging.Logger)


def test_sdk_records_reach_an_application_handler():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    sdk_logger = logging.getLogger("okxsdk")
    sdk_logger.addHandler(handler)
    previous_level = sdk_logger.level
    sdk_logger.setLevel(logging.DEBUG)
    try:
        transport.logger.debug("visible-sdk-record")
    finally:
        sdk_logger.removeHandler(handler)
        sdk_logger.setLevel(previous_level)

    assert "visible-sdk-record" in stream.getvalue()


def test_debug_log_does_not_leak_credentials():
    api_key = "LEAKTEST_KEY_abc123"
    passphrase = "LEAKTEST_PASSPHRASE_xyz789"
    secret = "LEAKTEST_SECRET_def456"

    sent_requests = []

    def handler(request):
        sent_requests.append(request)
        return httpx.Response(200, json={'code': '0'})

    captured = _CapturingHandler()
    sdk_logger = logging.getLogger("okxsdk")
    sdk_logger.addHandler(captured)
    previous_level = sdk_logger.level
    sdk_logger.setLevel(logging.DEBUG)
    try:
        client = mock_transport(
            handler,
            api_key=api_key,
            api_secret_key=secret,
            passphrase=passphrase,
            debug=True,
        )
        client.request("POST", "/api/v5/test", {"instId": "BTC-USDT"})
    finally:
        sdk_logger.removeHandler(captured)
        sdk_logger.setLevel(previous_level)

    log_text = "\n".join(captured.messages)
    # The values that really went on the wire must not appear in the log.
    headers = sent_requests[0].headers
    for value in (
        headers["OK-ACCESS-KEY"],
        headers["OK-ACCESS-SIGN"],
        headers["OK-ACCESS-PASSPHRASE"],
        passphrase,
    ):
        assert value not in log_text
    # A方案: field names are kept, values are masked. Guard against the test
    # passing merely because no debug record was emitted at all.
    assert "OK-ACCESS-KEY" in log_text
    assert "***" in log_text


def test_wsbase_instances_do_not_change_module_logger_level():
    ws_logger = logging.getLogger("okxsdk.websocket.WsBaseAsync")
    previous_level = ws_logger.level
    # A fixed non-DEBUG baseline: the old instance-level setLevel(DEBUG) would
    # be visible as a change against it.
    ws_logger.setLevel(logging.WARNING)
    baseline = ws_logger.level
    try:
        WsBaseAsync(apiKey="k", passphrase="p", secretKey="s", debug=True)
        WsBaseAsync(apiKey="k", passphrase="p", secretKey="s", debug=False)
        assert ws_logger.level == baseline
    finally:
        ws_logger.setLevel(previous_level)


# ------------------------------------------------------------------ WS masking

WS_KEY = "WS_LEAK_KEY_abc123"
WS_PASSPHRASE = "WS_LEAK_PASSPHRASE_xyz789"
WS_SECRET = "WS_LEAK_SECRET_def456"
WS_SIGN = "WS_LEAK_SIGN_def456"
WS_ACK = '{"event":"login","code":"0"}'


def _capture_ws_debug(coro):
    """Drive one WS session under a capturing handler; return (sent, log text)."""
    captured = _CapturingHandler()
    sdk_logger = logging.getLogger("okxsdk")
    sdk_logger.addHandler(captured)
    previous_level = sdk_logger.level
    sdk_logger.setLevel(logging.DEBUG)
    try:
        sent = asyncio.run(coro)
    finally:
        sdk_logger.removeHandler(captured)
        sdk_logger.setLevel(previous_level)
    return sent, "\n".join(captured.messages)


def _ws_session(sock):
    return WsPublicAsync(
        url="wss://example.com",
        connector=FakeConnector(sock),
        debug=True,
        apiKey=WS_KEY, passphrase=WS_PASSPHRASE, secretKey=WS_SECRET,
    )


def _login_values(sent):
    """The credential values that actually went on the wire in the login frame."""
    for payload in sent:
        if payload == "ping":
            continue
        frame = json.loads(payload)
        if frame.get("op") == "login":
            arg = frame["args"][0]
            return arg["apiKey"], arg["passphrase"], arg["sign"]
    raise AssertionError("no login frame was sent")


def test_ws_send_debug_log_does_not_leak_credentials():
    """The public send() entry can carry a hand-built login frame; its debug
    line must not print the credentials, and masking must be log-only."""
    sock = FakeSocket()
    ws = _ws_session(sock)

    async def run():
        await ws.start()
        try:
            await ws.send("login", [{"apiKey": WS_KEY,
                                     "passphrase": WS_PASSPHRASE,
                                     "sign": WS_SIGN}])
            return list(sock.sent)
        finally:
            await ws.stop()

    sent, log_text = _capture_ws_debug(run())

    for value in (WS_KEY, WS_PASSPHRASE, WS_SIGN):
        assert value not in log_text
    assert "***" in log_text
    assert "apiKey" in log_text
    # Masking is log-only: the frame on the wire keeps the real values.
    assert any(WS_KEY in frame for frame in sent)


def test_ws_login_debug_log_does_not_leak_credentials():
    """Invariant guard: the built-in login path was already masked."""
    sock = FakeSocket(answer_login=WS_ACK)
    ws = _ws_session(sock)

    async def run():
        await ws.start()
        try:
            await ws.login()
            return list(sock.sent)
        finally:
            await ws.stop()

    sent, log_text = _capture_ws_debug(run())

    for value in _login_values(sent):
        assert value not in log_text
    assert "***" in log_text
    assert "apiKey" in log_text
