# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import os
import asyncio
from app import app

CHAT_SERVER_PORT = int(os.getenv('CHAT_SERVER_PORT', 8080))
CHAT_SERVER_HOST = str(os.getenv('CHAT_SERVER_HOST', '0.0.0.0'))

loop = asyncio.get_event_loop()


async def init(loop):
    srv = await loop.create_server(
        app(loop=loop).make_handler(),
        CHAT_SERVER_HOST,
        CHAT_SERVER_PORT
    )
    return srv


loop.run_until_complete(
    init(loop)
)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
