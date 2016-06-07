from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import os
from motor import motor_asyncio as ma

__all__ = [
    'DB',
]

MONGODB_SERVER_HOST = os.getenv('MONGODB_SERVER_HOST', '127.0.0.1')
MONGODB_SERVER_PORT = os.getenv('MONGODB_SERVER_PORT', '27017')


class DB(object):
    db = None

    @property
    def connect(self):
        if self.db:
            pass
        else:
            self.db = ma.AsyncIOMotorClient(
                '%s:%s' % (MONGODB_SERVER_HOST, MONGODB_SERVER_PORT)
            )

        return self.db['async-chat']
