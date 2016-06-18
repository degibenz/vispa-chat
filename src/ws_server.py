# -*- coding: utf-8 -*-

__author__ = 'degibenz'

import os
import asyncio
from aiohttp import web

from api.chat_ws import *

loop = asyncio.get_event_loop()

CHAT_SERVER_PORT = int(os.getenv('CHAT_SERVER_PORT', 8090))
CHAT_SERVER_HOST = str(os.getenv('CHAT_SERVER_HOST', '0.0.0.0'))


async def ws_chat(loop):
    app = web.Application()
    app.router.add_route('GET', '/chat/ws/{id}/{client}/', ChatWS)

    srv = await loop.create_server(
        app.make_handler(),
        CHAT_SERVER_HOST,
        CHAT_SERVER_PORT
    )
    return srv


loop.run_until_complete(
    ws_chat(loop)
)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
