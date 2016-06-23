# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import os
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json
import asyncio

from aiohttp import web, MsgType

from core.api import AbsView
from core.model import ObjectId
from core.exceptions import *

from models.chat import *
from models.client import Client

__all__ = [
    'ChatWS'
]


class ChatWS(AbsView):
    ws = None

    chat = None
    client = None

    chat_pk = None
    client_pk = None
    db = None
    agents = []

    def __init__(self, request):
        try:
            self.db = request.app['db']
        except(KeyError,):
            pass

        self.chat_pk = ObjectId(request.match_info.get('id'))
        self.client_pk = ObjectId(request.match_info.get('client'))

        super(AbsView, self).__init__(request)

    async def check_receiver(self, receiver: ObjectId):
        client = Client(
            pk=ObjectId(receiver)
        )

        if self.db:
            client.db = self.db

        await client.get()

        client_in_chat = ClientsInChatRoom()

        if self.db:
            client_in_chat.db = self.db

        q = {
            'chat': self.chat_pk,
            'client': ObjectId(receiver)
        }

        if not await client_in_chat.get(**q):
            client_in_chat.save()

    async def prepare_msg(self):
        if not self.ws.closed:

            msg = await self.ws.receive()
            if msg.tp == MsgType.text:
                content = json.loads(msg.data)

                system_operation = content.get('system_operation', None)

                if system_operation == 'close':
                    await self.close_chat(for_me=True)

                else:
                    data = json.loads(msg.data)

                    receiver = data.get('receiver', None)

                    if receiver:
                        await self.check_receiver(receiver)

                    msg_obj = MessagesFromClientInChat(
                        chat=self.chat.get('_id'),
                        client=self.client_pk,
                        msg=data.get('msg'),
                        receiver_message=receiver
                    )

                    if self.db:
                        msg_obj.db = self.db

                    await msg_obj.save()

                    for client in self.agents:
                        await self.notify(
                            client,
                            msg_obj.message_content,
                            receiver
                        )

    async def check_client(self):

        token_in_header = self.request.__dict__.get('headers').get('AUTHORIZATION', None)

        # if not bool(os.getenv('IS_TEST')):
        #     token_in_header = 'c97868d8-ccd5-43e4-914c-fe87e9438ec0'

        if not token_in_header:
            raise TokeInHeadersNotFound
        else:
            client = Client(
                pk=self.client_pk
            )

            if self.db:
                client.db = self.db

            self.client = await client.get()
            if not self.client:
                raise ObjectNotFound(cls_name=Client)

            if not str(await client.token) == str(token_in_header):
                raise TokenIsNotFound

    async def notify(self, item: dict, message: str, receiver=None):

        async def _notify():
            socket = item.get('socket')

            try:
                if not socket.closed:
                    await socket.send_str(
                        data="{}".format(message)
                    )

            except(Exception,) as error:
                log.error("notify :: {}".format(error))

        if receiver:
            if item.get('client_uid') == receiver:
                message = "@{}: {}".format(receiver, message)

        await _notify()

    async def _del_it(self, item):
        print("Mark client :: {} in chat :: {} as offline".format(self.client_pk, self.chat_pk))

        client_in_chat = ClientsInChatRoom()

        q = {
            'chat': self.chat_pk,
            'client': self.client_pk
        }

        if self.db:
            client_in_chat.db = self.db

        await client_in_chat.objects.update(
            q,
            {'$set': {'online': False}},
            upsert=False
        )

        await item.get('socket').close()
        self.agents.remove(item)

    async def close_chat(self, for_me=False):
        for item in self.agents[:]:
            if for_me:
                if item.get('chat_uid') == self.chat_pk and item.get('client_uid') == self.client_pk:
                    await self._del_it(item)
            else:
                await self._del_it(item)

    async def get(self):
        try:
            chat = Chat(
                pk=self.chat_pk
            )

            if self.db:
                chat.db = self.db

            self.chat = await chat.get()

            self.ws = web.WebSocketResponse()

            await self.ws.prepare(self.request)

            await self.check_client()

            client_in_room = ClientsInChatRoom(
                chat=self.chat_pk,
                client=self.client_pk,
            )

            if self.db:
                client_in_room.db = self.db

            await client_in_room.add_person_to_chat()

            self.agents.append(
                {
                    "client_uid": self.client_pk,
                    "chat_uid": self.chat_pk,
                    "socket": self.ws
                }
            )

            await asyncio.gather(self.prepare_msg())

        except(Exception,) as error:

            self.response = {
                'status': False,
                'error': "{}".format(error)
            }

            data = {
                'client_uid': self.client_pk,
                'socket': self.ws
            }

            await self.notify(
                item=data,
                message="{}".format(self.response)
            )

            await self.close_chat()

        finally:
            return self.ws
