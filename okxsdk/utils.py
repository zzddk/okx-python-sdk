import base64
import datetime
import hmac
import json
import logging
from typing import Any, Dict
from urllib.parse import urlencode

from . import consts as c

logger = logging.getLogger(__name__)

# One field list for both naming systems: REST header keys are declared as
# constants, WS login frames use JSON field names. ADR-0020 owns the "debug
# does not print secrets" boundary; this is the one place that says which
# fields are secret. See .scratch/credential-mask-owner/spec.md.
_SENSITIVE_FIELDS = frozenset({
    c.OK_ACCESS_KEY, c.OK_ACCESS_SIGN, c.OK_ACCESS_PASSPHRASE,
    'apiKey', 'passphrase', 'sign',
})


def mask_sensitive(value: Any) -> Any:
    """A copy for logging: field names stay, credential values do not.

    Walks dicts and lists — a REST header is flat, a WS frame nests its args
    — replacing the value of any sensitive field with ``***``. The input is
    never mutated, so masking a frame for a debug line cannot change what is
    sent on the wire.
    """
    if isinstance(value, dict):
        return {
            key: ('***' if key in _SENSITIVE_FIELDS else mask_sensitive(item))
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [mask_sensitive(item) for item in value]
    return value


def _masked_header(header: Dict[str, Any]) -> Dict[str, Any]:
    """A copy for logging: field names stay, credential values do not."""
    return mask_sensitive(header)


def sign(message: str, secretKey: str) -> bytes:
    mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp: str, method: str, request_path: str, body: str, debug: bool = True) -> str:
    if debug:
        logger.debug(f'body: {body}')
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key: str, sign: Any, timestamp: str, passphrase: str, flag: str,
               debug: bool = True) -> Dict[str, Any]:
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header[c.OK_ACCESS_KEY] = api_key
    header[c.OK_ACCESS_SIGN] = sign
    header[c.OK_ACCESS_TIMESTAMP] = str(timestamp)
    header[c.OK_ACCESS_PASSPHRASE] = passphrase
    header['x-simulated-trading'] = flag
    if debug:
        logger.debug(f'header: {_masked_header(header)}')
    return header

def get_header_no_sign(flag: str, debug: bool = True) -> Dict[str, Any]:
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header['x-simulated-trading'] = flag
    if debug:
        logger.debug(f'header: {_masked_header(header)}')
    return header

def parse_params_to_str(params: Dict[str, Any]) -> str:
    """Serialize query parameters. Only None means "not supplied"."""
    filtered = {}
    for key, value in params.items():
        if value is None:
            continue
        if value is True:
            value = 'true'
        elif value is False:
            value = 'false'
        elif isinstance(value, (list, dict)):
            value = json.dumps(value, separators=(',', ':'))
        filtered[key] = value
    if not filtered:
        return ''
    return '?' + urlencode(filtered)


def drop_none_params(params: Any) -> Any:
    """Drop top-level None values before serializing a JSON request body."""
    if params is None:
        return {}
    if isinstance(params, dict):
        return {key: value for key, value in params.items() if value is not None}
    return params


def get_timestamp() -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.isoformat("T", "milliseconds").replace("+00:00", "Z")
