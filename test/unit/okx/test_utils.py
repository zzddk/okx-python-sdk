"""Unit tests for okx.utils."""

from urllib.parse import parse_qs

from okx.utils import parse_params_to_str


def test_empty_params_return_empty_string():
    assert parse_params_to_str({}) == ""


def test_basic_params_are_prefixed_with_question_mark():
    assert parse_params_to_str({"instId": "BTC-USDT"}) == "?instId=BTC-USDT"


def test_none_and_empty_values_are_dropped():
    params = {"instId": "BTC-USDT", "after": "", "before": None}
    assert parse_params_to_str(params) == "?instId=BTC-USDT"


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
