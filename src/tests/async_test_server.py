# -*- coding: utf-8 -*-

from app import app
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop


class TestServerApp(AioHTTPTestCase):
    def get_app(self, loop):
        server = app(loop=loop)

        return server

    @unittest_run_loop
    async def test_server_loop(self):
        assert self.app.loop is self.loop

    @unittest_run_loop
    async def test_server_is_closed(self):
        assert self.client._closed is False

