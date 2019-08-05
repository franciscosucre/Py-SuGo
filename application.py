from urllib.parse import parse_qs
from email.message import Message

HTTP_HEADERS = [
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
    def __init__(self, environ: dict):
        self.wsgi_input = environ.get('wsgi.input')
        self.path = environ.get('PATH_INFO')
        self.remote_address = environ.get('PATH_INFO')
        self.port = environ.get('PORT', '')
        self.query = parse_qs(environ.get('QUERY_STRING', ''))
        self.content_length = environ.get('CONTENT_LENGTH', '')
        self.headers = dict()
        keys = list(map(lambda x: x.replace('HTTP_', ''),  environ.keys()))
        for key in filter(lambda key: key in HTTP_HEADERS, keys):
            self.headers[key.replace('HTTP_', '')] = environ.get(key)
        self._read_request_body()

    def _read_request_body(self):
        try:
            request_body_size = int(self.headers.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        readbytes = self.wsgi_input.read(request_body_size)  # returns bytes object
        self.raw_body = readbytes.decode('utf-8')  # returns str object




class Application:
    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self.headers = dict()

    def __iter__(self):
        request = Request(self._environ)
        
        body = b'Hello world!\n'
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        query = parse_qs(self._environ.get('QUERY_STRING', ''))
        self._start_response(status, headers)
        yield body

    def set_header(self, key, value):
        self.headers[key] = value

    def get_header(self, key):
        return self.header.get(key)

    


class Response():
    pass
