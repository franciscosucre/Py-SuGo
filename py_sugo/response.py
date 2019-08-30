# Standard libs imports
import json
from http import HTTPStatus
from typing import Dict
from wsgiref.headers import Headers

# First party libs imports
from py_sugo.core import CONTENT_TYPE, CONTENT_LENGTH
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
        http_status = self._get_http_status(self.status_code)
        string_body: str = json.dumps(data)
        self.body = bytes(string_body, 'utf-8')
        self.headers.add_header(CONTENT_TYPE, 'application/json')
        self.headers.add_header(CONTENT_LENGTH, str(len(self.body)))
        self._start_response('%d %s' % (http_status.value, http_status.phrase), self.headers.items())
        return self.body

    def _get_http_status(self: 'Response', status_code: int):
        return list(filter(lambda h: h.value == status_code, list(HTTPStatus))).pop()
