import base64
import datetime
import hmac
import json
from urllib.parse import urlencode

from loguru import logger

from . import consts as c


def sign(message, secretKey):
    mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp, method, request_path, body,debug = True):
    if debug == True:
        logger.debug(f'body: {body}')
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key, sign, timestamp, passphrase, flag,debug = True):
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header[c.OK_ACCESS_KEY] = api_key
    header[c.OK_ACCESS_SIGN] = sign
    header[c.OK_ACCESS_TIMESTAMP] = str(timestamp)
    header[c.OK_ACCESS_PASSPHRASE] = passphrase
    header['x-simulated-trading'] = flag
    if debug == True:
        logger.debug(f'header: {header}')
    return header

def get_header_no_sign(flag,debug = True):
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header['x-simulated-trading'] = flag
    if debug == True:
        logger.debug(f'header: {header}')
    return header

def parse_params_to_str(params):
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


def drop_none_params(params):
    """Drop top-level None values before serializing a JSON request body."""
    if isinstance(params, dict):
        return {key: value for key, value in params.items() if value is not None}
    return params


def get_timestamp():
    now = datetime.datetime.utcnow()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def signature(timestamp, method, request_path, body, secret_key):
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    message = str(timestamp) + str.upper(method) + request_path + str(body)

    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()

    return base64.b64encode(d)
