# -*- coding: utf-8 -*-
import os, binascii

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import unittest
import mongomock

from models.client import Client


class TestClient(unittest.TestCase):
    email = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    password = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    def setUp(self):
        self.mock_db = mongomock.MongoClient().db

    def test_create_client(self):
        client = Client(
            email=self.email,
            password=self.password
        )

        client.db = self.mock_db

        client.save()

    def test_delete_client(self):
        client = Client(
            email=self.email,
            password=self.password
        )

        client.db = self.mock_db

        client.delete()
