# -*- coding: utf-8 -*-

__author__ = 'degibenz'

import uuid

import datetime
from core.model import Model, ObjectId

__all__ = [
    'Client',
    'Token'
]


class Client(Model):
    pk = None
    collection = 'clients'
    client_email = None
    password = None

    def __init__(self, email=None, password=None, pk=None):
        self.pk = pk
        self.client_email = email
        self.password = password

        super(Client, self).__init__()

    @property
    async def token(self):
        token_is = Token()
        token_is.db = self.db

        return await token_is.key(self.pk)

    async def delete(self):
        try:
            token_is = Token()

            search_key = await token_is.objects.find_one(
                {
                    'client': ObjectId(self.pk)
                }
            )

            token_is.pk = ObjectId(search_key.get('_id'))

            await token_is.delete()

            await super(Client, self).delete()

            self.result = {
                'status': True
            }

        except(Exception,) as error:
            self.result = {
                'status': False,
                'error': "{}".format(error)
            }

        finally:
            return self.result


class Token(Model):
    collection = 'tokens'
    client_uid = ObjectId
    token = str
    create_at = datetime.datetime

    def __init__(self, client_uid=None):
        self.client_uid = client_uid

        super(Token, self).__init__()

    async def key(self, client_pk):
        search_key = await self.objects.find_one(
            {
                'client': ObjectId(client_pk)
            }
        )

        if search_key:
            key = "%s" % search_key.get('token')

        else:
            key = str(uuid.uuid4())

            await self.save(**{
                'client': ObjectId(self.pk),
                'token': "%s" % key
            })

        return key
