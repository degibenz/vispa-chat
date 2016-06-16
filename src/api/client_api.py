# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import uuid
from aiohttp import web

from core.api import json_response

from models.client import Client, Token, ObjectId
from core.middleware import check_auth

__all__ = [
    'ClientInfo',
    'CreateClient',
    'AuthClient',
    'DeleteClient'
]


class ClientInfo(web.View):
    @check_auth
    async def get(self):
        client_obj = Client(
            pk=self.request.match_info.get('id')
        )

        if self.request.app['db']:
            client_obj.db = self.request.app['db']

        client = await client_obj.get()

        result = {
            'id': "{}".format(client.get('_id')),
            'email': "{}".format(client.get('email')),
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

        client.db = self.request.app['db']

        client_exit = await client.objects.find_one(
            {"email": email}
        )

        if not client_exit:
            client_object = await client.save(
                **data
            )

            token = Token()

            if self.request.app['db']:
                token.db = self.request.app['db']

            await client.save()

            token_is = await token.objects.find_one({
                'client': ObjectId("{}".format(client.pk))
            })

            if token_is:
                pass
            else:
                token_is = str(uuid.uuid4())

                await token.save(**{
                    'client': ObjectId(client.pk),
                    'token': "{}".format(token_is)
                })

            response = {
                'status': True,
                'client_id': "{}".format(client_object),
                'token': "{}".format(token_is)
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

        client.db = self.request.app['db']

        client_exit = await client.objects.find_one(
            {
                "email": email,
                "password": password
            }
        )

        if client_exit:
            client.pk = client_exit.get('_id')

            response = {
                'client_id': "{}".format(client.pk),
                'status': True,
                'token': "{}".format(await client.token)
            }

        else:
            response = {
                'status': False,
                'error': 'client not found'
            }

        return json_response(response)


class DeleteClient(web.View):
    async def post(self):
        data = await self.request.json()

        try:
            client = Client(
                pk=data.get('id')
            )

            client.db = self.request.app['db']

            if await client.get():
                await client.delete()

                response = {
                    'status': True
                }
            else:
                response = {
                    'status': False,
                    'error': 'client not found'
                }
        except(Exception,) as error:
            response = {
                'status': False,
                'error': "{}".format(error)
            }

        return json_response(response)
