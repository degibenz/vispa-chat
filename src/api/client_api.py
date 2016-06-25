# -*- coding: utf-8 -*-

__author__ = 'degibenz'
from aiohttp import web
from aiohttp.web import json_response

from models.client import Client, ObjectId
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
            pk=ObjectId(self.request.match_info.get('id'))
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

        client = Client(
            email=data.get('email'),
            password=data.get('password')
        )

        if self.request.app['db']:
            client.db = self.request.app['db']

        q = {'email': client.client_email}

        search = await client.objects.find_one(q)

        if not search:
            try:
                response = {
                    'status': True,
                    'client_id': "{}".format(await client.save()),
                }

            except(Exception,) as error:
                response = {
                    'status': False,
                    'error': "{}".format(error)
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

        client = Client(
            email=data.get('email'),
            password=data.get('password')
        )

        if self.request.app['db']:
            client.db = self.request.app['db']

        q = {
            "email": client.client_email,
            "password": client.password
        }

        client_exit = await client.get(**q)

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
                pk=ObjectId(data.get('id'))
            )

            if self.request.app['db']:
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
