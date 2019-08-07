import json
from wsgiref.headers import Headers
from typing import Any, Dict
from http import HTTPStatus

from request import Request

class Response():
    id: str
    headers: Headers = Headers()
    request: Request
    status_code: int = 200
    body: Any = dict()

    def __init__(self: 'Response', start_response, request: Request):
        self.request = request
        self.id = request.id
        self._start_response = start_response

    def status(self: 'Response', status_code: int) -> 'Response':
        self.status_code = status_code
        return self

    def json(self: 'Response', data: Dict):
        self.headers.add_header('CONTENT_TYPE', 'application/json')
        self.body = data
        http_status = self._get_http_status(self.status_code)
        self._start_response('%d %s' % (http_status.value, http_status.phrase), self.headers.items())
        string_body: str = json.dumps(data)
        byte_body: bytes = string_body.encode('utf-8')
        return byte_body

    def _get_http_status(self: 'Response', status_code: int):
        return list(filter(lambda h: h.value == status_code, list(HTTPStatus))).pop()