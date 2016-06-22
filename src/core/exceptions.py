# -*- coding: utf-8 -*-

__author__ = 'degibenz'


class ObjectNotFound(Exception):
    cls_name = None

    def __init__(self, cls_name):
        self.cls_name = cls_name

    def __str__(self):
        return "Object :: {} not found".format(self.cls_name)


class NotPermissions(Exception):
    def __str__(self):
        return "not have permission for this action"


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
