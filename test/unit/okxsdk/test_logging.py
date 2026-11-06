"""Logging contract: the whole SDK uses one standard-library logging setup."""

import io
import logging

import httpx
import pytest

from okxsdk import transport, utils
from okxsdk.websocket.WsBaseAsync import WsBaseAsync

from .fakes import mock_transport


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
