# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp import web

from api.client_api import *
from api.chat_api import *
from api.chat_ws import *

__all__ = [
    'app'
]


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
    app_server.router.add_route('POST', '/chat/delete/', DeleteChat)

    app_server.router.add_route('GET', '/chat/ws/{id}/', ChatWS)
    app_server['websockets'] = []

    return app_server
