"""
Unit tests for the WebSocket login correctness fixes

Mirrors: okx/websocket/login.py, Ws*Async.login
"""
import asyncio
import unittest

from okx.websocket.WsPrivateAsync import WsPrivateAsync
from okx.websocket.WsPublicAsync import WsPublicAsync

from .fakes import FakeConnector, FakeSocket

URL = 'wss://example.com'
ACK = '{"event":"login","code":"0"}'
REJECT = '{"event":"login","code":"60009","msg":"Login failed"}'
CREDS = {'apiKey': 'k', 'passphrase': 'p', 'secretKey': 's'}


def _public_on(answer_login=None, *frames):
    sock = FakeSocket(*frames, answer_login=answer_login)
    return WsPublicAsync(url=URL, connector=FakeConnector(sock), **CREDS), sock


def _private_on(answer_login=None, *frames):
    sock = FakeSocket(*frames, answer_login=answer_login)
    return WsPrivateAsync(url=URL, connector=FakeConnector(sock), **CREDS), sock


class TestLoginAck(unittest.TestCase):
    def test_public_login_succeeds_on_ack(self):
        async def run():
            ws, sock = _public_on(ACK)
            await ws.start()
            result = await ws.login()
            logged_in = ws.isLoggedIn
            await ws.stop()
            return result, logged_in

        self.assertEqual(asyncio.run(run()), (True, True))

    def test_public_login_raises_on_rejection(self):
        async def run():
            ws, sock = _public_on(REJECT)
            await ws.start()
            try:
                await ws.login()
            finally:
                await ws.stop()

        with self.assertRaises(ConnectionError) as ctx:
            asyncio.run(run())
        self.assertIn('60009', str(ctx.exception))

    def test_private_login_raises_on_rejection(self):
        async def run():
            ws, sock = _private_on(REJECT)
            await ws.start()

        with self.assertRaises(ConnectionError):
            asyncio.run(run())

    def test_login_times_out_without_an_ack(self):
        async def run():
            ws, sock = _public_on()
            await ws.start()
            try:
                await ws.login(timeout=0.05)
            finally:
                await ws.stop()

        with self.assertRaises(TimeoutError):
            asyncio.run(run())

    def test_non_login_frames_reach_the_callback(self):
        received = []

        async def run():
            ws, sock = _public_on(ACK, '{"event":"notice"}')
            ws.callback = received.append
            await ws.start()
            await ws.login()
            await ws.stop()

        asyncio.run(run())
        self.assertEqual(received, ['{"event":"notice"}'])

    def test_private_subscribe_does_not_sleep_after_the_ack(self):
        async def run():
            ws, sock = _private_on(ACK)
            await ws.start()
            await ws.subscribe([{'channel': 'account'}])
            await ws.stop()
            return [p['op'] for p in sock.payloads]

        self.assertEqual(asyncio.run(run()), ['login', 'subscribe'])


if __name__ == '__main__':
    unittest.main()
