# Standard libs imports
import json
import time
import mimetypes
from typing import Any, Dict, List, Tuple, Union, TextIO, cast
from http.client import HTTPResponse, HTTPConnection
from urllib.parse import urlparse
from wsgiref.headers import Headers

# First party libs imports
from py_sugo.core import (
    GET, PUT, HEAD, POST, PATCH, UTF_8, DELETE, OPTIONS, CONTENT_TYPE,
    CONTENT_LENGTH)


class HttpResponse:
    status_code: int
    data: Union[Dict, bytes]
    header: Headers
    message: str
    url: str

    def __init__(self, status_code: int, headers: Headers, message: str, url: str, data: Dict = None):
        self.status_code = status_code
        self.headers = headers
        self.message = message
        self.url = url
        self.data = data if data is not None else dict()


class HttpClient:
    default_headers: Dict = {CONTENT_TYPE: 'plain/text'}
    base_url: str

    def __init__(self, default_headers: Dict = default_headers, base_url: str = ''):
        self.default_headers = default_headers if default_headers else dict()
        self.base_url = base_url

    def http_request(self,
                     method: str,
                     path: str,
                     headers: Dict = None,
                     body: Any = None,
                     fields: Dict[str, Any] = None,
                     files: Dict[str, TextIO] = None) -> HttpResponse:
        complete_url = self.base_url + path
        url_elements = urlparse(complete_url)
        connection = HTTPConnection(host=url_elements.hostname, port=url_elements.port)
        combined_headers = self.default_headers.copy()
        byte_body: bytes = ''.encode(UTF_8)
        if files or fields:
            byte_body, boundary = self.encode_multipart_formdata(files=files if files else dict(), fields=fields if fields else dict())
            combined_headers[CONTENT_TYPE] = 'multipart/form-data; boundary=%s' % boundary
        elif body:
            byte_body = self.convert_body_to_bytes(body=body)
        combined_headers.update({CONTENT_LENGTH: str(len(byte_body))})
        if headers is not None:
            combined_headers.update(headers)
        connection.request(method=method, url=url_elements.path, body=byte_body, headers=combined_headers)
        native_response: HTTPResponse = connection.getresponse()
        byte_response: bytes = native_response.read()
        if byte_response and native_response.getheader(CONTENT_TYPE, 'plain/text') == 'application/json':
            response_body = json.loads(byte_response)
        else:
            response_body = byte_response
        response = HttpResponse(status_code=native_response.status,
                                headers=Headers(native_response.getheaders()),
                                message=native_response.reason,
                                url=complete_url,
                                data=response_body)
        return response

    def get(self, path: str, headers: Dict = None) -> HttpResponse:
        return self.http_request(GET, path=path, headers=headers)

    def post(self, path: str, headers: Dict = None, body: Any = None, fields: Dict[str, Any] = None, files: Dict[str, TextIO] = None) -> HttpResponse:
        return self.http_request(POST, path=path, headers=headers, body=body, fields=fields, files=files)

    def patch(self, path: str, headers: Dict = None, body: Any = None, fields: Dict[str, Any] = None,
              files: Dict[str, TextIO] = None) -> HttpResponse:
        return self.http_request(PATCH, path=path, headers=headers, body=body, fields=fields, files=files)

    def put(self, path: str, headers: Dict = None, body: Any = None, fields: Dict[str, Any] = None, files: Dict[str, TextIO] = None) -> HttpResponse:
        return self.http_request(PUT, path=path, headers=headers, body=body, fields=fields, files=files)

    def delete(self, path: str, headers: Dict = None) -> HttpResponse:
        return self.http_request(DELETE, path=path, headers=headers)

    def options(self, path: str, headers: Dict = None) -> HttpResponse:
        return self.http_request(OPTIONS, path=path, headers=headers)

    def head(self, path: str, headers: Dict = None) -> HttpResponse:
        return self.http_request(HEAD, path=path, headers=headers)

    def convert_body_to_bytes(cls, body: Any) -> bytes:
        if isinstance(body, dict):
            return json.dumps(body).encode(UTF_8)
        elif isinstance(body, str):
            return body.encode(UTF_8)
        elif body is None:
            return ''.encode(UTF_8)
        return cast(bytes, body)

    def get_content_type(self, filename: str) -> str:
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def encode_multipart_formdata(self, fields: Dict[str, Any], files: Dict[str, TextIO]) -> Tuple[bytes, str]:
        '''
        Build a multipart/form-data body with generated random boundary.
        '''
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data: List[str] = []
        for key, value in fields.items():
            data.append('--%s' % boundary)
            data.append('Content-Disposition: form-data; name="%s"\r\n' % key)
            if isinstance(value, str):
                data.append(value)
            elif isinstance(value, bytes):
                data.append(value.decode('utf-8'))
            else:
                data.append(str(value))

        for key, file in files.items():
            data.append('--%s' % boundary)
            content = file.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, file.name))
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % self.get_content_type(file.name.lower()))
            data.append(content)
        data.append('--%s--\r\n' % boundary)
        return '\r\n'.join(data).encode(UTF_8), boundary
