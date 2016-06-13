# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp import web

from api.client_api import *
from api.chat_api import *

__all__ = [
    'app'
]

app = web.Application()

app.router.add_route('GET', '/client/{id}/', ClientInfo)
app.router.add_route('POST', '/client/create/', CreateClient)
app.router.add_route('POST', '/client/auth/', AuthClient)
app.router.add_route('POST', '/client/delete/', DeleteClient)

app.router.add_route('GET', '/chat/byId/{id}/', GetChat)
app.router.add_route('GET', '/chat/list/', GetChatList)
app.router.add_route('POST', '/chat/create/', CreateChat)