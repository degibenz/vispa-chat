# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp.log import *

from functools import wraps

from models.client import Token, Client
from core.api import json_response

from core.exceptions import *

__all__ = [
    'check_auth',
]


def check_auth(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):

        token_in_header = request._request.__dict__.get('headers').get('AUTHORIZATION', None)

        if token_in_header:
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
                        pk="{}".format(token_is.get('client'))
                    )

                    print("info token :: ", token_is)
                    print("client in token :: ", token_is.get('client'))

                    if request._request.app['db']:
                        client.db = request._request.app['db']

                    request._request.client = await client.get()

                    print("Client is :: ", await client.get())

                    if not client:
                        raise ClientNotFoundViaToken

                    return await func(request, *args, **kwargs)

                    # except(Exception,) as error:
                    #     access_logger.error("%s" % error)
                    #
                    #     return json_response({
                    #         'status': False,
                    #         'error': '%s' % error
                    #     })

    return wrapper
