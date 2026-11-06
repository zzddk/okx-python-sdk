"""Unit tests for okx.utils."""

import json
import re
import warnings
from datetime import datetime, timezone
from urllib.parse import parse_qs

from okx.utils import drop_none_params, get_timestamp, parse_params_to_str


def test_empty_params_return_empty_string():
    assert parse_params_to_str({}) == ""


def test_basic_params_are_prefixed_with_question_mark():
    assert parse_params_to_str({"instId": "BTC-USDT"}) == "?instId=BTC-USDT"


def test_none_values_are_dropped_but_empty_strings_are_sent():
    params = {"instId": "BTC-USDT", "after": "", "before": None}
    assert parse_params_to_str(params) == "?instId=BTC-USDT&after="


def test_lists_and_dicts_are_serialized_as_json():
    params = {
        "attachAlgoOrds": [{"instId": "BTC-USDT-SWAP"}],
        "meta": {"a": 1},
    }
    parsed = parse_qs(parse_params_to_str(params)[1:])

    assert json.loads(parsed["attachAlgoOrds"][0]) == [{"instId": "BTC-USDT-SWAP"}]
    assert json.loads(parsed["meta"][0]) == {"a": 1}


def test_booleans_are_lowercase():
    assert parse_params_to_str({"reduceOnly": True, "flag": False}) == (
        "?reduceOnly=true&flag=false"
    )


def test_special_characters_are_url_encoded():
    params = {"tag": "a&b=c", "note": "hello world"}
    query = parse_params_to_str(params)

    assert query.startswith("?")
    # A raw '&' or '=' would split the value; parse_qs must recover it intact.
    assert parse_qs(query[1:]) == {"tag": ["a&b=c"], "note": ["hello world"]}


def test_drop_none_params_keeps_empty_strings():
    assert drop_none_params({"a": None, "b": "", "c": "0"}) == {"b": "", "c": "0"}


def test_drop_none_params_passes_lists_through():
    orders = [{"instId": "BTC-USDT"}]
    assert drop_none_params(orders) == orders


def test_drop_none_params_turns_none_into_an_empty_body():
    assert drop_none_params(None) == {}


def test_timestamp_is_utc_iso_with_milliseconds():
    value = get_timestamp()
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z', value)
    stamp = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
    assert abs((datetime.now(timezone.utc) - stamp).total_seconds()) < 5


def test_timestamp_does_not_use_deprecated_utcnow():
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        get_timestamp()
