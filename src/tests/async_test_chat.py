# -*- coding: utf-8 -*-
import json
import os, binascii
import asyncio
from app import app
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestClient

from configs.db import DB

os.environ['IS_TEST'] = 'True'


class TestChatApi(AioHTTPTestCase):
    data = {}
    headers = {}
    token = None

    client_in_request = None

    def get_app(self, loop):
        server = app(loop=loop)

        server['db'] = self.database.hold_connect(
            loop=loop
        )

        return server

    def setUp(self):
        self.database = DB()
        self.loop = asyncio.new_event_loop()

        self.data = {
            'email': '5762cab8f4e00bad310d44ae@gmail.com',
            'password': 'bd31d44ae'
        }

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

        print(self.token)

    @unittest_run_loop
    async def test_create_chat(self):
        request = await self.client.post(
            path='/chat/create/',
            headers=self.headers
        )

        result = await request.text()

        print(result)
