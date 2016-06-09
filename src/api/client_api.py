# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp import web

from core.api import json_response

from models.client import Client
from core.middleware import check_auth

__all__ = [
    'ClientInfo',
    'CreateClient',
    'AuthClient'
]


class ClientInfo(web.View):
    @check_auth
    async def get(self):
        client_obj = Client(
            pk=self.request.match_info.get('id')
        )

        client = await client_obj.get()

        result = {
            'id': "{}".format(client.get('_id')),
            'email': client.get('email'),
        }

        return json_response(result)


class CreateClient(web.View):
    async def post(self):
        data = await self.request.json()

        email = data.get('email')
        password = data.get('password')

        data = {
            'email': email,
            'password': password
        }

        client = Client()

        client_exit = await client.objects.find_one(
            {"email": email}
        )

        if not client_exit:
            client_object = await client.save(
                **data
            )

            response = {
                'status': True,
                'client_id': "".format(client_object)
            }
        else:
            response = {
                'status': False,
                'error': 'client already exist'
            }

        return json_response(response)


class AuthClient(web.View):
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

            response = {
                'status': True,
                'token': "%s" % await client.token
            }

        else:
            response = {
                'status': False,
                'error': 'client not found'
            }

        return json_response(response)
