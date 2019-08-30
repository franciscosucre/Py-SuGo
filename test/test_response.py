# Standard libs imports
import json
import unittest
from typing import Dict
from unittest import TestCase
from test.mixins import ServerTestMixin, HttpRequestMixin

# First party libs imports
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import RequestHandler


class ResponseTestCase(ServerTestMixin, HttpRequestMixin, TestCase):
    port: int = 50001

    @classmethod
    def get_request_handler(cls) -> RequestHandler:
        def request_handler(request: Request, response: Response):
            return response.status(201).json({"hello": True})

        return request_handler

    def test_should_have_the_status_sent_to_status_method(self):
        response = self.http_request('GET', '/', port=self.port)
        self.assertEqual(response.status, 201)

    def test_have_the_body_sent_to_the_json(self):
        response = self.http_request('GET', '/', port=self.port)
        body: Dict = json.loads(response.read())
        self.assertTrue(body.get('hello'))


if __name__ == '__main__':
    unittest.main()
