from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-
__author__ = 'degibenz'

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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

            try:
                token_is = await token.objects.find_one({
                    'token': token_in_header
                })

                try:

                    if not token_is:
                        raise TokenIsNotFound

                    else:
                        client = Client(
                            pk=token_is.get('client')
                        )

                        request._request.client = await client.get()

                        if not client:
                            raise ClientNotFoundViaToken

                        return await func(request, *args, **kwargs)

                except(Exception,) as error:
                    log.error("%s" % error)

                    return json_response({
                        'status': False,
                        'error': 'token not correct'
                    })

            except(Exception,) as error:
                log.error("%s" % error)

                return json_response({
                    'status': False,
                    'error': '%s' % error
                })

    return wrapper
