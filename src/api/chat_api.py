# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp.log import *

from aiohttp import web

from core.exceptions import *
from core.middleware import check_auth
from aiohttp.web import json_response

from models.chat import *

__all__ = [
    'GetChat',
    'GetChatList',
    'CreateChat',
    'DeleteChat'
]


class GetChat(web.View):
    @check_auth
    async def get(self) -> json_response:
        chat = Chat(
            pk=self.request.match_info.get('id')
        )

        if self.request.app['db']:
            chat.db = self.request.app['db']

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

        return json_response(
            response
        )


class GetChatList(web.View):
    @check_auth
    async def get(self) -> json_response:
        chat = Chat()

        if self.request.app['db']:
            chat.db = self.request.app['db']

        response = {
            'status': True,
            'chats-list': await chat.list
        }

        return json_response(
            response
        )


class CreateChat(web.View):
    @check_auth
    async def post(self) -> json_response:
        assert self.request.client is not None

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


class DeleteChat(web.View):
    @check_auth
    async def post(self) -> json_response:
        response = {}

        data = await self.request.json()

        chat = Chat(
            pk=data.get('id')
        )

        if self.request.app['db']:
            chat.db = self.request.app['db']

        try:
            chat_is = await chat.get()

            if not chat_is.get('author') == self.request.client.get('_id'):
                raise NotPermissions
            else:
                response = {
                    'status': True,
                }
        except(Exception,) as error:
            response = {
                'status': False,
                'error': "{}".format(error)
            }
        finally:
            return json_response(
                response
            )
