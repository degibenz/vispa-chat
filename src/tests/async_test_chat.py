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

        server['db'] = self.database.hold_connect(
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
    async def test_create_chat_without_token(self):
        request = await self.client.post(
            path='/chat/create/',
        )

        result = await request.json()
        assert result.get('status') is False

    @unittest_run_loop
    async def test_receive_chat_list(self):
        request = await self.client.get(
            path='/chat/list/',
            headers=self.headers
        )

        result = await request.json()
        assert result.get('status') is True

    @unittest_run_loop
    async def test_create_and_delete_chat(self):
        create_chat_request = await self.client.post(
            path='/chat/create/',
            headers=self.headers
        )

        chat_info = await create_chat_request.json()

        assert chat_info.get('status') is True

        data = {
            'id': chat_info.get('chat')
        }

        delete_chat_request = await self.client.post(
            path='/chat/delete/',
            headers=self.headers,
            data=json.dumps(data)
        )

        result = await delete_chat_request.json()

        assert result.get('status') is True

    @unittest_run_loop
    async def test_delete_chat_with_not_correct_pk(self):

        data = json.dumps({
            'id': '57652fa9f4e00b15bcd17f7d'
        })

        request = await self.client.post(
            path='/chat/delete/',
            headers=self.headers,
            data=data
        )

        result = await request.json()
        assert result.get('status') is False
