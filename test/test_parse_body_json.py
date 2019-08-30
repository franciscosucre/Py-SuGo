# Standard libs imports
import json
import unittest
from time import sleep
from typing import Dict
from unittest import TestCase
from test.mixins import HttpRequestMixin

# First party libs imports
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import parse_body_json
from py_sugo.application import Application


class ParseBodyJsonTestCase(HttpRequestMixin, TestCase):
    port: int = 50004
    body: Dict = {"hello": 1}

    def test_should_not_parse_anything_if_content_type_is_not_json(self):
        def handler(request: Request, response: Response):
            self.assertEqual(len(request.body.keys()), 0)
            self.assertEqual(request.raw_body, json.dumps(self.body).encode('utf-8'))
            return response.json({})

        application = Application(handler)
        application.use_middleware(parse_body_json)
        application.listen(port=self.port, parallel=True)
        response = self.http_request('POST', '/', body=self.body, headers={"content-type": "plain/text"}, port=self.port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)

    def test_should_parse_if_content_type_is_json(self):
        def handler(request: Request, response: Response):
            self.assertTrue(isinstance(request.body, dict))
            return response.json({})

        port = self.port + 1
        application = Application(handler)
        application.use_middleware(parse_body_json)
        application.listen(port=port, parallel=True)
        response = self.http_request(method='POST', path='/', body=self.body, headers={"content-type": "application/json"}, port=port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)


if __name__ == '__main__':
    unittest.main()
