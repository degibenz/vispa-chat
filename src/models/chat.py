# -*- coding: utf-8 -*-

__author__ = 'degibenz'

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import datetime
from core.model import Model, ObjectId
from core.exceptions import *
from models.client import Client

__all__ = [
    'Chat',
    'ClientsInChatRoom',
    'MessagesFromClientInChat'
]


class Chat(Model):
    collection = 'chats'

    pk = ObjectId
    author = ObjectId
    create_at = datetime.datetime

    def __init__(self, author: ObjectId = None, pk: ObjectId = None):
        self.pk = pk
        self.author = author
        self.create_at = datetime.datetime.now()

        super(Chat, self).__init__()

    @property
    async def list(self):
        result = []

        try:

            cursor = self.objects.find({})

            while await cursor.fetch_next:
                doc = cursor.next_object()

                result.append(
                    {
                        'chat-id': "%s" % doc.get('_id'),
                        'author': "%s" % doc.get('author')
                    }
                )

            return result

        except(Exception,) as error:
            log.error("%s" % error)
        finally:
            return result

    @property
    async def list_clients(self):
        assert self.pk is not None

        result = []

        try:

            cursor = self.objects.find(
                {'chat': ObjectId(self.pk)}
            )

            while await cursor.fetch_next:
                doc = cursor.next_object()

                result.append(
                    {
                        'chat-id': "%s" % doc.get('_id'),
                        'author': "%s" % doc.get('author')
                    }
                )

            return result

        except(Exception,) as error:
            log.error("%s" % error)
        finally:
            return result

    async def save(self, **kwargs):
        assert self.author is not None

        data = {
            'author': self.author,
            'create_at': self.create_at
        }

        return await super(Chat, self).save(**data)


class ClientsInChatRoom(Model):
    collection = 'clients-in-chat'

    chat = Chat
    client = Client
    join_at = datetime.datetime

    online = True

    def __init__(self, chat: ObjectId = None, client: ObjectId = None):
        self.chat = chat
        self.client = client
        self.join_at = datetime.datetime.now()

        super(ClientsInChatRoom, self).__init__()

    async def save(self, **kwargs):
        data = {
            'chat': self.chat,
            'client': self.client,
            'join_at': self.join_at,
            'online': self.online,
        }

        return await super(ClientsInChatRoom, self).save(**data)


class MessagesFromClientInChat(Model):
    collection = 'messages'

    chat = ObjectId

    client = ObjectId
    receiver_message = ObjectId

    message_content = str

    send_at = datetime.datetime

    def __init__(self, chat: ObjectId = None, client: ObjectId = None, receiver_message: ObjectId = None, msg: str = None):

        self.chat = chat
        self.client = client
        self.receiver_message = receiver_message

        self.send_at = datetime.datetime.now()
        self.message_content = msg

        super(MessagesFromClientInChat, self).__init__()

    async def save(self, **kwargs):
        if str(self.client) == str(self.receiver_message):
            raise SendMessageYourself

        else:
            data = {
                'client': self.client,
                'receiver': self.receiver_message,
                'msg': self.message_content,
                'join': self.send_at
            }

        return await super(MessagesFromClientInChat, self).save(**data)

    async def messages(self):
        return await self.objects.find({'chat': ObjectId(self.chat)}).order(['join', 1])
