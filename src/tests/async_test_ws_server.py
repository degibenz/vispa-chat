# -*- coding: utf-8 -*-
import datetime
import os
import json
import asyncio
import string
import random
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestClient

from app import app

from configs.db import DB

os.environ['IS_TEST'] = 'True'
os.environ['MONGODB_DB_NAME'] = 'async_chat_test'


class TestChatApi(AioHTTPTestCase):
    data = {}
    headers = {}

    first_headers = None
    second_headers = None

    first_token = None
    second_token = None

    first_client = {}
    second_client = {}

    client_in_request = None

    def get_app(self, loop):
        server = app(
            loop=loop
        )

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
            self.app,
        )

        self.loop.run_until_complete(self.install_client())

        self.loop.run_until_complete(self.auth_client())

        self.first_headers = {
            'Authorization': self.first_token,
            'Content-Type': 'application/json',
        }

        self.second_headers = {
            'Authorization': self.second_token,
            'Content-Type': 'application/json',
        }

        self.loop.run_until_complete(self.install_chat())

    def load_data(self):
        with open('ws_chat_fixtures.json') as data:
            self.data = json.load(data)

    def install_client(self):
        #   Grab data for create users
        first_client = self.data.get('clients').get('first')
        second_client = self.data.get('clients').get('second')

        #   Create request for create first client
        first_client_auth_request = yield from self.client.post(
            path="/client/create/",
            data=json.dumps(first_client)
        )

        # Create request for create second client
        second_client_auth_request = yield from self.client.post(
            path="/client/create/",
            data=json.dumps(second_client)
        )

        yield

    def auth_client(self):
        first_client = self.data.get('clients').get('first')
        second_client = self.data.get('clients').get('second')

        #   auth  and get token for first client
        first_client_request = yield from self.client.post(
            path="/client/auth/",
            data=json.dumps(first_client)
        )

        self.first_client = yield from first_client_request.json()
        self.first_token = self.first_client.get('token')

        #   auth  and get token for second client
        second_client_request = yield from self.client.post(
            path="/client/auth/",
            data=json.dumps(second_client)
        )

        self.second_client = yield from second_client_request.json()

        self.second_token = self.second_client.get('token')

    def install_chat(self):
        request = yield from self.client.post(
            path='/chat/create/',
            headers=self.first_headers
        )

        result = yield from request.json()
        os.environ['TEST_CHAT_PK'] = result.get('chat')

    def delete_test_chat(self):
        chat = os.environ['TEST_CHAT_PK']

        data = json.dumps({
            'id': chat
        })

        request = yield from self.client.post(
            path='/chat/delete/',
            headers=self.first_headers,
            data=data
        )

        result = yield from request.json()

    def tearDown(self):
        self.delete_test_chat()
        super(TestChatApi, self).tearDown()

    @property
    def chat_path(self):
        chat = os.environ['TEST_CHAT_PK']
        path = "/chat/ws/{}/".format(chat)
        return path

    def message(self, content, sender, receiver=None):
        if receiver:
            msg = '{"msg" : "%s", "sender": "%s", "receiver": "%s"}' % (
                content, sender, receiver
            )
        else:
            msg = '{"msg" : "%s", "sender": "%s"}' % (
                content, sender
            )
        return msg

    @unittest_run_loop
    async def test_open_ws_connect(self):
        print("========================")
        print("test_open_ws_connect")

        request = await self.client.ws_connect(
            path=self.chat_path,
            headers=self.first_headers
        )

        assert request.closed is False
        request.send_str('{"msg": "Hello world"}')
        await request.close()
        assert request.closed is True



    @unittest_run_loop
    async def test_chat_btw_users(self):
        print("========================")
        print("test_chat_btw_users")

        first_client = await self.client.ws_connect(
            path=self.chat_path,
            headers=self.first_headers
        )

        second_client = await self.client.ws_connect(
            path=self.chat_path,
            headers=self.second_headers
        )

        messages_for_first_client = []
        messages_for_second_client = []
        count_messages = 20

        for period in range(count_messages):
            gen_message = ''.join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(random.choice([4, 10]))).lower()

            if len(messages_for_first_client) <= 10:
                messages_for_first_client.append(gen_message)
            else:
                messages_for_second_client.append(gen_message)

        def message(content, sender):
            msg = '{"msg": "%s", "sender" : "%s", "send_at": "%s"}' % (content, sender, datetime.datetime.now())
            return msg

        receive_by_first_client = []
        receive_by_second_client = []

        def first_sender(client):
            for msg in messages_for_first_client:
                first_client.send_str(message(msg, client.get('client_id')))

        def second_sender(client):
            for msg in messages_for_first_client:
                second_client.send_str(message(msg, client.get('client_id')))

        first_sender(self.first_client)
        second_sender(self.second_client)

        async def messages_first_client():
            while len(receive_by_first_client) != count_messages:
                msg = await first_client.receive()
                receive_by_first_client.append(msg)

        async def messages_second_client():

            while len(receive_by_second_client) != count_messages:
                msg = await second_client.receive()
                receive_by_second_client.append(msg)

        await messages_first_client()
        await messages_second_client()

        print(receive_by_first_client)
        print(receive_by_second_client)

        await first_client.close()
        await second_client.close()

        assert first_client.closed is True
        assert second_client.closed is True

    @unittest_run_loop
    async def test_send_private_message(self):
        first_client = await self.client.ws_connect(
            path=self.chat_path,
            headers=self.first_headers
        )

        second_client = await self.client.ws_connect(
            path=self.chat_path,
            headers=self.second_headers
        )

        #   отправка публичного сообщения
        first_client.send_str(self.message("Hello second client", self.first_client.get('client_id')))
        second_client.send_str(self.message("Hello first client", self.second_client.get('client_id')))

        #   отправка приватного сообщения
        first_client.send_str(
            self.message(
                content="Hello second client from private message",
                sender=self.first_client.get('client_id'),
                receiver=self.second_client.get('client_id')
            )
        )

        receive_by_first_client = []
        receive_by_second_client = []

        async def messages_first_client():
            while len(receive_by_first_client) != 2:
                msg = await first_client.receive()
                receive_by_first_client.append(msg)

        async def messages_second_client():

            while len(receive_by_second_client) != 3:
                msg = await second_client.receive()
                receive_by_second_client.append(msg)

        await messages_first_client()
        await messages_second_client()

        print(receive_by_first_client)
        print(receive_by_second_client)

        await first_client.close()
        await second_client.close()

        assert first_client.closed is True
        assert second_client.closed is True

    @unittest_run_loop
    async def test_get_list_of_client_in_chat(self):
        print("========================")
        print("test_get_list_of_client_in_chat")
        path = "/chat/byId/{}/".format(os.environ['TEST_CHAT_PK'])
        request = await self.client.get(
            path=path,
            headers=self.first_headers
        )

        result = await request.json()
