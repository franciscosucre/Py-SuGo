# Standard libs imports
import json
from http import HTTPStatus
from typing import Any, Dict
from wsgiref.headers import Headers

# Third party libs imports
from core import HttpHeader
from request import Request


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
        self.headers.add_header(HttpHeader.CONTENT_TYPE.value, 'application/json')
        self.headers.add_header(HttpHeader.CONTENT_LENGTH.value, str(len(self.body)))
        self._start_response('%d %s' % (http_status.value, http_status.phrase), self.headers.items())
        return self.body

    def _get_http_status(self: 'Response', status_code: int):
        return list(filter(lambda h: h.value == status_code, list(HTTPStatus))).pop()
