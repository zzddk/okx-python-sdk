from okx.okxclient import OkxClient
from okx.consts import (
    GET,
    _NO_CREDENTIAL,
    AFFILIATE_TVB_INVITEE_DETAIL,
    AFFILIATE_TVB_INVITEE_LIST,
    AFFILIATE_TVB_LINK_LIST,
    AFFILIATE_TVB_PERFORMANCE_SUMMARY,
    AFFILIATE_TVB_TIER_BREAKDOWN,
)


class AffiliateAPI(OkxClient):
    def get_tvb_invitee_detail(self, uid):
        params = {'uid': uid}
        return self._request_with_params(GET, AFFILIATE_TVB_INVITEE_DETAIL, params)

    def get_tvb_invitee_list(self, periodType = None, begin = None, end = None, feeTier = None, tradeType = None,
                             keyword = None, orderBy = None, orderDir = None, page = None, limit = None):
        params = {}
        if periodType is not None:
            params['periodType'] = periodType
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        if feeTier is not None:
            params['feeTier'] = feeTier
        if tradeType is not None:
            params['tradeType'] = tradeType
        if keyword is not None:
            params['keyword'] = keyword
        if orderBy is not None:
            params['orderBy'] = orderBy
        if orderDir is not None:
            params['orderDir'] = orderDir
        if page is not None:
            params['page'] = page
        if limit is not None:
            params['limit'] = limit
        return self._request_with_params(GET, AFFILIATE_TVB_INVITEE_LIST, params)

    def get_tvb_link_list(self, periodType = None, begin = None, end = None, page = None, limit = None,
                          linkType = None, linkStatus = None):
        params = {}
        if periodType is not None:
            params['periodType'] = periodType
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        if page is not None:
            params['page'] = page
        if limit is not None:
            params['limit'] = limit
        if linkType is not None:
            params['linkType'] = linkType
        if linkStatus is not None:
            params['linkStatus'] = linkStatus
        return self._request_with_params(GET, AFFILIATE_TVB_LINK_LIST, params)

    def get_tvb_performance_summary(self, periodType = None, begin = None, end = None):
        params = {}
        if periodType is not None:
            params['periodType'] = periodType
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self._request_with_params(GET, AFFILIATE_TVB_PERFORMANCE_SUMMARY, params)

    def get_tvb_tier_breakdown(self, periodType = None, begin = None, end = None):
        params = {}
        if periodType is not None:
            params['periodType'] = periodType
        if begin is not None:
            params['begin'] = begin
        if end is not None:
            params['end'] = end
        return self._request_with_params(GET, AFFILIATE_TVB_TIER_BREAKDOWN, params)
