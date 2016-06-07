from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-
__author__ = 'degibenz'

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from bson.objectid import ObjectId
from configs.db import DB

__all__ = [
    'Model',
    'ObjectId'
]


class Model(object):
    pk = None
    db = None
    collection = None

    result = {}

    def __init__(self, **kwargs):
        database = DB()
        self.db = database.connect

    async def get(self):
        assert self.pk is not None

        try:
            self.result = await self.objects.find_one(
                {
                    "_id": ObjectId(self.pk)
                }
            )
        except(Exception,) as error:
            self.result = {
                'status': False,
                'error': '%s' % error
            }

            log.error("%s" % self.result)

        finally:
            return self.result

    async def save(self, **kwargs):
        try:
            self.result = await self.objects.insert(
                kwargs
            )

            self.pk = self.result

        except(Exception,) as error:
            self.result = {
                'status': False,
                'error': '%s' % error
            }

            log.error("%s" % self.result)

        finally:
            return self.result

    async def delete(self):

        try:
            self.objects.delete(
                {
                    "_id": ObjectId(self.pk)
                }
            )

            self.result = {
                'status': True
            }
        except(Exception,) as error:
            self.result = {
                'status': False,
                'error': '%s' % error
            }

            log.error("%s" % self.result)

        finally:
            return self.result

    @property
    def objects(self):
        return self.db["%s" % self.collection]
