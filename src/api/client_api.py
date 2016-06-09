# -*- coding: utf-8 -*-

__author__ = 'degibenz'

import uuid
from core.api import AbsView, json_response
from bson.objectid import ObjectId

from models.client import Client, Token
from core.middleware import check_auth

__all__ = [
    'ClientInfo',
    'CreateClient',
    'AuthClient'
]


class ClientInfo(AbsView):
    @check_auth
    async def get(self):
        client = Client(
            pk=self.request.match_info.get('id')
        )

        response = await client.get()

        self.response = {
            'id': str(response.get('_id')),
            'email': response.get('email'),
        }

        if hasattr(self.request, 'client'):
            if str(self.request.client) == str(response.get('_id')):
                self.response.setdefault(
                    'token', "%s" % await client.token
                )

        return json_response(self.response)


class CreateClient(AbsView):
    async def post(self):
        data = await self.request.json()

        email = data.get('email')
        password = data.get('password')

        data = {
            'email': email,
            'password': password
        }

        client = Client()

        client_exit = await client.db["%s" % client.collection].find_one(
            {"email": email}
        )

        if not client_exit:
            client_object = await client.save(
                **data
            )

            self.response = {
                'status': True,
                'client_id': "%s" % client_object
            }
        else:
            self.response = {
                'status': False,
                'error': 'client already exist'
            }

        return json_response(self.response)


class AuthClient(AbsView):
    async def post(self):
        data = await self.request.json()

        email = data.get('email')
        password = data.get('password')

        client = Client()

        client_exit = await client.objects.find_one(
            {
                "email": email,
                "password": password
            }
        )

        if client_exit:

            token = Token(
                client_uid=client_exit.get('_id')
            )

            token_exist = await token.objects.find_one(
                {
                    "client": ObjectId(token.client_uid)
                }
            )

            if token_exist:
                token_is = token_exist.get(
                    'token'
                )

            else:
                token_is = str(uuid.uuid4())

                await token.save(**{
                    'client': token.client_uid,
                    'token': "%s" % token_is
                })

            self.response = {
                'status': True,
                'token': "%s" % token_is
            }

        else:
            self.response = {
                'status': False,
                'error': 'client not found'
            }

        return json_response(self.response)
