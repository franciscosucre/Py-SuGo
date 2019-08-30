# Standard libs imports
import json
from typing import Any, Dict, List, cast
from http.client import HTTPConnection

# First party libs imports
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import Middleware, RequestHandler
from py_sugo.application import Application


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
