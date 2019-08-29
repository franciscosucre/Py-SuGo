# Standard libs imports
import json
import unittest
from time import sleep
from typing import Dict, Any
from http.client import HTTPConnection

# Third party libs imports
from unittest import TestCase
from urllib import parse

from request import Request
from response import Response
from middleware import RequestHandler, NextFunction, parse_body_json
from application import Application


class ServerTestMixin:
    host: str = 'localhost'
    port: int = 50000
    application: Application

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = Application(cls.get_request_handler())
        cls.application.listen(cls.host, cls.port, True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.application.close()


    @classmethod
    def get_request_handler(cls) -> RequestHandler:
        def request_handler(request: Request, response: Response):
            return response.status(200).json({
                "body": request.body,
                "id": request.id,
                "method": request.method,
                "query": request.query,
                "path": request.path,
            })
        return request_handler


class HttpRequestMixin:
    host: str = 'localhost'
    port: int = 50000

    @classmethod
    def http_request(cls, method: str, path: str = '/', headers=dict(), body: Any = None, host='localhost', port=50000):
        connection = HTTPConnection(host=host, port=port)
        connection.request(method=method, url=path, body=body, headers=headers)
        return connection.getresponse()


class RequestTestCase(ServerTestMixin, HttpRequestMixin, TestCase):

    def test_request_path_should_be_set(self):
        response = self.http_request('GET', '/hello')
        response_body: Dict = json.loads(response.read())
        self.assertIsNotNone(response_body.get('id'))

    def test_request_path_should_be_set(self):
        response = self.http_request('GET', '/hello')
        response_body: Dict = json.loads(response.read())
        self.assertEqual(response_body.get('path'), '/hello')


class ResponseTestCase(ServerTestMixin, HttpRequestMixin, TestCase ):
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


class MiddlewareTestCase(HttpRequestMixin, TestCase):

    def get_first_middleware(self):
        def first_middleware(request: Request, response: Response, next: NextFunction):
            request.body = dict()
            request.body['first'] = True
            next()
        return first_middleware

    def get_second_middleware(self):
        def second_middleware(request: Request, response: Response, next: NextFunction):
            request.body['second'] = True
            next()
            self.assertEqual(request.body['handler'], True)
        return second_middleware

    def test_should_run_added_middleware(self):
        def request_handler(request: Request, response: Response):
            return response.status(201).json(request.body)
        app = Application(request_handler)
        app.use_middleware(self.get_first_middleware())
        app.listen(port=50002, parallel=True)
        response = self.http_request('GET', '/', port=50002)
        app.close()
        body = json.loads(response.read())
        self.assertTrue(body.get('first'))

    def test_should_handle_the_route_then_continue_the_middleware(self):
        def request_handler(request: Request, response: Response):
            request.body['handler'] = True
            self.assertTrue(request.body['second'])
            return response.status(201).json(request.body)

        app = Application(request_handler)
        app.use_middleware(self.get_first_middleware())
        app.use_middleware(self.get_second_middleware())
        app.listen(port=50003, parallel=True)
        response = self.http_request('GET', '/', port=50003)
        app.close()
        body = json.loads(response.read())
        self.assertTrue(body.get('first'))
        self.assertTrue(body.get('second'))


class ParseBodyJsonTestCase(HttpRequestMixin, TestCase):
    port: int = 50004

    def test_should_not_parse_anything_if_content_type_is_not_json(self):
        def handler(request: Request, response: Response):
            self.assertTrue(isinstance(request.body, str))
            return response.json({})
        application = Application(handler)
        application.use_middleware(parse_body_json)
        application.listen(port=self.port, parallel=True)
        response = self.http_request('POST', '/', body="{ hello: 1 }", headers={ "content-type": "plain/text"  }, port=self.port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)

    def test_should_parse_if_content_type_is_json(self):


        def handler(request: Request, response: Response):
            self.assertTrue(isinstance(request.body, dict))
            return response.json({})

        application = Application(handler)
        application.use_middleware(parse_body_json)
        response = self.http_request('POST', '/', body="{ hello: 1 }", headers={ "content-type": "application/json"  }, port=self.port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)


class ParseBodyFormDataTestCasa(TestCase, ServerTestMixin):
    port: int = 50005


class CorsTestCase(ServerTestMixin, HttpRequestMixin, TestCase):
    pass


class HttpClientTestCase(TestCase, ServerTestMixin):
    port: int = 50006


class RouterTestCase(TestCase):
    pass



if __name__ == '__main__':
    unittest.main()
