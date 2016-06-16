# -*- coding: utf-8 -*-
import json
import os, binascii
import asyncio
from app import app
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestClient

from configs.db import DB

os.environ['IS_TEST'] = 'True'

email = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
password = binascii.b2a_hex(os.urandom(15)).decode("utf-8")


class TestClientApi(AioHTTPTestCase):
    data = {}

    def setUp(self):
        self.database = DB()
        self.loop = asyncio.new_event_loop()

        self.data = {
            'email': email,
            'password': password
        }

        self.app = self.get_app(
            self.loop
        )

        self.client = TestClient(self.app)

    def get_app(self, loop):
        server = app(loop=loop)

        server['db'] = self.database.hold_connect(
            loop=loop
        )

        return server

    @unittest_run_loop
    async def test_a_join_client(self):
        print("test_join_client")

        data = json.dumps(self.data)
        request = await self.client.post(
            path="/client/create/",
            data=data
        )

        content = await request.json()
        return content

    @unittest_run_loop
    async def test_b_auth_client(self):
        print("test_auth_client")
        data = json.dumps(self.data)
        request = await self.client.post(
            path="/client/auth/",
            data=data
        )
        content = await request.json()
        return content

    @unittest_run_loop
    async def test_с_join_client_again(self):
        print("test_auth_with_exist_data")

        data = json.dumps(self.data)
        request = await self.client.post(
            path="/client/create/",
            data=data
        )

        content = await request.json()
        return content

    @unittest_run_loop
    async def test_d_delete_client(self):
        print("test_delete_client")
        data = json.dumps(self.data)
        auth_request = await self.client.post(
            path="/client/auth/",
            data=data
        )

        content = await auth_request.json()

        data = json.dumps({
            'id': content.get('client_id')
        })

        delete_request = await self.client.post(
            path="/client/delete/",
            data=data
        )
