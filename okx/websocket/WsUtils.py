"""WebSocket helpers: authentication payloads and local time."""

from __future__ import annotations

import base64
import hmac
import json
import time


def initLoginParams(
    apiKey: str,
    passphrase: str,
    secretKey: str,
) -> str:
    timestamp = getLocalTime()
    message = str(timestamp) + 'GET' + '/users/self/verify'
    mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    sign = base64.b64encode(d)
    arg = {"apiKey": apiKey, "passphrase": passphrase, "timestamp": timestamp, "sign": sign.decode("utf-8")}
    payload = {"op": "login", "args": [arg]}
    return json.dumps(payload)


def getLocalTime() -> int:
    return int(time.time())
