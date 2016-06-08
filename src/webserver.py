from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-
__author__ = 'degibenz'
import os
import asyncio
from aiohttp import web

from api.client_api import *
from api.chat_api import *

loop = asyncio.get_event_loop()


async def init(loop):
    app = web.Application()

    app.router.add_route('GET', '/client/{id}/', ClientInfo)
    app.router.add_route('POST', '/client/create/', CreateClient)
    app.router.add_route('POST', '/client/auth/', AuthClient)

    app.router.add_route('GET', '/chat/byId/{id}/', GetChat)
    app.router.add_route('GET', '/chat/list/', GetChatList)
    app.router.add_route('POST', '/chat/create/', CreateChat)

    srv = await loop.create_server(
        app.make_handler(),
        '0.0.0.0',
        8080
    )
    return srv


loop.run_until_complete(
    init(loop)
)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
