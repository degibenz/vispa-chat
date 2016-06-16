# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp import web

from api.client_api import *
from api.chat_api import *

__all__ = [
    'app'
]

from configs.db import DB

database = DB()


def app(loop):
    app_server = web.Application(
        loop=loop
    )

    app_server.router.add_route('GET', '/client/{id}/', ClientInfo)
    app_server.router.add_route('POST', '/client/create/', CreateClient)
    app_server.router.add_route('POST', '/client/auth/', AuthClient)
    app_server.router.add_route('POST', '/client/delete/', DeleteClient)

    app_server.router.add_route('GET', '/chat/byId/{id}/', GetChat)
    app_server.router.add_route('GET', '/chat/list/', GetChatList)
    app_server.router.add_route('POST', '/chat/create/', CreateChat)

    return app_server
