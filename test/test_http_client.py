# Standard libs imports
import unittest
from typing import List, TextIO
from unittest import TestCase
from test.mixins import ServerTestMixin

# First party libs imports
from py_sugo.core import GET, PUT, POST, PATCH, DELETE, CONTENT_TYPE
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import Middleware, RequestHandler, parse_body_json, parse_body_form_data
from py_sugo.http_client import HttpClient, HttpResponse


class HttpClientTestCase(ServerTestMixin, TestCase):
    port: int = 50009
    http_client: HttpClient
    middleware: List[Middleware] = [parse_body_json, parse_body_form_data]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.http_client = HttpClient(default_headers={CONTENT_TYPE: 'application/json'}, base_url='http://localhost:%d' % cls.port)

    @classmethod
    def get_request_handler(cls) -> RequestHandler:
        def request_handler(request: Request, response: Response):
            res_data = {"method": request.method}
            if request.body.get('files', None):
                res_data['filename'] = request.body['files']['file'].filename
            if request.body.get('fields', None):
                res_data['fields'] = request.body['fields']
            if request.body.get('hello', None):
                res_data['hello'] = request.body['hello']
            return response.status(200).json(res_data)

        return request_handler

    def test_should_make_a_get_request(self):
        response: HttpResponse = self.http_client.get(path='/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], GET)

    def test_should_make_a_delete_request(self):
        response: HttpResponse = self.http_client.delete(path='/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], DELETE)

    def test_should_make_a_head_request(self):
        response: HttpResponse = self.http_client.head(path='/')
        self.assertEqual(response.status_code, 200)

    def test_should_make_a_options_request(self):
        response: HttpResponse = self.http_client.head(path='/')
        self.assertEqual(response.status_code, 200)

    def test_should_make_a_post_request(self):
        response: HttpResponse = self.http_client.post(path='/', body={"hello": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], POST)
        self.assertEqual(response.data['hello'], True)

    def test_should_make_a_put_request(self):
        response: HttpResponse = self.http_client.put(path='/', body={"hello": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], PUT)
        self.assertEqual(response.data['hello'], True)

    def test_should_make_a_patch_request(self):
        response: HttpResponse = self.http_client.patch(path='/', body={"hello": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], PATCH)
        self.assertEqual(response.data['hello'], True)

    def test_should_make_a_multiform_request(self):
        file: TextIO = open('README.md')
        response: HttpResponse = self.http_client.post(path='/', files={"file": file}, fields={"field": True})
        self.assertEqual(response.data['filename'], file.name)
        self.assertEqual(response.data['fields']['field'], 'True')
        file.close()


if __name__ == '__main__':
    unittest.main()
