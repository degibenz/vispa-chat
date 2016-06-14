# -*- coding: utf-8 -*-
import json
import os, binascii
from app import app
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop


class TestClientApi(AioHTTPTestCase):
    data = {}
    email = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    password = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    def setUp(self):
        self.data = {
            'email': self.email,
            'password': self.password
        }

        super(TestClientApi, self).setUp()

    def get_app(self, loop):
        return app(loop=loop)

    @unittest_run_loop
    async def test_join_client(self):
        data = json.dumps(self.data)

        request = await self.client.post(
            path="/client/create/",
            data=data
        )

        return await request.json()

    @unittest_run_loop
    async def test_auth_client(self):
        data = json.dumps(self.data)

        request = await self.client.post(
            path="/client/auth/",
            data=data
        )
        return await request.json()

    @unittest_run_loop
    async def test_join_client_again(self):
        result = await self.test_auth_client()

    @unittest_run_loop
    async def test_delete_client(self):
        client_id = await self.test_auth_client()
        data = json.dumps({
            'id': client_id
        })

        request = await self.client.post(
            path="/client/delete/",
            data=data
        )
