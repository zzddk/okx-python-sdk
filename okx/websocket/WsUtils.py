"""WebSocket helpers: authentication payloads and channel validation."""

from __future__ import annotations

import base64
import hmac
import json
import time
from typing import Any, Dict, List, Optional, Set


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


def isNotBlankStr(param: Any) -> bool:
    return isinstance(param, str) and param.strip() != ""


def getParamKey(arg: Dict[str, Any]) -> str:
    s = ""
    for k in arg:
        if k == 'channel':
            continue
        s = s + "@" + arg.get(k)
    return s


def initSubscribeSet(arg: Optional[Dict[str, Any]]) -> Set[str]:
    paramsSet: Set[str] = set()
    if arg is None:
        return paramsSet
    elif isinstance(arg, dict):
        paramsSet.add(getParamKey(arg))
        return paramsSet
    else:
        raise ValueError("arg must dict")


def checkSocketParams(
    args: List[Dict[str, Any]],
    channelArgs: Dict[str, List[Dict[str, Any]]],
    channelParamMap: Dict[str, Set[str]],
) -> None:
    for arg in args:
        channel = arg['channel'].strip()
        if not isNotBlankStr(channel):
            raise ValueError("channel must not none")
        argSet = channelParamMap.get(channel, set())
        argKey = getParamKey(arg)
        if argKey in argSet:
            continue
        else:
            validParams = initSubscribeSet(arg)
        if len(validParams) < 1:
            continue
        p = {}
        for k in arg:
            p[k.strip()] = arg.get(k).strip()
        channelParamMap[channel] = channelParamMap.get(channel, set()) | validParams
        if channel not in channelArgs:
            channelArgs[channel] = []
        channelArgs[channel].append(p)


def getLocalTime() -> int:
    return int(time.time())
