# Standard libs imports
import random
from io import BufferedReader
from string import (
    digits, octdigits, punctuation, ascii_lowercase, ascii_uppercase)
from typing import Any, List, cast
from urllib.parse import parse_qs
from wsgiref.headers import Headers

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

chars: str = ascii_lowercase + ascii_uppercase + digits + octdigits + punctuation


class Request():
    id: str = ''.join(random.choice(chars) for i in range(30))
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
