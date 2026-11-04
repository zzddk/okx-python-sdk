"""Logging contract: the whole SDK uses one standard-library logging setup."""

import io
import logging

import pytest

from okx import okxclient, utils


@pytest.mark.parametrize("module", [okxclient, utils])
def test_sdk_loggers_are_stdlib(module):
    assert isinstance(module.logger, logging.Logger)


def test_sdk_records_reach_an_application_handler():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    sdk_logger = logging.getLogger("okx")
    sdk_logger.addHandler(handler)
    previous_level = sdk_logger.level
    sdk_logger.setLevel(logging.DEBUG)
    try:
        okxclient.logger.debug("visible-sdk-record")
    finally:
        sdk_logger.removeHandler(handler)
        sdk_logger.setLevel(previous_level)

    assert "visible-sdk-record" in stream.getvalue()
