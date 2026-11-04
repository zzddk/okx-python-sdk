"""
Unit tests for okx.pagination and OkxClient.paginate

Mirrors the structure: okx/pagination.py -> test/unit/okx/test_pagination.py
"""
import unittest
from unittest.mock import MagicMock, patch

from okx import pagination
from okx.okxclient import OkxClient

MOCK_CLIENT_INIT = 'okx.okxclient.Client.__init__'


def _page(*ids):
    return {'code': '0', 'data': [{'billId': str(i)} for i in ids]}


class TestPaginateWalk(unittest.TestCase):
    def test_walks_until_an_empty_page(self):
        fetch = MagicMock(side_effect=[_page(3, 2), _page(1), _page()])
        records = list(pagination.paginate(fetch, cursor='billId', page_size=2))
        self.assertEqual([r['billId'] for r in records], ['3', '2', '1'])
        self.assertEqual(fetch.call_count, 3)

    def test_next_page_uses_the_last_cursor(self):
        fetch = MagicMock(side_effect=[_page(9, 8), _page()])
        list(pagination.paginate(fetch, cursor='billId', page_size=2))
        self.assertEqual(fetch.call_args_list[1].kwargs['after'], '8')

    def test_first_call_has_no_after(self):
        fetch = MagicMock(return_value=_page())
        list(pagination.paginate(fetch, cursor='billId'))
        self.assertNotIn('after', fetch.call_args.kwargs)

    def test_short_page_does_not_stop_the_walk(self):
        """The endpoint caps limit at its own maximum; a short page proves nothing."""
        fetch = MagicMock(side_effect=[_page(5), _page(4), _page()])
        records = list(pagination.paginate(fetch, cursor='billId', page_size=100))
        self.assertEqual(len(records), 2)
        self.assertEqual(fetch.call_count, 3)

    def test_stops_when_the_cursor_stops_advancing(self):
        """A server that ignores `after` would otherwise loop forever."""
        fetch = MagicMock(side_effect=[_page(7), _page(7), _page(7)])
        records = list(pagination.paginate(fetch, cursor='billId', page_size=1))
        self.assertEqual(len(records), 2)
        self.assertEqual(fetch.call_count, 2)

    def test_stops_when_the_cursor_field_is_missing(self):
        """The page is still yielded; only the walk stops."""
        fetch = MagicMock(return_value={'code': '0', 'data': [{'other': 'x'}]})
        records = list(pagination.paginate(fetch, cursor='billId'))
        self.assertEqual(len(records), 1)
        self.assertEqual(fetch.call_count, 1)

    def test_max_pages_limits_the_walk(self):
        fetch = MagicMock(return_value=_page(3, 2))
        records = list(pagination.paginate(fetch, cursor='billId', page_size=2, max_pages=2))
        self.assertEqual(len(records), 4)
        self.assertEqual(fetch.call_count, 2)

    def test_filters_are_sent_on_every_page(self):
        fetch = MagicMock(side_effect=[_page(3, 2), _page()])
        list(pagination.paginate(fetch, cursor='billId', params={'begin': '1', 'end': '2'}))
        for call in fetch.call_args_list:
            self.assertEqual(call.kwargs['begin'], '1')
            self.assertEqual(call.kwargs['end'], '2')

    def test_page_size_becomes_limit(self):
        fetch = MagicMock(return_value=_page())
        list(pagination.paginate(fetch, cursor='billId', page_size=50))
        self.assertEqual(fetch.call_args.kwargs['limit'], 50)

    def test_resumes_from_a_supplied_cursor(self):
        fetch = MagicMock(return_value=_page())
        list(pagination.paginate(fetch, cursor='billId', params={'after': '42'}))
        self.assertEqual(fetch.call_args.kwargs['after'], '42')

    def test_empty_result_yields_nothing(self):
        fetch = MagicMock(return_value={'code': '0', 'data': []})
        self.assertEqual(list(pagination.paginate(fetch, cursor='billId')), [])

    def test_missing_cursor_is_rejected(self):
        fetch = MagicMock()
        with self.assertRaises(ValueError):
            list(pagination.paginate(fetch, cursor=''))
        fetch.assert_not_called()


class TestClientPaginate(unittest.TestCase):
    def _client(self):
        with patch(MOCK_CLIENT_INIT):
            return OkxClient()

    def test_missing_cursor_fails_at_the_call_site(self):
        client = self._client()
        client.get_bills = MagicMock()
        with self.assertRaises(ValueError):
            client.paginate(client.get_bills)

    def test_page_number_endpoints_get_a_specific_message(self):
        client = self._client()

        def get_announcements(page=None):
            return {'code': '0', 'data': []}

        with self.assertRaises(ValueError) as ctx:
            client.paginate(get_announcements)
        self.assertIn('page', str(ctx.exception))

    def test_iterates_through_the_client(self):
        client = self._client()
        client.get_bills = MagicMock(side_effect=[_page(2, 1), _page()])
        records = list(client.paginate(client.get_bills, cursor='billId', page_size=2))
        self.assertEqual([r['billId'] for r in records], ['2', '1'])

    def test_pagination_goes_through_the_retry_layer(self):
        """Each page is a normal _request call, so retries and limits apply."""
        client = self._client()
        with patch.object(client, '_request', return_value=_page()) as request:
            list(client.paginate(lambda **kw: client._request('GET', '/x', kw), cursor='billId'))
        self.assertTrue(request.called)
