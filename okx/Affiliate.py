from typing import Any, Dict

from okx.okxclient import OkxClient
from okx.consts import (
    GET,
    AFFILIATE_TVB_INVITEE_DETAIL,
    AFFILIATE_TVB_INVITEE_LIST,
    AFFILIATE_TVB_LINK_LIST,
    AFFILIATE_TVB_PERFORMANCE_SUMMARY,
    AFFILIATE_TVB_TIER_BREAKDOWN,
)


class AffiliateAPI(OkxClient):
    def get_tvb_invitee_detail(self, uid: Any) -> Dict[str, Any]:
        params = {'uid': uid}
        return self.request(GET, AFFILIATE_TVB_INVITEE_DETAIL, params)

    def get_tvb_invitee_list(self, periodType: Any = None, begin: Any = None, end: Any = None, feeTier: Any = None, tradeType: Any = None,
                             keyword: Any = None, orderBy: Any = None, orderDir: Any = None, page: Any = None, limit: Any = None) -> Dict[str, Any]:
        params = {'periodType': periodType, 'begin': begin, 'end': end, 'feeTier': feeTier, 'tradeType': tradeType,
                  'keyword': keyword, 'orderBy': orderBy, 'orderDir': orderDir, 'page': page, 'limit': limit}
        return self.request(GET, AFFILIATE_TVB_INVITEE_LIST, params)

    def get_tvb_link_list(self, periodType: Any = None, begin: Any = None, end: Any = None, page: Any = None, limit: Any = None,
                          linkType: Any = None, linkStatus: Any = None) -> Dict[str, Any]:
        params = {'periodType': periodType, 'begin': begin, 'end': end, 'page': page, 'limit': limit,
                  'linkType': linkType, 'linkStatus': linkStatus}
        return self.request(GET, AFFILIATE_TVB_LINK_LIST, params)

    def get_tvb_performance_summary(self, periodType: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'periodType': periodType, 'begin': begin, 'end': end}
        return self.request(GET, AFFILIATE_TVB_PERFORMANCE_SUMMARY, params)

    def get_tvb_tier_breakdown(self, periodType: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'periodType': periodType, 'begin': begin, 'end': end}
        return self.request(GET, AFFILIATE_TVB_TIER_BREAKDOWN, params)
