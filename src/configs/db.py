# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import os

from motor import motor_asyncio as ma

__all__ = [
    'DB',
]

MONGODB_SERVER_HOST = os.getenv('MONGODB_SERVER_HOST', '127.0.0.1')
MONGODB_SERVER_PORT = os.getenv('MONGODB_SERVER_PORT', '27017')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'async-chat')


class DB(object):
    db = None
    loop = None

    def __init__(self, loop=None):
        self.loop = loop

    def hold_connect(self):
        if self.db:
            pass
        else:
            self.db = ma.AsyncIOMotorClient(
                '%s:%s' % (MONGODB_SERVER_HOST, MONGODB_SERVER_PORT),
                io_loop=self.loop,
            )

        return self.db['%s' % MONGODB_DB_NAME]
