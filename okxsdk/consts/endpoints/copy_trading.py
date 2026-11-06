"""Copy trading endpoint paths."""

GET_EXISTING_LEADING_POSITIONS = '/api/v5/copytrading/current-subpositions'
GET_LEADING_POSITIONS_HISTORY = '/api/v5/copytrading/subpositions-history'
PLACE_LEADING_STOP_ORDER = '/api/v5/copytrading/algo-order'
CLOSE_LEADING_POSITIONS = '/api/v5/copytrading/close-subposition'
GET_LEADING_POSITIONS = '/api/v5/copytrading/instruments'
AMEND_EXISTING_LEADING_POSITIONS = '/api/v5/copytrading/set-instruments'
GET_PROFIT_SHARING_DETAILS = '/api/v5/copytrading/profit-sharing-details'
GET_TOTAL_PROFIT_SHARING = '/api/v5/copytrading/total-profit-sharing'
GET_UNREALIZED_PROFIT_SHARING_DETAILS = '/api/v5/copytrading/unrealized-profit-sharing-details'
