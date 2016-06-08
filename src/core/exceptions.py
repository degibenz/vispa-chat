from __future__ import unicode_literals, absolute_import

# -*- coding: utf-8 -*-

__author__ = 'degibenz'


class TokeInHeadersNotFound(Exception):
    def __str__(self):
        return "requires authorization key in request-header"


class TokenIsNotFound(Exception):
    def __str__(self):
        return "token not found"


class ClientNotFoundViaToken(Exception):
    def __str__(self):
        return "Can't found client via token"


class ClientNotFound(Exception):
    def __str__(self):
        return "client not found"


class ClientNotFoundInChat(Exception):
    def __str__(self):
        return "client not found in chat"


class ChatNotFound(Exception):
    def __str__(self):
        return "Chat not found via enter PK"


class SendMessageYourself(Exception):
    def __str__(self):
        return "you cant send message yourself"
