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

    def __init__(self, email=None, password=None, pk: ObjectId = None):
        self.pk = pk
        self.client_email = email
        self.password = password

        super(Client, self).__init__()

    @property
    async def token(self):
        token_is = Token(
            client_uid=self.pk
        )

        token_is.db = self.db

        return await token_is.key()

    async def save(self, **kwargs):
        assert self.client_email is not None
        assert self.password is not None

        data = {
            'email': self.client_email,
            'password': self.password,
            'join_at': datetime.datetime.now()
        }

        return await super(Client, self).save(**data)

    async def delete(self):
        try:
            assert self.pk is not None

            token_is = Token()
            token_is.db = self.db

            search_q = {
                'client': ObjectId(self.pk),
                'token': "{}".format(await self.token)
            }
            search_key = await token_is.get(**search_q)

            token_is.pk = search_key.get('_id')

            await token_is.delete()

            q = {'_id': ObjectId(self.pk)}

            remove_result = await self.objects.remove(q)

            self.result = {
                'status': True,
                'result': remove_result
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
        self.client_uid = ObjectId(client_uid)
        super(Token, self).__init__()

    async def key(self):
        assert self.client_uid is not None

        q = {
            'client': ObjectId(self.client_uid)
        }

        search_key = await self.get(**q)

        if search_key:
            key = "{}".format(search_key.get('token'))
        else:
            key = str(uuid.uuid4())

            await self.save(**{
                'client': ObjectId(self.client_uid),
                'token': "{}".format(key),
                'create_at': datetime.datetime.now()
            })

        return key
