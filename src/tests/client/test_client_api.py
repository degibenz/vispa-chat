# -*- coding: utf-8 -*-
import os, binascii

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json

import requests as r
import unittest

SERVER = "http://127.0.0.1:8080/{}"


class TestClientApi(unittest.TestCase):
    data = {}
    email = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    password = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    def setUp(self):
        self.data = {
            "email": "{}@mail-server.dns".format(self.email),
            "password": "{}".format(self.password)
        }

    def test_create_client(self):
        path = "client/create/"
        request = r.post(
            url=SERVER.format(path),
            data=json.dumps(self.data)
        )

        status = request.json().get('status')
        token = request.json().get('token')
        pk = request.json().get('client_id')

        http_status = request.status_code

        return request

    def test_again_create_client(self):
        request = self.test_create_client()

        status = request.json().get('status')
        token = request.json().get('token')
        pk = request.json().get('client_id')

        http_status = request.status_code

    def test_auth_client(self):
        path = "client/auth/"

        request = r.post(
            url=SERVER.format(path),
            data=json.dumps(self.data)
        )

        status = request.json().get('status')
        token = request.json().get('token')
        pk = request.json().get('client_id')
        http_status = request.status_code

        return pk

    def test_delete_client(self):
        log.info("Delete client")
        path = "client/delete/"

        pk = self.test_auth_client()

        data = {
            "id": "{}".format(pk)
        }

        request = r.post(
            url=SERVER.format(path),
            data=json.dumps(data)
        )

        status = request.json().get('status')


if __name__ == '__main__':
    unittest.main()
