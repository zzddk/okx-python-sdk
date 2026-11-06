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

def _collect_exports(modules):
    """Build the export map in function scope so the loop variables do not
    linger as module globals (a private name holding an endpoint string would
    look like an undeclared constant to anything scanning `vars(consts)`)."""
    exports = {}
    for module in modules:
        for name, value in vars(module).items():
            if name.startswith("_") or name == "annotations":
                continue
            if name in exports:
                raise ImportError(
                    f"duplicate constant {name!r}: defined in both "
                    f"{exports[name][1]!r} and {module.__name__!r}"
                )
            exports[name] = (value, module.__name__)
    return exports


_EXPORTS = _collect_exports(_MODULES)

globals().update({name: value for name, (value, _) in _EXPORTS.items()})
_NO_CREDENTIAL = http._NO_CREDENTIAL

__all__ = sorted(_EXPORTS)
