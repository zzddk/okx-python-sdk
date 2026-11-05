"""
Unit tests for the login handshake.

The handshake is exercised without a session: frames go in through `feed()`,
and the outcome comes out of `wait()`.

Mirrors: okx/websocket/login.py
"""
import asyncio
import json
import time
import unittest

from okx.websocket.login import LoginHandshake, login_payload

ACK = '{"event": "login", "code": "0"}'
REJECTED = '{"event": "login", "code": "60009", "msg": "Login failed"}'
DATA = '{"arg": {"channel": "tickers", "instId": "BTC-USDT"}, "data": []}'


def _parse(message):
    try:
        return json.loads(message)
    except ValueError:
        return None


class TestLoginPayload(unittest.TestCase):
    def test_payload_matches_the_bytes_0_14_1_sent(self):
        payload = login_payload("key", "pass", "secret", timestamp=1700000000)
        self.assertEqual(
            payload,
            '{"op": "login", "args": [{"apiKey": "key", "passphrase": "pass", '
            '"timestamp": 1700000000, "sign": '
            '"lhmJXK08fk9SI1ZwFXKFRrPtzfbNOwC+D1xMJJ/1KZg="}]}',
        )

    def test_timestamp_defaults_to_the_local_clock_in_whole_seconds(self):
        before = int(time.time())
        payload = json.loads(login_payload("key", "pass", "secret"))
        after = int(time.time())
        stamp = payload["args"][0]["timestamp"]
        self.assertIsInstance(stamp, int)
        self.assertGreaterEqual(stamp, before)
        self.assertLessEqual(stamp, after)


class TestFeedAndWait(unittest.TestCase):
    def test_accepting_answer_completes_the_wait(self):
        async def run():
            handshake = LoginHandshake(timeout=1)
            self.assertTrue(handshake.feed(_parse(ACK)))
            await handshake.wait()

        asyncio.run(run())

    def test_rejection_raises_with_the_server_code_and_message(self):
        async def run():
            handshake = LoginHandshake(timeout=1)
            handshake.feed(_parse(REJECTED))
            with self.assertRaises(ConnectionError) as caught:
                await handshake.wait()
            self.assertIn("60009", str(caught.exception))
            self.assertIn("Login failed", str(caught.exception))

        asyncio.run(run())

    def test_data_frames_are_left_to_the_caller(self):
        async def run():
            handshake = LoginHandshake(timeout=0.01)
            self.assertFalse(handshake.feed(_parse(DATA)))
            with self.assertRaises(TimeoutError) as caught:
                await handshake.wait()
            self.assertIn("no login acknowledgement", str(caught.exception))

        asyncio.run(run())

    def test_only_the_first_answer_counts(self):
        async def run():
            handshake = LoginHandshake(timeout=1)
            handshake.feed(_parse(REJECTED))
            handshake.feed(_parse(ACK))
            with self.assertRaises(ConnectionError):
                await handshake.wait()

        asyncio.run(run())
