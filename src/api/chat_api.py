from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp.log import *

from core.middleware import check_auth
from core.api import AbsView, json_response
from models.chat import *

__all__ = [
    'GetChat',
    'GetChatList',
    'CreateChat',
]


class GetChat(AbsView):
    @check_auth
    async def get(self):
        try:
            chat = Chat(
                pk=self.request.match_info.get('id')
            )
            chat_info = await chat.get()

            self.response = {
                'chat-uid': "%s" % chat.pk,
                'client-list': await chat.list_clients,
                'author': "%s" % chat_info.get('author')
            }

            access_logger.log("%s" % self.response)

        except(Exception,) as error:
            self.response = {
                'status': False,
                'error': '%s' % error
            }

            access_logger.error("%s" % self.response)

        finally:

            return json_response(
                self.response
            )


class GetChatList(AbsView):
    @check_auth
    async def get(self):
        try:
            chat = Chat()

            self.response = {
                'status': True,
                'chats-list': await chat.list
            }

        except(Exception,) as error:
            self.response = {
                'status': False,
                'error': '%s' % error
            }

            server_logger.error("%s" % self.response)

        finally:
            return json_response(
                self.response
            )


class CreateChat(AbsView):
    @check_auth
    async def post(self):
        try:

            chat = Chat(
                author=self.request.client.get('_id')
            )

            self.response = {
                'status': True,
                'chat': "%s" % await chat.save()
            }

        except(Exception,) as error:
            self.response = {
                'status': False,
                'error': '%s' % error
            }

            server_logger.error("%s" % self.response)

        finally:
            return json_response(
                self.response
            )
