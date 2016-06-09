# -*- coding: utf-8 -*-

__author__ = 'degibenz'

from aiohttp import web
from aiohttp.web import json_response

__all__ = [
    'AbsView',
    'json_response'
]


class AbsView(web.View):
    response = {}
