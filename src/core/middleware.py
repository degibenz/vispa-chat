# -*- coding: utf-8 -*-
__author__ = 'degibenz'

from functools import wraps
from aiohttp.web import json_response

from models.client import Token, Client
from core.exceptions import *

__all__ = [
    'check_auth',
]


def check_auth(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):

        token_in_header = request._request.__dict__.get('headers').get('AUTHORIZATION', None)

        if token_in_header:
            try:
                token = Token()

                if request._request.app['db']:
                    token.db = request._request.app['db']

                token_is = await token.objects.find_one({
                    'token': token_in_header
                })

                if not token_is:
                    raise TokenIsNotFound

                else:
                    client = Client(
                        pk=token_is.get('client')
                    )
                    if request._request.app['db']:
                        client.db = request._request.app['db']

                    request._request.client = await client.get()

                    if not client:
                        raise ClientNotFoundViaToken
                    else:
                        return await func(request, *args, **kwargs)
            except(Exception,) as error:
                return json_response({
                    'status': False,
                    'error': '{}'.format(error)
                })

        else:
            return json_response({
                'status': False,
                'error': 'need token in headers'
            })

    return wrapper
