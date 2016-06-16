# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp.log import *

from aiohttp import web

from core.middleware import check_auth
from core.api import json_response
from models.chat import *

__all__ = [
    'GetChat',
    'GetChatList',
    'CreateChat',
]


class GetChat(web.View):
    @check_auth
    async def get(self):
        chat = Chat(
            pk=self.request.match_info.get('id')
        )
        chat_info = await chat.get()

        if chat_info:
            response = {
                'status': True,
                'chat-uid': "{}".format(chat.pk),
                'client-list': await chat.list_clients,
                'author': "{}".format(chat_info.get('author'))
            }
        else:
            response = {
                'status': False,
                'error': 'chat not found'
            }

        access_logger.log("%s" % response)

        return json_response(
            response
        )


class GetChatList(web.View):
    @check_auth
    async def get(self):
        chat = Chat()

        response = {
            'status': True,
            'chats-list': await chat.list
        }

        return json_response(
            response
        )


class CreateChat(web.View):
    @check_auth
    async def post(self):
        chat = Chat(
            author=self.request.client.get('_id')
        )

        if self.request.app['db']:
            chat.db = self.request.app['db']

        response = {
            'status': True,
            'chat': "{}".format(await chat.save())
        }

        return json_response(
            response
        )
