from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-
__author__ = 'degibenz'

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import asyncio
from aiohttp import web

from api.chat_ws import *

loop = asyncio.get_event_loop()


async def ws_chat(loop):
    app = web.Application()
    app.router.add_route('GET', '/chat/ws/{id}/{client}/', ChatWS)

    srv = await loop.create_server(
        app.make_handler(), '0.0.0.0', 8090)
    return srv


loop.run_until_complete(
    ws_chat(loop)
)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
