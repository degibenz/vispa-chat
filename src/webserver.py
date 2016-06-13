# -*- coding: utf-8 -*-

__author__ = 'degibenz'

import asyncio
from app import app

loop = asyncio.get_event_loop()

async def init(loop):
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
