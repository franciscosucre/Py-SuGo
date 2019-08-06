# Standard libs imports
import json
from email.message import Message
from http import HTTPStatus
from io import BufferedReader
from typing import Any, Callable, Dict, List, Optional, Tuple, cast, Union, Iterable
from urllib.parse import parse_qs
from wsgiref.headers import Headers
from wsgiref.util import is_hop_by_hop

HTTP_HEADERS: List[str] = [
    "A_IM",
    "ACCEPTACCEPT_CHARSETACCEPT_DATETIMEACCEPT_ENCODING",
    "ACCEPT_LANGUAGE",
    "ACCESS_CONTROL_REQUEST_METHOD",
    "ACCESS_CONTROL_REQUEST_HEADERS",
    "AUTHORIZATION",
    "CACHE_CONTROL",
    "CONNECTION",
    "CONTENT_LENGTH",
    "CONTENT_MD5",
    "CONTENT_TYPE",
    "COOKIE",
    "DATE",
    "EXPECT",
    "FORWARDED",
    "FROM",
    "HOST",
    "HTTP2_SETTINGS",
    "IF_MATCH",
    "IF_MODIFIED_SINCE",
    "IF_NONE_MATCH",
    "IF_RANGE",
    "IF_UNMODIFIED_SINCE",
    "MAX_FORWARDS",
    "ORIGIN",
    "PRAGMA",
    "PROXY_AUTHORIZATION",
    "RANGE",
    "REFERER",
    "TE",
    "USER_AGENT",
    "UPGRADE",
    "VIA",
    "WARNING",
]


class Request():
    headers: Headers = Headers()
    body: Any = dict()

    def __init__(self, environ: dict):
        self.wsgi_input: BufferedReader = cast(BufferedReader, environ.get('wsgi.input'))
        self.path = environ.get('PATH_INFO')
        self.port = environ.get('PORT', '')
        self.query = parse_qs(environ.get('QUERY_STRING', ''))
        for key in environ.keys():
            replaced_key = key.replace('HTTP_', '')
            if replaced_key in HTTP_HEADERS:
                self.headers.add_header(replaced_key, environ.get(key))
        self._read_request_body()

    def _read_request_body(self: 'Request'):
        try:
            request_body_size = int(self.headers.get('CONTENT_LENGTH', '0'))
        except (ValueError):
            request_body_size = 0
        readbytes = self.wsgi_input.read(request_body_size)  # returns bytes object
        self.raw_body = readbytes.decode('utf-8')  # returns str object


class Response():
    headers: Headers = Headers()
    request: Request
    status_code: int = 200
    body: Any = dict()
    bytes_body: bytes

    def __init__(self, start_response, request: Request):
        self.request = request
        self._start_response = start_response

    def status(self: 'Response', status_code: int) -> 'Response':
        self.status_code = status_code
        return self

    def json(self: 'Response', data: Dict):
        self.headers.add_header('CONTENT_TYPE', 'application/json')
        self.body = data
        string_body: str = json.dumps(data)
        self.bytes_body = string_body.encode('utf-8')
        self._start_response('200 OK', self.headers.items())
        return self.bytes_body


NextFunction = Callable[[], Any]
Middleware = Union[Callable[[Request, Response, NextFunction], Any], Callable[[Request, Response], Any]]


class Application():
    middlewares: List[Middleware] = list()
    current_layer: int = 0

    def __init__(self: 'Application', request_handler: Middleware):
        self.request_handler = request_handler

    def __call__(self: 'Application', environ, start_response):
        self.current_layer: int = 0
        request = Request(environ)
        response = Response(start_response, request)

        def next_layer():
            if (self.current_layer >= len(self.middlewares)):
                return self.request_handler(request, response)
            layer = self.middlewares[self.current_layer]
            self.current_layer += 1
            layer(request, response, next_layer)
        next_layer()
        yield str(request.body).encode('utf-8')
        return request.body

    def use_middleware(self: 'Application', middleware: Middleware):
        self.middlewares.append(middleware)
