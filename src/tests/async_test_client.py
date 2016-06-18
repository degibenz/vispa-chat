# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import os
import json
import asyncio

from app import app
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestClient

from configs.db import DB

os.environ['IS_TEST'] = 'True'


class TestClientApi(AioHTTPTestCase):
    data = {}

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

        self.client = TestClient(self.app)

    def load_data(self):
        with open('fixtures.json') as data:
            self.data = json.load(data)

    @unittest_run_loop
    async def test_a_join_client(self):
        print("========================")
        print("test_join_client")

        data = json.dumps(self.data)
        request = await self.client.post(
            path="/client/create/",
            data=data
        )

        content = await request.json()

        error_exist = content.get('error', None)

        if not error_exist:
            assert content.get('status') is True
            assert content.get('client_id') is not None
        else:
            assert content.get('status') is False

    @unittest_run_loop
    async def test_b_auth_client(self):
        print("========================")
        print("test_auth_client")

        data = json.dumps(self.data)

        request = await self.client.post(
            path="/client/auth/",
            data=data
        )
        content = await request.json()

        assert content.get('status') is True

    @unittest_run_loop
    async def test_с_join_client_again(self):
        print("========================")
        print("test_auth_with_exist_data")

        data = json.dumps(self.data)
        request = await self.client.post(
            path="/client/create/",
            data=data
        )

        content = await request.json()
        assert content.get('status') is True

    @unittest_run_loop
    async def test_d_delete_client(self):
        print("========================")
        print("test_delete_client")
        data = json.dumps(self.data)
        auth_request = await self.client.post(
            path="/client/auth/",
            data=data
        )

        auth_content = await auth_request.json()

        data = json.dumps({
            'id': auth_content.get('client_id')
        })

        delete_request = await self.client.post(
            path="/client/delete/",
            data=data
        )
        delete_content = await delete_request.json()

        assert delete_content.get('status') is True

    @unittest_run_loop
    async def test_f_auth_client_after_delete_account(self):
        print("========================")
        print("test_f_auth_client_after_delete_account")
        data = json.dumps(self.data)
        request = await self.client.post(
            path="/client/auth/",
            data=data
        )
        content = await request.json()

        assert content.get('status') is False
