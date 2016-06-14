# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import os
import asyncio

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

    def hold_connect(self, loop=None):
        if self.db:
            pass
        else:
            self.db = ma.AsyncIOMotorClient(
                '%s:%s' % (MONGODB_SERVER_HOST, MONGODB_SERVER_PORT),
                io_loop=loop,
            )

        return self.db['%s' % MONGODB_DB_NAME]
