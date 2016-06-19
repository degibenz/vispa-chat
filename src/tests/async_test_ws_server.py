# -*- coding: utf-8 -*-
import os
import json
import asyncio

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestClient

from app import app
from configs.db import DB

os.environ['IS_TEST'] = 'True'


class TestChatApi(AioHTTPTestCase):
    data = {}
    headers = {}
    token = None

    client_in_request = None

    def get_app(self, loop):
        server = app(loop=loop)

        server['db'] = self.database(
            loop=loop
        )

        return server

    def setUp(self):
        self.load_data()

        self.database = DB()
        self.loop = asyncio.new_event_loop()

        self.app = self.get_app(
            self.loop
        )

        self.client = TestClient(
            self.app
        )

        self.loop.run_until_complete(self.install_client())

        self.loop.run_until_complete(self.auth_client())

        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }

    def load_data(self):
        with open('fixtures.json') as data:
            self.data = json.load(data)

    def install_client(self):
        data = json.dumps(self.data)
        request = yield from self.client.post(
            path="/client/create/",
            data=data
        )

        self.client_in_request = yield from request.json()

    def auth_client(self):
        data = json.dumps(self.data)
        request = yield from self.client.post(
            path="/client/auth/",
            data=data
        )

        auth_data = yield from request.json()
        self.token = auth_data.get('token')

    @unittest_run_loop
    async def test_open_ws_connect(self):
        pass

    @unittest_run_loop
    async def test_close_ws_connect(self):
        pass

    @unittest_run_loop
    async def test_send_message_to_chat(self):
        pass

    @unittest_run_loop
    async def test_send_message_to_myself(self):
        pass

    @unittest_run_loop
    async def test_send_private_message(self):
        pass
