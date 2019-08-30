# Standard libs imports
import json
import unittest
from typing import Dict
from unittest import TestCase
from test.mixins import ServerTestMixin, HttpRequestMixin


class RequestTestCase(ServerTestMixin, HttpRequestMixin, TestCase):
    def test_request_id_should_be_set(self):
        response = self.http_request('GET', '/hello')
        response_body: Dict = json.loads(response.read())
        self.assertIsNotNone(response_body.get('id'))

    def test_request_path_should_be_set(self):
        response = self.http_request('GET', '/hello')
        response_body: Dict = json.loads(response.read())
        self.assertEqual(response_body.get('path'), '/hello')


if __name__ == '__main__':
    unittest.main()
