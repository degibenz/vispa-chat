# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json
import asyncio

from aiohttp import web, MsgType

from aiohttp import web
from core.model import ObjectId
from core.exceptions import *

from models.chat import *
from models.client import Client

__all__ = [
    'ChatWS'
]

DEBUG = True

print("DEBUG :: ", DEBUG)


class ChatWS(web.View):
    ws = None
    response = None

    chat = None
    client = None

    chat_pk = None
    client_pk = None
    db = None
    agents = []

    client_in_chat = None

    def __init__(self, request):

        try:
            self.db = request.app['db']
        except(KeyError,):
            pass

        self.chat_pk = ObjectId(request.match_info.get('id'))
        self.client_pk = ObjectId(request.match_info.get('client'))

        super(web.View, self).__init__(request)

    async def check_receiver(self, receiver: ObjectId):
        """
        Метод проверяет, что получатель существует и находится в чате с отправителем.

        :param receiver: индификатор получателя
        """
        client = Client(
            pk=ObjectId(receiver)
        )

        if self.db:
            client.db = self.db

        await client.get()

        q = {
            'chat': self.chat_pk,
            'client': ObjectId(receiver)
        }

        if not await self.client_in_chat.get(**q):
            self.client_in_chat.save(**q)

    async def prepare_msg(self):
        while True:
            if DEBUG:
                print("Wait for message in Chat :: {}".format(self.chat_pk))

            if not self.ws.closed:
                msg = await self.ws.receive()

                if DEBUG:
                    print("Get message\nclient :: {}\nmessage  ::  {}".format(self.client_pk, msg))

                if msg.tp == MsgType.text:
                    content = json.loads(msg.data)

                    system_operation = content.get('system_operation', None)

                    if system_operation == 'close':
                        await self.close_chat(
                            for_me=True
                        )

                    else:

                        receiver = content.get('receiver', None)

                        if receiver:
                            await self.check_receiver(receiver)

                        msg_obj = MessagesFromClientInChat(
                            chat=self.chat_pk,
                            client=self.client_pk,
                            msg=content.get('msg'),
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
        """
            Метод для проверяет, что данный пользователь авторизован и что он это он.
            Ищем пользователя по указанному ID в строке URL
            Затем, находтим его token и сравниваем с тем, что указан в заголовке запроса
            Если токены не совпадают - произойдет ошибка
        """
        token_in_header = self.request.__dict__.get('headers').get('AUTHORIZATION',
                                                                   'c97868d8-ccd5-43e4-914c-fe87e9438ec0')

        if not token_in_header:
            raise TokeInHeadersNotFound
        else:

            client = Client(
                pk=self.client_pk
            )

            if self.db:
                client.db = self.db

            self.client = await client.get()

            if not str(await client.token) == str(token_in_header):
                raise TokenIsNotFound

    async def notify(self, item: dict, message: str, receiver: ObjectId = None):
        """
        Метод для рассылки сообщений всем участникам или выбранному пользователю в чате

        :param item: dict-объект хранящий в себе данные об ID отправителе и его socket
        :param message: текст сообщения
        :param receiver: индификатор пользователя, который должен получить это сообщение
        """

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

        q = {
            'chat': self.chat_pk,
            'client': self.client_pk
        }

        await self.client_in_chat.objects.update(
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
            print("Welcome to chat-server")
            chat = Chat(
                pk=self.chat_pk
            )

            if self.db:
                chat.db = self.db

            if DEBUG:
                print("Get information about chat :: {}".format(self.chat_pk))

            self.chat = await chat.get()

            if DEBUG:
                print("Check client information :: {}".format(self.client_pk))

            await self.check_client()

            if DEBUG:
                print("Add client :: {} to chat :: {}".format(self.client_pk, self.chat_pk))

            self.client_in_chat = ClientsInChatRoom(
                chat=self.chat_pk,
                client=self.client_pk,
            )

            if self.db:
                self.client_in_chat.db = self.db

            await self.client_in_chat.add_person_to_chat()

            if DEBUG:
                print("Add client to agents-list :: {}".format(self.client_pk))

            self.agents.append(
                {
                    "client_uid": self.client_pk,
                    "chat_uid": self.chat_pk,
                    "socket": self.ws
                }
            )

            self.ws = web.WebSocketResponse()
            await self.ws.prepare(self.request)

            if DEBUG:
                print("prepare msg from client :: {} in chat :: {}".format(self.client_pk, self.chat_pk))

            await asyncio.gather(
                self.prepare_msg(),
                return_exceptions=True
            )

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
