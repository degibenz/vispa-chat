# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json

from aiohttp import web

from core.model import ObjectId
from core.exceptions import *

from models.chat import *
from models.client import Client, Token

__all__ = [
    'ChatWS'
]

DEBUG = True


class ChatWS(web.View):
    ws = None
    response = None
    chat = None
    client = None

    chat_pk = None
    client_pk = None
    db = None

    client_in_chat = None

    def __init__(self, request):
        try:
            self.db = request.app['db']
        except(KeyError,):
            pass

        self.chat_pk = request.match_info.get('id')

        super(ChatWS, self).__init__(request)

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
        async for msg in self.socket:
            content = json.loads(msg.data)

            receiver = content.get('receiver', None)

            if receiver:
                await self.check_receiver(receiver)

                receiver = ObjectId(receiver)

            msg_obj = MessagesFromClientInChat(
                chat=self.chat_pk,
                client=self.client_pk,
                msg=content.get('msg'),
                receiver_message=receiver
            )

            if self.db:
                msg_obj.db = self.db

            await msg_obj.save()

            for item in self.agents:
                await self.notify(
                    sender=item.get('client_uid'),
                    message=msg_obj.message_content,
                    socket=item.get('socket'),
                    receiver=receiver,
                )

    async def check_client(self):
        token_in_header = self.request.__dict__.get('headers').get('AUTHORIZATION', None)

        if not token_in_header:
            raise TokeInHeadersNotFound
        else:
            token = Token()
            token.token = token_in_header

            if self.db:
                token.db = self.db

            self.client = await token.find_client_by_key()

            if not self.client:
                raise TokenIsNotFound
            self.client_pk = ObjectId(self.client.get('client'))

    async def notify(self, sender: ObjectId, message: str, socket: web.WebSocketResponse, receiver: ObjectId = None, ):
        """
        Метод для рассылки сообщений всем участникам или выбранному пользователю в чате

        :param sender:
        :param socket:
        :param message: текст сообщения
        :param receiver: индификатор пользователя, который должен получить это сообщение
        """

        async def _notify():
            try:
                if not socket.closed:
                    socket.send_str(
                        data="{}".format(message)
                    )

            except(Exception,) as error:
                error_info = {
                    'action': 'notify',
                    'receiver': receiver,
                    'sender': sender,
                    'error': '{}'.format(error)
                }

                log.error(error_info)

        if receiver:
            message = "@{}: {}".format(receiver, message)

        await _notify()

    async def mark_client_as_offline(self):

        q = {
            'chat': self.chat_pk,
            'client': self.client_pk
        }

        await self.client_in_chat.objects.update(
            q,
            {'$set':
                 {'online': False}
             },
            upsert=False
        )

    @property
    def socket(self):
        for item in self.agents:
            if item.get('client_uid') == self.client_pk:
                return item.get('socket')

    @property
    def agents(self):
        result = []
        for ws in self.request.app['websockets']:
            if ws.get('chat_uid') == self.chat_pk:
                result.append(ws)

        return result

    async def get(self):
        try:
            self.ws = web.WebSocketResponse()
            await self.ws.prepare(self.request)

            self.chat_pk = ObjectId(self.chat_pk)

            chat = Chat(
                pk=self.chat_pk
            )

            if self.db:
                chat.db = self.db

            self.chat = await chat.get()

            await self.check_client()

            self.client_in_chat = ClientsInChatRoom(
                chat=self.chat_pk,
                client=self.client_pk,
            )

            if self.db:
                self.client_in_chat.db = self.db

            await self.client_in_chat.add_person_to_chat()

            self.request.app['websockets'].append({
                "socket": self.ws,
                "client_uid": self.client_pk,
                'chat_uid': self.chat_pk
            })

            for _ws in self.agents:
                _ws.get('socket').send_str('%s joined' % self.client_pk)

            await self.prepare_msg()

        except(Exception,) as error:
            self.response = {
                'status': False,
                'error': "{}".format(error)
            }

            log.error(self.response)
            await self.ws.close()

        finally:
            return self.ws
