"""OKX API constants, grouped by product area.

Every constant is re-exported here so star-import and attribute access keep
working. Endpoint modules are merged with duplicate detection: two modules
defining the same name raise instead of silently shadowing each other.
"""

from . import http, websocket
from .endpoints import (
    account,
    affiliate,
    block_trading,
    convert,
    copy_trading,
    dual_invest,
    fd_broker,
    flexible_loan,
    funding,
    glp,
    market_data,
    okusd,
    public_data,
    spread_trading,
    stacking,
    status,
    subaccount,
    trade,
    trading_bot,
    trading_data,
)

_MODULES = (http, websocket, account, affiliate, block_trading, convert, copy_trading, dual_invest, fd_broker, flexible_loan, funding, glp, market_data, okusd, public_data, spread_trading, stacking, status, subaccount, trade, trading_bot, trading_data)

_EXPORTS = {}
for _module in _MODULES:
    for _name, _value in vars(_module).items():
        if _name.startswith("_") or _name == "annotations":
            continue
        if _name in _EXPORTS:
            raise ImportError(
                f"duplicate constant {_name!r}: defined in both "
                f"{_EXPORTS[_name][1]!r} and {_module.__name__!r}"
            )
        _EXPORTS[_name] = (_value, _module.__name__)

globals().update({name: value for name, (value, _) in _EXPORTS.items()})
_NO_CREDENTIAL = http._NO_CREDENTIAL

__all__ = sorted(_EXPORTS)
