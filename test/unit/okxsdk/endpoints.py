"""The REST endpoint surface, one row per method.

Each row is (HTTP method, path constant, spec), where spec is one of:

  "a b c"       the request carries a dict with exactly these keys
  "[a b c]"     the request carries a one-element list of such a dict
  PAYLOAD       the request carries the caller's object unchanged

test_endpoint_table.py drives every method from this table: add a row when you
add an endpoint, and update the row when its parameters change. A parameter
renamed in the signature but not here fails the sweep.

`DEFAULTED_COLLECTIONS` is the companion table for required collection
parameters: each row names a method and the request keys that must be sent as
`[]` when the caller passes nothing.
"""

from okxsdk import consts as c
from okxsdk.Account import AccountAPI
from okxsdk.Affiliate import AffiliateAPI
from okxsdk.BlockTrading import BlockTradingAPI
from okxsdk.Convert import ConvertAPI
from okxsdk.CopyTrading import CopyTradingAPI
from okxsdk.DualInvest import DualInvestAPI
from okxsdk.FDBroker import FDBrokerAPI
from okxsdk.Finance.EthStaking import EthStakingAPI
from okxsdk.Finance.FlexibleLoan import FlexibleLoanAPI
from okxsdk.Finance.Okusd import OkusdAPI
from okxsdk.Finance.Savings import SavingsAPI
from okxsdk.Finance.SolStaking import SolStakingAPI
from okxsdk.Finance.StakingDefi import StakingDefiAPI
from okxsdk.Funding import FundingAPI
from okxsdk.Grid import GridAPI
from okxsdk.MarketData import MarketAPI
from okxsdk.PublicData import PublicAPI
from okxsdk.SpreadTrading import SpreadTradingAPI
from okxsdk.Status import StatusAPI
from okxsdk.SubAccount import SubAccountAPI
from okxsdk.Trade import TradeAPI
from okxsdk.TradingData import TradingDataAPI

ENDPOINTS = {
    AccountAPI: {
        'get_position_risk': (c.GET, c.POSITION_RISK, 'instType'),
        'get_account_balance': (c.GET, c.ACCOUNT_INFO, 'ccy'),
        'get_positions': (c.GET, c.POSITION_INFO, 'instType instId posId'),
        'position_builder': (
            c.POST, c.POSITION_BUILDER,
            'acctLv inclRealPosAndEq lever greeksType simPos simAsset idxVol'),
        'get_account_bills': (
            c.GET, c.BILLS_DETAIL,
            'instType ccy mgnMode ctType type subType after before limit begin end'),
        'get_account_bills_archive': (
            c.GET, c.BILLS_ARCHIVE,
            'instType ccy mgnMode ctType type subType after before limit begin end'),
        'get_account_config': (c.GET, c.ACCOUNT_CONFIG, ''),
        'set_position_mode': (c.POST, c.POSITION_MODE, 'posMode'),
        'set_leverage': (c.POST, c.SET_LEVERAGE, 'lever mgnMode instId ccy posSide'),
        'get_max_order_size': (c.GET, c.MAX_TRADE_SIZE, 'instId tdMode ccy px tradeQuoteCcy'),
        'get_max_avail_size': (
            c.GET, c.MAX_AVAIL_SIZE,
            'instId tdMode ccy reduceOnly unSpotOffset quickMgnType tradeQuoteCcy'),
        'adjustment_margin': (c.POST, c.ADJUSTMENT_MARGIN, 'instId posSide type amt loanTrans'),
        'get_leverage': (c.GET, c.GET_LEVERAGE, 'instId mgnMode ccy'),
        'get_instruments': (c.GET, c.GET_INSTRUMENTS, 'instType uly instFamily instId'),
        'get_max_loan': (c.GET, c.MAX_LOAN, 'instId mgnMode mgnCcy tradeQuoteCcy'),
        'get_fee_rates': (c.GET, c.FEE_RATES, 'instType instId uly category instFamily groupId'),
        'get_interest_accrued': (c.GET, c.INTEREST_ACCRUED, 'instId ccy mgnMode after before limit'),
        'get_interest_rate': (c.GET, c.INTEREST_RATE, 'ccy'),
        'set_greeks': (c.POST, c.SET_GREEKS, 'greeksType'),
        'set_isolated_mode': (c.POST, c.ISOLATED_MODE, 'isoMode type'),
        'get_max_withdrawal': (c.GET, c.MAX_WITHDRAWAL, 'ccy'),
        'get_interest_limits': (c.GET, c.INTEREST_LIMITS, 'type ccy'),
        'get_simulated_margin': (c.POST, c.SIMULATED_MARGIN, 'instType inclRealPos spotOffsetType simPos'),
        'get_greeks': (c.GET, c.GREEKS, 'ccy'),
        'get_account_position_risk': (c.GET, c.ACCOUNT_RISK, ''),
        'get_positions_history': (c.GET, c.POSITIONS_HISTORY, 'instType instId mgnMode type posId after before limit'),
        'get_account_position_tiers': (c.GET, c.GET_PM_LIMIT, 'instType uly instFamily'),
        'set_risk_offset_amount': (c.POST, c.SET_RISK_OFFSET_AMT, 'ccy clSpotInUseAmt'),
        'set_auto_loan': (c.POST, c.SET_AUTO_LOAN, 'autoLoan'),
        'set_account_level': (c.POST, c.SET_ACCOUNT_LEVEL, 'acctLv'),
        'activate_option': (c.POST, c.ACTIVATE_OPTION, ''),
        'spot_manual_borrow_repay': (c.POST, c.MANUAL_REBORROW_REPAY, 'ccy side amt'),
        'set_auto_repay': (c.POST, c.SET_AUTO_REPAY, 'autoRepay'),
        'spot_borrow_repay_history': (c.GET, c.GET_BORROW_REPAY_HISTORY, 'ccy type after before limit'),
        'set_auto_earn': (c.POST, c.SET_AUTO_EARN, 'ccy action earnType'),
        'set_trading_config': (c.POST, c.SET_TRADING_CONFIG, 'type stgyType'),
        'precheck_set_delta_neutral': (c.GET, c.PRECHECK_SET_DELTA_NEUTRAL, 'stgyType'),
        'get_bill_type': (c.GET, c.BILL_TYPE, 'type'),
        'apply_bills': (c.POST, c.BILLS_APPLY, 'year quarter type'),
        'get_glp_historical_performance': (c.GET, c.GLP_HISTORICAL_PERFORMANCE, 'program begin end limit'),
        'get_glp_today_performance': (c.GET, c.GLP_TODAY_PERFORMANCE, ''),
    },
    AffiliateAPI: {
        'get_invitee_detail': (c.GET, c.AFFILIATE_INVITEE_DETAIL, 'uid periodType'),
        'get_invitee_list': (
            c.GET, c.AFFILIATE_INVITEE_LIST,
            'page limit periodType begin end keyword commissionCategory orderBy orderDir kycStatus subAffiliateUid uid'),
        'get_link_list': (c.GET, c.AFFILIATE_LINK_LIST, 'page limit linkType linkStatus'),
        'get_performance_summary': (c.GET, c.AFFILIATE_PERFORMANCE_SUMMARY, 'periodType begin end'),
        'get_tvb_tier_breakdown': (c.GET, c.AFFILIATE_TVB_TIER_BREAKDOWN, 'periodType begin end'),
    },
    BlockTradingAPI: {
        'counterparties': (c.GET, c.COUNTERPARTIES, ''),
        'create_rfq': (c.POST, c.CREATE_RFQ, 'counterparties anonymous clRfqId tag allowPartialExecution legs'),
        'cancel_rfq': (c.POST, c.CANCEL_RFQ, 'rfqId clRfqId'),
        'cancel_batch_rfqs': (c.POST, c.CANCEL_BATCH_RFQS, 'rfqIds clRfqIds'),
        'cancel_all_rfqs': (c.POST, c.CANCEL_ALL_RFQS, ''),
        'execute_quote': (c.POST, c.EXECUTE_QUOTE, 'rfqId quoteId legs'),
        'create_quote': (c.POST, c.CREATE_QUOTE, 'rfqId clQuoteId tag quoteSide legs anonymous expiresIn'),
        'cancel_quote': (c.POST, c.CANCEL_QUOTE, 'quoteId clQuoteId'),
        'cancel_batch_quotes': (c.POST, c.CANCEL_BATCH_QUOTES, 'quoteIds clQuoteIds'),
        'cancel_all_quotes': (c.POST, c.CANCEL_ALL_QUOTES, ''),
        'get_rfqs': (c.GET, c.GET_RFQS, 'rfqId clRfqId state beginId endId limit'),
        'get_quotes': (c.GET, c.GET_QUOTES, 'rfqId clRfqId quoteId clQuoteId state beginId endId limit'),
        'get_trades': (
            c.GET, c.GET_RFQ_TRADES,
            'rfqId clRfqId quoteId clQuoteId state beginId endId beginTs endTs limit'),
        'get_public_trades': (c.GET, c.GET_PUBLIC_TRADES, 'beginId endId limit'),
        'reset_mmp': (c.POST, c.MMP_RESET, ''),
        'set_marker_instrument': (c.POST, c.MAKER_INSTRUMENT_SETTING, 'PAYLOAD'),
        'get_quote_products': (c.GET, c.MAKER_INSTRUMENT_SETTING, ''),
    },
    ConvertAPI: {
        'get_currencies': (c.GET, c.GET_CURRENCIES, ''),
        'get_currency_pair': (c.GET, c.GET_CURRENCY_PAIR, 'fromCcy toCcy convertMode'),
        'estimate_quote': (c.POST, c.ESTIMATE_QUOTE, 'baseCcy quoteCcy side rfqSz rfqSzCcy clQReqId tag convertMode'),
        'convert_trade': (c.POST, c.CONVERT_TRADE, 'quoteId baseCcy quoteCcy side sz szCcy clTReqId tag convertMode'),
        'get_convert_history': (c.GET, c.CONVERT_HISTORY, 'after before limit tag'),
    },
    CopyTradingAPI: {
        'get_existing_leading_positions': (c.GET, c.GET_EXISTING_LEADING_POSITIONS, 'instId'),
        'get_leading_position_history': (c.GET, c.GET_LEADING_POSITIONS_HISTORY, 'instId after before limit'),
        'place_leading_stop_order': (
            c.POST, c.PLACE_LEADING_STOP_ORDER,
            'subPosId tpTriggerPx slTriggerPx tpTriggerPxType slTriggerPxType'),
        'close_leading_position': (c.POST, c.CLOSE_LEADING_POSITIONS, 'subPosId'),
        'get_leading_instruments': (c.GET, c.GET_LEADING_POSITIONS, ''),
        'amend_leading_instruments': (c.POST, c.AMEND_EXISTING_LEADING_POSITIONS, 'instId'),
        'get_profit_sharing_details': (c.GET, c.GET_PROFIT_SHARING_DETAILS, 'after before limit'),
        'get_total_profit_sharing': (c.GET, c.GET_TOTAL_PROFIT_SHARING, ''),
        'get_unrealized_profit_sharing_details': (c.GET, c.GET_UNREALIZED_PROFIT_SHARING_DETAILS, ''),
    },
    DualInvestAPI: {
        'get_currency_pairs': (c.GET, c.DUAL_INVEST_CURRENCY_PAIRS, ''),
        'get_product_info': (c.GET, c.DUAL_INVEST_PRODUCT_INFO, 'baseCcy quoteCcy optType'),
        'request_quote': (c.POST, c.DUAL_INVEST_REQUEST_QUOTE, 'productId notionalSz notionalCcy'),
        'trade': (c.POST, c.DUAL_INVEST_TRADE, 'quoteId'),
        'request_redeem_quote': (c.POST, c.DUAL_INVEST_REQUEST_REDEEM_QUOTE, 'ordId'),
        'redeem': (c.POST, c.DUAL_INVEST_REDEEM, 'ordId quoteId'),
        'get_order_state': (c.GET, c.DUAL_INVEST_ORDER_STATE, 'ordId'),
        'get_order_history': (
            c.GET, c.DUAL_INVEST_ORDER_HISTORY,
            'ordId productId uly state beginId endId begin end limit'),
    },
    EthStakingAPI: {
        'eth_product_info': (c.GET, c.STACK_ETH_PRODUCT_INFO, ''),
        'eth_purchase': (c.POST, c.STACK_ETH_PURCHASE, 'amt'),
        'eth_redeem': (c.POST, c.STACK_ETH_REDEEM, 'amt'),
        'eth_cancel_redeem': (c.POST, c.STACK_ETH_CANCEL_REDEEM, 'ordId'),
        'eth_balance': (c.GET, c.STACK_ETH_BALANCE, ''),
        'eth_purchase_redeem_history': (c.GET, c.STACK_ETH_PURCHASE_REDEEM_HISTORY, 'type status after before limit'),
        'eth_apy_history': (c.GET, c.STACK_ETH_APY_HISTORY, 'days'),
    },
    FDBrokerAPI: {
        'generate_rebate_details_download_link': (c.POST, c.FD_GET_REBATE_PER_ORDERS, 'begin end'),
        'get_rebate_details_download_link': (c.GET, c.FD_GET_REBATE_PER_ORDERS, 'type begin end'),
    },
    FlexibleLoanAPI: {
        'borrow_currencies': (c.GET, c.FINANCE_BORROW_CURRENCIES, ''),
        'collateral_assets': (c.GET, c.FINANCE_COLLATERAL_ASSETS, 'ccy'),
        'max_loan': (c.POST, c.FINANCE_MAX_LOAN, 'borrowCcy supCollateral'),
        'max_collateral_redeem_amount': (c.GET, c.FINANCE_MAX_REDEEM, 'ccy'),
        'adjust_collateral': (c.POST, c.FINANCE_ADJUST_COLLATERAL, 'type collateralCcy collateralAmt'),
        'loan_info': (c.GET, c.FINANCE_LOAN_INFO, ''),
        'loan_history': (c.GET, c.FINANCE_LOAN_HISTORY, 'type after before limit'),
        'interest_accrued': (c.GET, c.FINANCE_INTEREST_ACCRUED, 'ccy after before limit'),
        'borrow': (c.POST, c.FINANCE_FLEXIBLE_LOAN_BORROW, 'loanData clOrdId ordId collateralData eMode'),
        'repay': (c.POST, c.FINANCE_FLEXIBLE_LOAN_REPAY, 'ordId ccy amt clOrdId'),
        'emode_info': (c.GET, c.FINANCE_FLEXIBLE_LOAN_EMODE_INFO, ''),
    },
    FundingAPI: {
        'get_deposit_address': (c.GET, c.DEPOSIT_ADDRESS, 'ccy'),
        'transfer_state': (c.GET, c.TRANSFER_STATE, 'transId type'),
        'get_balances': (c.GET, c.GET_BALANCES, 'ccy'),
        'funds_transfer': (c.POST, c.FUNDS_TRANSFER, 'ccy amt from to type subAcct instId toInstId loanTrans'),
        'withdrawal': (c.POST, c.WITHDRAWAL_COIN, 'ccy amt dest toAddr chain areaCode clientId toAddrType'),
        'get_deposit_history': (c.GET, c.DEPOSIT_HISTORY, 'ccy type state after before limit txId depId fromWdId'),
        'get_currencies': (c.GET, c.CURRENCY_INFO, 'ccy'),
        'get_bills': (c.GET, c.BILLS_INFO, 'ccy type after before limit'),
        'get_deposit_lightning': (c.GET, c.DEPOSIT_LIGHTNING, 'ccy amt to'),
        'withdrawal_lightning': (c.POST, c.WITHDRAWAL_LIGHTNING, 'ccy invoice memo'),
        'cancel_withdrawal': (c.POST, c.CANCEL_WITHDRAWAL, 'wdId'),
        'get_asset_valuation': (c.GET, c.ASSET_VALUATION, 'ccy'),
        'get_non_tradable_assets': (c.GET, c.NON_TRADABLE_ASSETS, 'ccy'),
        'get_deposit_withdraw_status': (c.GET, c.GET_DEPOSIT_WITHDRAW_STATUS, 'wdId txId ccy to chain'),
        'get_withdrawal_history': (
            c.GET, c.GET_WITHDRAWAL_HISTORY,
            'ccy wdId clientId txId type state after before limit toAddrType'),
    },
    GridAPI: {
        'grid_order_algo': (
            c.POST, c.GRID_ORDER_ALGO, (
                'instId algoOrdType maxPx minPx gridNum runType tpTriggerPx slTriggerPx tag quoteSz baseSz sz '
                'direction lever basePos tradeQuoteCcy')),
        'grid_amend_order_algo': (c.POST, c.GRID_AMEND_ORDER_ALGO, 'algoId instId slTriggerPx tpTriggerPx'),
        'grid_stop_order_algo': (c.POST, c.GRID_STOP_ORDER_ALGO, '[algoId instId algoOrdType stopType]'),
        'grid_orders_algo_pending': (
            c.GET, c.GRID_ORDERS_ALGO_PENDING,
            'algoOrdType algoId instId instType after before limit instFamily'),
        'grid_orders_algo_history': (
            c.GET, c.GRID_ORDERS_ALGO_HISTORY,
            'algoOrdType algoId instId instType after before limit instFamily'),
        'grid_orders_algo_details': (c.GET, c.GRID_ORDERS_ALGO_DETAILS, 'algoOrdType algoId'),
        'grid_sub_orders': (c.GET, c.GRID_SUB_ORDERS, 'algoId algoOrdType type groupId after before limit'),
        'grid_positions': (c.GET, c.GRID_POSITIONS, 'algoOrdType algoId'),
        'grid_withdraw_income': (c.POST, c.GRID_WITHDRAW_INCOME, 'algoId'),
        'grid_compute_margin_balance': (c.POST, c.GRID_COMPUTE_MARGIN_BALANCE, 'algoId type amt'),
        'grid_adjust_margin_balance': (c.POST, c.GRID_MARGIN_BALANCE, 'algoId type amt percent'),
        'grid_ai_param': (c.GET, c.GRID_AI_PARAM, 'algoOrdType instId direction duration'),
        'place_recurring_buy_order': (
            c.POST, c.PLACE_RECURRING_BUY_ORDER, (
                'stgyName recurringList period recurringDay recurringTime timeZone amt investmentCcy tdMode '
                'algoClOrdId tag tradeQuoteCcy')),
        'amend_recurring_buy_order': (c.POST, c.AMEND_RECURRING_BUY_ORDER, 'algoId stgyName'),
        'stop_recurring_buy_order': (c.POST, c.STOP_RECURRING_BUY_ORDER, 'PAYLOAD'),
        'get_recurring_buy_order_list': (c.GET, c.GET_RECURRING_BUY_ORDER_LIST, 'algoId after before limit'),
        'get_recurring_buy_order_history': (c.GET, c.GET_RECURRING_BUY_ORDER_HISTORY, 'algoId after before limit'),
        'get_recurring_buy_order_details': (c.GET, c.GET_RECURRING_BUY_ORDER_DETAILS, 'algoId'),
        'get_recurring_buy_sub_orders': (c.GET, c.GET_RECURRING_BUY_SUB_ORDERS, 'algoId ordId after before limit'),
    },
    MarketAPI: {
        'get_tickers': (c.GET, c.TICKERS_INFO, 'instType uly instFamily'),
        'get_ticker': (c.GET, c.TICKER_INFO, 'instId'),
        'get_index_tickers': (c.GET, c.INDEX_TICKERS, 'quoteCcy instId'),
        'get_orderbook': (c.GET, c.ORDER_BOOKS, 'instId sz'),
        'get_rpi_orderbook': (c.GET, c.MARKET_BOOKS_RPI, 'instId sz'),
        'get_candlesticks': (c.GET, c.MARKET_CANDLES, 'instId after before bar limit'),
        'get_history_candlesticks': (c.GET, c.HISTORY_CANDLES, 'instId after before bar limit'),
        'get_index_candlesticks': (c.GET, c.INDEX_CANDLES, 'instId after before bar limit'),
        'get_mark_price_candlesticks': (c.GET, c.MARKPRICE_CANDLES, 'instId after before bar limit'),
        'get_trades': (c.GET, c.MARKET_TRADES, 'instId limit'),
        'get_volume': (c.GET, c.VOLUME, ''),
        'get_tier': (c.GET, c.TIER, 'instType tdMode uly instId ccy tier'),
        'get_index_components': (c.GET, c.INDEX_COMPONENTS, 'index'),
        'get_exchange_rate': (c.GET, c.EXCHANGE_RATE, ''),
        'get_history_trades': (c.GET, c.HISTORY_TRADES, 'instId type after before limit'),
        'get_block_ticker': (c.GET, c.BLOCK_TICKER, 'instId'),
        'get_block_tickers': (c.GET, c.BLOCK_TICKERS, 'instType uly instFamily'),
        'get_block_trades': (c.GET, c.BLOCK_TRADES, 'instId'),
        'get_option_trades': (c.GET, c.MARKET_OPTION_TRADES, 'instFamily'),
    },
    OkusdAPI: {
        'get_account': (c.GET, c.OKUSD_ACCOUNT, ''),
        'get_rate_history': (c.GET, c.OKUSD_RATE_HISTORY, 'limit begin end'),
        'get_subscribe_history': (c.GET, c.OKUSD_SUBSCRIBE_HISTORY, 'limit begin end'),
        'get_redeem_history': (c.GET, c.OKUSD_REDEEM_HISTORY, 'limit begin end type'),
        'get_rewards_history': (c.GET, c.OKUSD_REWARDS_HISTORY, 'limit begin end'),
    },
    PublicAPI: {
        'get_instruments': (c.GET, c.INSTRUMENT_INFO, 'instType uly instId instFamily'),
        'get_delivery_exercise_history': (c.GET, c.DELIVERY_EXERCISE, 'instType uly after before limit instFamily'),
        'get_open_interest': (c.GET, c.OPEN_INTEREST, 'instType uly instId instFamily'),
        'get_funding_rate': (c.GET, c.FUNDING_RATE, 'instId'),
        'funding_rate_history': (c.GET, c.FUNDING_RATE_HISTORY, 'instId after before limit'),
        'get_price_limit': (c.GET, c.PRICE_LIMIT, 'instId'),
        'get_opt_summary': (c.GET, c.OPT_SUMMARY, 'uly expTime instFamily'),
        'get_estimated_price': (c.GET, c.ESTIMATED_PRICE, 'instId'),
        'discount_interest_free_quota': (c.GET, c.DISCOUNT_INTEREST_INFO, 'ccy'),
        'get_system_time': (c.GET, c.SYSTEM_TIME, ''),
        'get_mark_price': (c.GET, c.MARK_PRICE, 'instType uly instId instFamily'),
        'get_position_tiers': (c.GET, c.TIER, 'instType tdMode uly instId ccy tier instFamily'),
        'get_interest_rate_loan_quota': (c.GET, c.INTEREST_LOAN, ''),
        'get_underlying': (c.GET, c.UNDERLYING, 'instType'),
        'get_insurance_fund': (c.GET, c.INSURANCE_FUND, 'instType type uly ccy before after limit instFamily'),
        'get_convert_contract_coin': (c.GET, c.CONVERT_CONTRACT_COIN, 'type instId sz px unit'),
        'get_option_tickbands': (c.GET, c.GET_OPTION_TICKBANDS, 'instType instFamily'),
        'get_option_trades': (c.GET, c.GET_OPTION_TRADES, 'instId instFamily optType'),
        'get_market_data_history': (
            c.GET, c.MARKET_DATA_HISTORY,
            'module instType dateAggrType begin end instIdList instFamilyList'),
        'get_announcements': (c.GET, c._value, 'annType page'),
    },
    SavingsAPI: {
        'get_saving_balance': (c.GET, c.GET_SAVING_BALANCE, 'ccy'),
        'savings_purchase_redemption': (c.POST, c.SAVING_PURCHASE_REDEMPTION, 'ccy amt side rate'),
        'set_lending_rate': (c.POST, c.SET_LENDING_RATE, 'ccy rate'),
        'get_lending_history': (c.GET, c.GET_LENDING_HISTORY, 'ccy after before limit'),
        'get_public_borrow_history': (c.GET, c.GET_PUBLIC_BORROW_HISTORY, 'ccy after before limit'),
        'get_public_borrow_info': (c.GET, c.GET_PUBLIC_BORROW_INFO, 'ccy'),
    },
    SolStakingAPI: {
        'sol_purchase': (c.POST, c.STACK_SOL_PURCHASE, 'amt'),
        'sol_redeem': (c.POST, c.STACK_SOL_REDEEM, 'amt'),
        'sol_balance': (c.GET, c.STACK_SOL_BALANCE, ''),
        'sol_purchase_redeem_history': (c.GET, c.STACK_SOL_PURCHASE_REDEEM_HISTORY, 'type status after before limit'),
        'sol_apy_history': (c.GET, c.STACK_SOL_APY_HISTORY, 'days'),
        'sol_product_info': (c.GET, c.STACK_SOL_PRODUCT_INFO, ''),
    },
    SpreadTradingAPI: {
        'place_order': (c.POST, c.SPREAD_PLACE_ORDER, 'sprdId clOrdId tag side ordType sz px'),
        'cancel_order': (c.POST, c.SPREAD_CANCEL_ORDER, 'ordId clOrdId'),
        'cancel_all_orders': (c.POST, c.SPREAD_CANCEL_ALL_ORDERS, 'sprdId'),
        'get_order_details': (c.GET, c.SPREAD_PLACE_ORDER, 'ordId clOrdId'),
        'get_active_orders': (c.GET, c.SPREAD_GET_ACTIVE_ORDERS, 'sprdId ordType state beginId endId limit'),
        'get_orders': (c.GET, c.SPREAD_GET_ORDERS, 'sprdId ordType state beginId endId begin end limit'),
        'get_trades': (c.GET, c.SPREAD_GET_TRADES, 'sprdId tradeId ordId beginId endId begin end limit'),
        'get_spreads': (c.GET, c.SPREAD_GET_SPREADS, 'baseCcy instId sprdId state'),
        'get_order_book': (c.GET, c.SPREAD_GET_ORDER_BOOK, 'sprdId sz'),
        'get_ticker': (c.GET, c.SPREAD_GET_TICKER, 'sprdId'),
        'get_public_trades': (c.GET, c.SPREAD_GET_PUBLIC_TRADES, 'sprdId'),
    },
    StakingDefiAPI: {
        'get_offers': (c.GET, c.STACK_DEFI_OFFERS, 'productId protocolType ccy'),
        'purchase': (c.POST, c.STACK_DEFI_PURCHASE, 'productId investData term tag'),
        'redeem': (c.POST, c.STACK_DEFI_REDEEM, 'ordId protocolType allowEarlyRedeem'),
        'cancel': (c.POST, c.STACK_DEFI_CANCEL, 'ordId protocolType'),
        'get_activity_orders': (c.GET, c.STACK_DEFI_ORDERS_ACTIVITY, 'productId protocolType ccy state'),
        'get_orders_history': (c.GET, c.STACK_DEFI_ORDERS_HISTORY, 'productId protocolType ccy after before limit'),
    },
    StatusAPI: {
        'status': (c.GET, c.STATUS, 'state'),
    },
    SubAccountAPI: {
        'get_account_balance': (c.GET, c.BALANCE, 'subAcct'),
        'bills': (c.GET, c.SUBACCOUNT_BILLS, 'ccy type subAcct after before limit'),
        'reset_subaccount_apikey': (c.POST, c.RESET, 'subAcct apiKey label perm ip'),
        'get_subaccount_list': (c.GET, c.VIEW_LIST, 'enable subAcct after before limit'),
        'subaccount_transfer': (
            c.POST, c.SUBACCOUNT_TRANSFER,
            'ccy amt from to fromSubAccount toSubAccount loanTrans omitPosRisk'),
        'get_entrust_subaccount_list': (c.GET, c.ENTRUST_SUBACCOUNT_LIST, 'subAcct'),
        'set_permission_transfer_out': (c.POST, c.SET_TRANSFER_OUT, 'subAcct canTransOut'),
        'get_funding_balance': (c.GET, c.GET_ASSET_SUBACCOUNT_BALANCE, 'subAcct ccy'),
        'set_sub_accounts_vip_loan': (c.POST, c.SET_SUB_ACCOUNTS_VIP_LOAN, 'enable alloc'),
        'get_sub_account_borrow_interest_and_limit': (
            c.GET, c.GET_SUB_ACCOUNT_BORROW_INTEREST_AND_LIMIT,
            'subAcct ccy'),
    },
    TradeAPI: {
        'place_order': (
            c.POST, c.PLACE_ORDER, (
                'instId tdMode side ordType sz ccy clOrdId tag posSide px reduceOnly tgtCcy stpMode pxUsd pxVol '
                'banAmend tradeQuoteCcy pxAmendType isElpTakerAccess instIdCode attachAlgoOrds')),
        'place_multiple_orders': (c.POST, c.BATCH_ORDERS, 'PAYLOAD'),
        'cancel_order': (c.POST, c.CANCEL_ORDER, 'instId ordId clOrdId'),
        'cancel_multiple_orders': (c.POST, c.CANCEL_BATCH_ORDERS, 'PAYLOAD'),
        'amend_order': (
            c.POST, c.AMEND_ORDER, (
                'instId cxlOnFail ordId clOrdId reqId newSz newPx newTpTriggerPx newTpOrdPx newSlTriggerPx '
                'newSlOrdPx newTpTriggerPxType newSlTriggerPxType newTriggerPx newOrdPx pxAmendType '
                'newTpTriggerRatio newSlTriggerRatio attachAlgoOrds')),
        'amend_multiple_orders': (c.POST, c.AMEND_BATCH_ORDER, 'PAYLOAD'),
        'close_positions': (c.POST, c.CLOSE_POSITION, 'instId mgnMode posSide ccy autoCxl clOrdId tag'),
        'get_order': (c.GET, c.PLACE_ORDER, 'instId ordId clOrdId'),
        'get_order_list': (c.GET, c.ORDERS_PENDING, 'instType uly instId ordType state after before limit instFamily'),
        'get_orders_history': (
            c.GET, c.ORDERS_HISTORY,
            'instType uly instId ordType state after before begin end limit instFamily'),
        'get_orders_history_archive': (
            c.GET, c.ORDERS_HISTORY_ARCHIVE,
            'instType uly instId ordType state after before begin end limit instFamily'),
        'get_fills': (c.GET, c.ORDER_FILLS, 'instType uly instId ordId after before limit instFamily begin end'),
        'place_algo_order': (
            c.POST, c.PLACE_ALGO_ORDER, (
                'instId tdMode side ordType sz ccy posSide reduceOnly tpTriggerPx tpOrdPx slTriggerPx slOrdPx '
                'triggerPx orderPx tgtCcy pxVar szLimit pxLimit timeInterval pxSpread tpTriggerPxType '
                'slTriggerPxType callbackRatio callbackSpread activePx tag triggerPxType closeFraction '
                'quickMgnType algoClOrdId tpOrdKind cxlOnClosePos chaseType chaseVal maxChaseType maxChaseVal '
                'attachAlgoOrds tradeQuoteCcy pxAmendType advanceOrdType tpTriggerRatio slTriggerRatio')),
        'cancel_algo_order': (c.POST, c.CANCEL_ALGOS, 'PAYLOAD'),
        'order_algos_list': (c.GET, c.ORDERS_ALGO_PENDING, 'ordType algoId instType instId after before limit'),
        'order_algos_history': (
            c.GET, c.ORDERS_ALGO_HISTORY,
            'ordType state algoId instType instId after before limit'),
        'get_fills_history': (c.GET, c.ORDERS_FILLS_HISTORY, 'instType uly instId ordId after before limit instFamily'),
        'get_easy_convert_currency_list': (c.GET, c.EASY_CONVERT_CURRENCY_LIST, ''),
        'easy_convert': (c.POST, c.EASY_CONVERT, 'fromCcy toCcy'),
        'get_easy_convert_history': (c.GET, c.CONVERT_EASY_HISTORY, 'before after limit'),
        'get_oneclick_repay_list': (c.GET, c.ONE_CLICK_REPAY_SUPPORT, 'debtType'),
        'oneclick_repay': (c.POST, c.ONE_CLICK_REPAY, 'debtCcy repayCcy'),
        'oneclick_repay_history': (c.GET, c.ONE_CLICK_REPAY_HISTORY, 'after before limit'),
        'get_algo_order_details': (c.GET, c.PLACE_ALGO_ORDER, 'algoId algoClOrdId'),
        'amend_algo_order': (
            c.POST, c.AMEND_ALGO_ORDER, (
                'instId algoId algoClOrdId cxlOnFail reqId newSz newTriggerPx newOrdPx newTpTriggerPx newTpOrdPx '
                'newSlTriggerPx newSlOrdPx newTpTriggerPxType newSlTriggerPxType')),
        'get_oneclick_repay_list_v2': (c.GET, c.ONE_CLICK_REPAY_SUPPORT_V2, ''),
        'oneclick_repay_v2': (c.POST, c.ONE_CLICK_REPAY_V2, 'debtCcy repayCcyList'),
        'oneclick_repay_history_v2': (c.GET, c.ONE_CLICK_REPAY_HISTORY_V2, 'after before limit'),
    },
    TradingDataAPI: {
        'get_support_coin': (c.GET, c.SUPPORT_COIN, ''),
        'get_taker_volume': (c.GET, c.TAKER_VOLUME, 'ccy instType begin end period'),
        'get_margin_lending_ratio': (c.GET, c.MARGIN_LENDING_RATIO, 'ccy begin end period'),
        'get_long_short_ratio': (c.GET, c.LONG_SHORT_RATIO, 'ccy begin end period'),
        'get_contracts_interest_volume': (c.GET, c.CONTRACTS_INTEREST_VOLUME, 'ccy begin end period'),
        'get_options_interest_volume': (c.GET, c.OPTIONS_INTEREST_VOLUME, 'ccy period'),
        'get_put_call_ratio': (c.GET, c.PUT_CALL_RATIO, 'ccy period'),
        'get_interest_volume_expiry': (c.GET, c.OPEN_INTEREST_VOLUME_EXPIRY, 'ccy period'),
        'get_interest_volume_strike': (c.GET, c.INTEREST_VOLUME_STRIKE, 'ccy expTime period'),
        'get_taker_block_volume': (c.GET, c.TAKER_FLOW, 'ccy period'),
        'get_open_interest_history': (c.GET, c.CONTRACTS_OPEN_INTEREST_HISTORY, 'instId period begin end limit'),
    },
}

# Methods whose collection parameters are required: the default lives in the
# signature as `[]`, so calling the method without arguments still sends the
# key. One row per method, listing the request keys that must be [].
DEFAULTED_COLLECTIONS = [
    (AccountAPI, 'get_simulated_margin', ('simPos',)),
    (BlockTradingAPI, 'create_rfq', ('counterparties', 'legs')),
    (BlockTradingAPI, 'cancel_batch_rfqs', ('rfqIds', 'clRfqIds')),
    (BlockTradingAPI, 'execute_quote', ('legs',)),
    (BlockTradingAPI, 'create_quote', ('legs',)),
    (TradeAPI, 'easy_convert', ('fromCcy',)),
    (TradeAPI, 'oneclick_repay', ('debtCcy',)),
    (TradeAPI, 'oneclick_repay_v2', ('repayCcyList',)),
    (GridAPI, 'place_recurring_buy_order', ('recurringList',)),
    (SubAccountAPI, 'set_sub_accounts_vip_loan', ('alloc',)),
    (FlexibleLoanAPI, 'max_loan', ('supCollateral',)),
    (StakingDefiAPI, 'purchase', ('investData',)),
]
