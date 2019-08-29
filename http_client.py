# Standard libs imports
import json
import mimetypes
from typing import Any, Dict, Union, Tuple
from http.client import HTTPConnection
from urllib.parse import urlparse
from wsgiref.headers import Headers


class HttpResponse:
    status_code: int
    data: Union[Dict, bytes]
    header: Headers

    def __init__(self, status, headers: Headers, reason: str, url: str, data: Dict = dict()):
        self.status = status
        self.headers = headers
        self.reason = reason
        self.url = url
        self.data = data


class HttpClient:
    default_headers: Dict = {'content-type': 'plain/text'}
    base_url: str

    def __init__(self, default_headers: Dict = default_headers, base_url: str = ''):
        self.default_headers = default_headers if default_headers else dict()
        self.base_url = base_url

    def http_request(self, method: str, path: str, headers: Dict = default_headers, body: Any = None) -> HttpResponse:
        url = urlparse(self.base_url + path)
        connection = HTTPConnection(host=url.netloc, port=url.port)
        combined_headers = self.default_headers.copy()
        if body:
            combined_headers.update({'content-type': str(len(str(body)))})
        combined_headers.update(headers)
        connection.request(method=method, url=url.path, body=body, headers=combined_headers)
        raw_response = connection.getresponse()
        if raw_response.getheader('Content-Type', 'plain/text') == 'application/json':
            response_body = json.loads(raw_response.read())
        else:
            response_body = raw_response.read()
        response = HttpResponse(status=raw_response.status,
                                headers=Headers(raw_response.getheaders()),
                                reason=raw_response.reason,
                                url=raw_response.geturl(),
                                data=response_body)
        return response

    def get(self, path: str, headers: Dict = default_headers) -> HttpResponse:
        return self.http_request('GET', path, headers, None)

    def post(self, path: str, headers: Dict = default_headers, body: Any = None) -> HttpResponse:
        return self.http_request('POST', path, headers, body)

    def patch(self, path: str, headers: Dict = default_headers, body: Any = None) -> HttpResponse:
        return self.http_request('PATCH', path, headers, body)

    def put(self, path: str, headers: Dict = default_headers, body: Any = None) -> HttpResponse:
        return self.http_request('PUT', path, headers, body)

    def delete(self, path: str, headers: Dict = default_headers) -> HttpResponse:
        return self.http_request('DELETE', path, headers, None)

    def options(self, path: str, headers: Dict = default_headers) -> HttpResponse:
        return self.http_request('OPTIONS', path, headers, None)

    def head(self, path: str, headers: Dict = default_headers) -> HttpResponse:
        return self.http_request('HEAD', path, headers, None)

    def get_content_type(self, filename: str) -> str:
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def encode_multipart_formdata(self, fields, files) -> Tuple[str, str]:
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self.get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
