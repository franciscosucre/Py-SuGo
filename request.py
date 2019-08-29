# Standard libs imports
import random
from io import BufferedReader
from string import digits, octdigits, ascii_lowercase, ascii_uppercase
from typing import Any, Dict, List, cast
from urllib.parse import parse_qs
from wsgiref.headers import Headers

# Third party libs imports
from core import HttpHeader

HTTP_HEADERS: List[str] = [
    "A_IM",
    "ACCEPT",
    "ACCEPT_CHARSET",
    "ACCEPT_DATETIME",
    "ACCEPT_ENCODING",
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

chars: str = ascii_lowercase + ascii_uppercase + digits + octdigits


class Request:
    id: str
    environ: dict
    wsgi_input: BufferedReader
    path: str
    method: str
    port: str
    host: str
    protocol: str
    server_name: str
    query: dict
    headers: Headers
    body: Dict
    raw_body: bytes
    params: Dict[str, Any]

    def __init__(self, environ: dict):
        self.id = ''.join(random.choice(chars) for i in range(30))
        self.body = dict()
        self.environ = environ
        self.wsgi_input: BufferedReader = cast(BufferedReader, environ.get('wsgi.input'))
        self.path = environ.get('PATH_INFO', '')
        self.method = environ.get('REQUEST_METHOD', '')
        self.port = environ.get('PORT', '')
        self.host = environ.get('HTTP_HOST', '')
        self.protocol = environ.get('HTTP_PROTOCOL', '')
        self.server_name = environ.get('SERVER_NAME', '')
        self.query = parse_qs(environ.get('QUERY_STRING', ''))
        self.params = dict()
        self.headers = Headers()
        self._parse_http_headers()
        self._read_request_body()

    def _parse_http_headers(self: 'Request'):
        for key in self.environ.keys():
            replaced_key: str = key.replace('HTTP_', '')
            value = self.environ.get(key)

            if replaced_key in HTTP_HEADERS:
                final_key : str = ''
                key_parts = list(map(lambda x: x.capitalize(), replaced_key.split('_')))
                part_count = len(key_parts)
                for i in range(part_count):
                    part = key_parts[i]
                    final_key += part
                    if i + 1 < part_count:
                        final_key += '-'
                self.headers.add_header(final_key, value)

    def _read_request_body(self: 'Request'):
        try:
            request_body_size = int(self.headers.get(HttpHeader.CONTENT_LENGTH.value, '0'))
        except ValueError:
            request_body_size = 0
        self.raw_body = self.wsgi_input.read(request_body_size)
