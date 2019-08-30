# Standard libs imports
import json
from http import HTTPStatus
from typing import Dict
from wsgiref.headers import Headers

# First party libs imports
from py_sugo.core import CONTENT_TYPE, CONTENT_LENGTH, UTF_8
from py_sugo.request import Request


class Response:
    id: str
    headers: Headers
    request: Request
    status_code: int
    body: bytes

    def __init__(self: 'Response', start_response, request: Request):
        self.request = request
        self.id = request.id
        self._start_response = start_response
        self.headers = Headers()
        self.status_code = 200

    def status(self: 'Response', status_code: int) -> 'Response':
        self.status_code = status_code
        return self

    def json(self: 'Response', data: Dict):
        self.headers.add_header(CONTENT_TYPE, 'application/json')
        return self.send(json.dumps(data).encode(UTF_8))

    def send(self: 'Response', body: bytes):
        self.body = body
        self.headers.add_header(CONTENT_LENGTH, str(len(self.body)))
        self._start_response(self._get_wsgi_http_status(self.status_code), self.headers.items())
        return self.body

    @staticmethod
    def _get_wsgi_http_status(status_code: int) -> str:
        for http_status in HTTPStatus:
            if http_status.value == status_code:
                return '%d %s' % (http_status.value, http_status.phrase)
        raise ValueError("Unsupported HTTP Code: '%d'" % status_code)
