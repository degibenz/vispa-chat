# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import traceback
import os
import asyncio

from aiohttp.log import *
from bson.objectid import ObjectId
from core.exceptions import ObjectNotFound

from configs.db import DB

__all__ = [
    'Model',
    'ObjectId'
]

# TODO было бы хорошо, сделать тут полноценное удержание соединения
database = DB()


class Model(object):
    pk = None
    db = None
    collection = None
    loop = None

    result = {}

    def __init__(self, **kwargs):
        if not bool(os.getenv('IS_TEST')):
            if 'io_loop' in kwargs.keys():
                self.loop = kwargs.get('io_loop')
            else:
                self.loop = asyncio.get_event_loop()

            self.db = database(loop=self.loop)

    async def get(self, **kwargs) -> dict:
        q = None
        try:
            q = {"_id": ObjectId(self.pk)} if self.pk else kwargs

            self.result = await self.objects.find_one(
                q
            )

            if not self.result:
                raise ObjectNotFound(cls_name=self.__class__.__name__)

        except(Exception, AssertionError) as error:
            self.result = {
                'status': False,
                'error': '%s' % error,
                'model': "{}".format(self.__class__.__name__),
                'action': 'get',
                'query': q
            }

            access_logger.error("%s" % self.result)

        finally:
            return self.result

    async def save(self, **kwargs) -> dict:
        try:
            self.result = await self.objects.insert(
                kwargs
            )

            self.pk = self.result

        except(Exception,) as error:
            self.result = {
                'status': False,
                'error': '%s' % error,
                'model': "{}".format(self.__class__.__name__),
                'action': 'save'
            }

            access_logger.error("%s" % self.result)

        finally:
            return self.result

    async def delete(self) -> dict:

        try:
            if not await self.get():
                raise ObjectNotFound

            self.objects.remove(
                {
                    "_id": ObjectId(self.pk)
                }
            )

            self.result = {
                'status': True
            }
        except(Exception, AssertionError) as error:
            self.result = {
                'status': False,
                'error': '%s' % error,
                'model': "{}".format(self.__class__.__name__),
                'action': 'delete'
            }

        finally:
            return self.result

    @property
    def objects(self):
        return self.db["%s" % self.collection]
