# -*- coding: utf-8 -*-

__author__ = 'degibenz'
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from aiohttp import web


class CustomWebSocketResponse(web.WebSocketResponse):
    agents = []
    client = None
    chat = None

    def __init__(self, *, timeout=10.0, autoclose=True, autoping=True, protocols=()):
        super(CustomWebSocketResponse, self).__init__(timeout=timeout, autoclose=autoclose, autoping=autoping,
                                                      protocols=protocols)

    @property
    def item(self):
        return {
            "client_uid": self.client,
            "chat_uid": self.chat,
            "socket": self
        }

    def add_client_to_list(self):
        print("add_client_to_list :: ->", self.client)

        self.agents.append(self.item)

    async def close(self, *, code=1000, message=b''):
        try:
            self.agents.remove(self.item)
        except(Exception,):
            pass
        await super(CustomWebSocketResponse, self).close(code=code, message=message)
