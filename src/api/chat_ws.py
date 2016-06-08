from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-
__author__ = 'degibenz'

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json
import asyncio
import traceback

from aiohttp import web, MsgType

from configs.db import DB

from core.api import AbsView
from core.model import ObjectId

from models.chat import *
from models.client import Token, Client

from core.exceptions import *

__all__ = [
    'ChatWS'
]

loop = asyncio.get_event_loop()

# TODO было бы хорошо, сделать тут полноценное удержание соединения
database = DB(loop=loop)


def init_model():
    connection = database.hold_connect()
    return connection


class ChatWS(AbsView):
    ws = None

    chat = None
    client = None

    chat_pk = None
    client_pk = None

    agents = []

    db = None

    def __init__(self, request):
        self.db = init_model()

        self.chat_pk = ObjectId(request.match_info.get('id'))
        self.client_pk = ObjectId(request.match_info.get('client'))

        super(AbsView, self).__init__(request)

    async def check_receiver(self, receiver: ObjectId):
        client = Client(
            pk=ObjectId(receiver)
        )

        if not await client.get():
            raise ClientNotFound

        client_in_chat = ClientsInChatRoom()

        q = {
            'chat': self.chat_pk,
            'client': ObjectId(receiver)
        }

        if not await client_in_chat.objects.find_one(q):
            raise ClientNotFoundInChat

    async def prepare_msg(self):
        while True:
            msg = await self.ws.receive()

            if msg.tp == MsgType.text:

                if msg.data == 'close':

                    log.info("Client :: %s and exit from chat :: %s" % (self.client_pk, self.chat_pk))

                    await self.close_chat(for_me=True)

                else:
                    try:
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

                        await msg_obj.save()

                        try:
                            for client in self.agents:
                                await self.notify(client, msg_obj.message_content, receiver)
                        except(Exception,) as error:
                            log.error("%s" % error)

                    except(Exception,) as error:
                        log.error("prepare_msg :: %s" % error)

    async def check_client(self):
        token_in_header = self.request.__dict__.get('headers').get('AUTHORIZATION', None)

        if not token_in_header:
            raise TokeInHeadersNotFound

        token = Token()

        token_is = await token.objects.find_one({
            'token': token_in_header
        })

        if not token_is:
            raise TokenIsNotFound

        client = Client(
            pk=token_is.get('client')
        )

        self.client = await client.get()

        if not self.client:
            raise ClientNotFoundViaToken

    async def cache_ws(self):
        try:
            chat_root = ClientsInChatRoom(
                chat=self.chat_pk,
                client=self.client_pk,
            )

            q = {
                'chat': chat_root.chat,
                'client': chat_root.client,
                'online': True
            }

            if not await chat_root.objects.find_one(q):
                await chat_root.save()

        except(Exception,) as error:
            log.error("%s" % error)

    async def notify(self, item: dict, message: str, receiver=None):

        async def _notify():
            socket = item.get('socket')

            try:
                if not socket.closed:
                    await socket.send_str(
                        data="%s" % message
                    )

            except(Exception,) as error:
                log.error("notify :: %s" % error)

        if receiver:
            if item.get('client_uid') == receiver:
                message = "@%s" % receiver + message

        await _notify()

    async def close_chat(self, for_me=False):

        async def _del_it():
            try:
                await item.get('socket').close()
            except(Exception,)as error:
                pass
            finally:
                del item

        for item in self.agents:
            if for_me:
                if item.get('chat_uid') == self.chat_pk and item.get('client_uid') == self.client_pk:
                    await _del_it()
            else:
                await _del_it()

    async def get(self):
        try:

            chat = Chat(
                pk=self.chat_pk
            )

            self.chat = await chat.get()

            if not self.chat:
                raise ChatNotFound

            self.ws = web.WebSocketResponse()

            await self.ws.prepare(self.request)

            await self.cache_ws()

            self.agents.append(
                {
                    "client_uid": self.client_pk,
                    "chat_uid": self.chat_pk,
                    "socket": self.ws
                }
            )

            await asyncio.gather(self.prepare_msg())

        except(Exception,) as error:

            traceback.print_exc()

            self.response = {
                'status': False,
                'error': '%s' % error
            }

            log.error("%s" % self.response)

        finally:
            return self.ws
