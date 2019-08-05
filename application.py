from urllib.parse import parse_qs

class Application:
    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self.headers = dict()

    def __iter__(self):
        self.read_request_body()
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

    def read_request_body(self):
        try:
            request_body_size = int(self._environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        readbytes = self._environ['wsgi.input'].read(request_body_size) # returns bytes object
        self.raw_body = readbytes.decode('utf-8')      # returns str object

class Request():
    pass

class Response():
    pass
