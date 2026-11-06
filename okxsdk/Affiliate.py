from typing import Any, Dict

from okxsdk.okxclient import OkxClient
from okxsdk.consts import (
    GET,
    AFFILIATE_INVITEE_DETAIL,
    AFFILIATE_INVITEE_LIST,
    AFFILIATE_LINK_LIST,
    AFFILIATE_PERFORMANCE_SUMMARY,
    AFFILIATE_TVB_TIER_BREAKDOWN,
)


class AffiliateAPI(OkxClient):
    def get_invitee_detail(self, uid: Any, periodType: Any = None) -> Dict[str, Any]:
        params = {'uid': uid, 'periodType': periodType}
        return self.request(GET, AFFILIATE_INVITEE_DETAIL, params)

    def get_invitee_list(self, page: Any = None, limit: Any = None, periodType: Any = None,
                         begin: Any = None, end: Any = None, keyword: Any = None,
                         commissionCategory: Any = None, orderBy: Any = None, orderDir: Any = None,
                         kycStatus: Any = None, subAffiliateUid: Any = None, uid: Any = None) -> Dict[str, Any]:
        params = {'page': page, 'limit': limit, 'periodType': periodType, 'begin': begin, 'end': end,
                  'keyword': keyword, 'commissionCategory': commissionCategory, 'orderBy': orderBy,
                  'orderDir': orderDir, 'kycStatus': kycStatus, 'subAffiliateUid': subAffiliateUid,
                  'uid': uid}
        return self.request(GET, AFFILIATE_INVITEE_LIST, params)

    def get_link_list(self, page: Any = None, limit: Any = None, linkType: Any = None,
                      linkStatus: Any = None) -> Dict[str, Any]:
        params = {'page': page, 'limit': limit, 'linkType': linkType, 'linkStatus': linkStatus}
        return self.request(GET, AFFILIATE_LINK_LIST, params)

    def get_performance_summary(self, periodType: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'periodType': periodType, 'begin': begin, 'end': end}
        return self.request(GET, AFFILIATE_PERFORMANCE_SUMMARY, params)

    def get_tvb_tier_breakdown(self, periodType: Any = None, begin: Any = None, end: Any = None) -> Dict[str, Any]:
        params = {'periodType': periodType, 'begin': begin, 'end': end}
        return self.request(GET, AFFILIATE_TVB_TIER_BREAKDOWN, params)
