# Standard libs imports
import json
import time
import unittest
import mimetypes
from time import sleep
from typing import Any, Dict, List, Tuple, TextIO, cast
from unittest import TestCase
from http.client import HTTPConnection

# Third party libs imports
from core import GET, PUT, HEAD, POST, PATCH, DELETE, OPTIONS, CONTENT_TYPE
from request import Request
from response import Response
from middleware import (
    Middleware, NextFunction, CorsMiddleware, RequestHandler, parse_body_json,
    parse_body_form_data)
from application import Application
from http_client import HttpClient, HttpResponse


class ServerTestMixin:
    host: str = 'localhost'
    port: int = 50000
    application: Application
    middleware: List[Middleware] = list()

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = Application(cls.get_request_handler())
        for middleware in cls.middleware:
            cls.application.use_middleware(middleware)
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
                "path": request.path
            })

        return request_handler


class HttpRequestMixin:
    host: str = 'localhost'
    port: int = 50000

    @classmethod
    def convert_body_to_bytes(cls, body: Any) -> bytes:
        if isinstance(body, dict):
            return json.dumps(body).encode('utf-8')
        elif isinstance(body, str):
            return body.encode('utf-8')
        elif body is None:
            return ''.encode('utf-8')
        return cast(bytes, body)

    @classmethod
    def get_default_headers(cls, body: bytes):
        return {"content-length": len(body), "content-type": "plain/text"}

    @classmethod
    def http_request(cls, method: str, path: str = '/', headers: Dict = None, body: Any = None, host='localhost', port=50000):
        connection = HTTPConnection(host=host, port=port)
        byte_body = cls.convert_body_to_bytes(body)
        final_headers = cls.get_default_headers(byte_body)
        if headers:
            final_headers.update(headers)
        connection.request(method=method, url=path, body=byte_body, headers=final_headers)
        return connection.getresponse()


class RequestTestCase(ServerTestMixin, HttpRequestMixin, TestCase):
    def test_request_id_should_be_set(self):
        response = self.http_request('GET', '/hello')
        response_body: Dict = json.loads(response.read())
        self.assertIsNotNone(response_body.get('id'))

    def test_request_path_should_be_set(self):
        response = self.http_request('GET', '/hello')
        response_body: Dict = json.loads(response.read())
        self.assertEqual(response_body.get('path'), '/hello')


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


class MiddlewareTestCase(HttpRequestMixin, TestCase):
    def get_first_middleware(self):
        def first_middleware(request: Request, response: Response, next_layer: NextFunction):
            request.body = dict()
            request.body['first'] = True
            next_layer()

        return first_middleware

    def get_second_middleware(self):
        def second_middleware(request: Request, response: Response, next_layer: NextFunction):
            request.body['second'] = True
            next_layer()
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


class ParseBodyFormDataTestCase(HttpRequestMixin, TestCase):
    port: int = 50006
    file: TextIO

    def get_content_type(self, filename: str) -> str:
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def setUp(self) -> None:
        super().setUp()
        self.file = open('README.md', 'r')

    def tearDown(self) -> None:
        super().tearDown()
        self.file.close()

    def encode_multipart_formdata(self, fields: Dict[str, Any], files: Dict[str, TextIO]):
        '''
        Build a multipart/form-data body with generated random boundary.
        '''
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data: List[str] = []
        for key, value in fields.items():
            data.append('--%s' % boundary)
            data.append('Content-Disposition: form-data; name="%s"\r\n' % key)
            if isinstance(value, str):
                data.append(value)
            elif isinstance(value, bytes):
                data.append(value.decode('utf-8'))
            else:
                data.append(str(value))

        for key, file in files.items():
            data.append('--%s' % boundary)
            content = file.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, file.name))
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % self.get_content_type(file.name.lower()))
            data.append(content)
        data.append('--%s--\r\n' % boundary)
        return '\r\n'.join(data), boundary

    def test_should_not_parse_anything_if_content_type_is_not_json(self):
        body, boundary = self.encode_multipart_formdata(fields={"field": True}, files={"file": self.file})

        def handler(request: Request, response: Response):
            self.assertEqual(len(request.body.keys()), 0)
            self.assertEqual(request.raw_body, body.encode('utf-8'))
            return response.json({})

        application = Application(handler)
        application.use_middleware(parse_body_form_data)
        application.listen(port=self.port, parallel=True)

        response = self.http_request('POST', '/', body=body, headers={"content-type": "plain/text"}, port=self.port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)

    def test_should_parse_if_content_type_is_json(self):
        body, boundary = self.encode_multipart_formdata(fields={"field": True}, files={"file": self.file})

        def handler(request: Request, response: Response):
            self.assertTrue(isinstance(request.body, dict))
            self.assertEqual(request.body['fields']['field'], 'True')
            self.assertEqual(request.body['files']['file'].filename, self.file.name)
            return response.json({})

        port = self.port + 1
        application = Application(handler)
        application.use_middleware(parse_body_form_data)
        application.listen(port=port, parallel=True)

        response = self.http_request(method='POST',
                                     path='/',
                                     body=body,
                                     headers={"content-type": 'multipart/form-data; boundary=%s' % boundary},
                                     port=port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)


class CorsTestCase(ServerTestMixin, HttpRequestMixin, TestCase):
    port = 50008
    middleware = [CorsMiddleware.get_handler()]

    @classmethod
    def get_request_handler(cls) -> RequestHandler:
        def handler(request: Request, response: Response):
            body = dict()
            for (key, value) in request.headers.items():
                body[key] = value
            return response.json(body)

        return handler

    def test_should_add_cors_headers(self):
        response = self.http_request(method='GET', path='/', port=self.port)
        body = json.loads(response.read())
        self.assertEqual(response.status, 200)
        self.assertEqual(body.get('access-control-allow-credentials'), CorsMiddleware.access_control_allow_credentials)
        self.assertEqual(body.get('access-control-allow-headers'), CorsMiddleware.access_control_allow_headers)
        self.assertEqual(body.get('access-control-allow-methods'), CorsMiddleware.access_control_allow_methods)
        self.assertEqual(body.get('access-control-allow-origin'), CorsMiddleware.access_control_allow_origin)
        self.assertEqual(body.get('access-control-expose-headers'), CorsMiddleware.access_control_expose_headers)
        self.assertEqual(body.get('access-control-max-age'), CorsMiddleware.access_control_max_age)


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
            res_data = { "method": request.method }
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


class RouterTestCase(TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
