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
        key = None
        token_is = Token()

        search_key = await token_is.objects.find_one(
            {
                'client': ObjectId(self.pk)
            }
        )

        if search_key:
            key = "%s" % search_key.get('token')

        else:
            token = str(uuid.uuid4())

            await token_is.save(**{
                'client': ObjectId(self.pk),
                'token': "%s" % token
            })

        return key


class Token(Model):
    collection = 'tokens'
    client_uid = ObjectId
    token = str
    create_at = datetime.datetime

    def __init__(self, client_uid=None):
        self.client_uid = client_uid

        super(Token, self).__init__()
