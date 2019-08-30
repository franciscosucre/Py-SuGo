# Standard libs imports
import time
import unittest
import mimetypes
from time import sleep
from typing import Any, Dict, List, TextIO
from unittest import TestCase
from test.mixins import HttpRequestMixin

# First party libs imports
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import parse_body_form_data
from py_sugo.application import Application


class ParseBodyFormDataTestCase(HttpRequestMixin, TestCase):
    port: int = 50006
    file: TextIO

    def get_content_type(self, filename: str) -> str:
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def setUp(self) -> None:
        super().setUp()
        self.file = open('README.md', 'r')

    def tearDown(self) -> None:
        super().tearDown()
        self.file.close()

    def encode_multipart_formdata(self, fields: Dict[str, Any], files: Dict[str, TextIO]):
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
        return '\r\n'.join(data), boundary

    def test_should_not_parse_anything_if_content_type_is_not_json(self):
        body, boundary = self.encode_multipart_formdata(fields={"field": True}, files={"file": self.file})

        def handler(request: Request, response: Response):
            self.assertEqual(len(request.body.keys()), 0)
            self.assertEqual(request.raw_body, body.encode('utf-8'))
            return response.json({})

        application = Application(handler)
        application.use_middleware(parse_body_form_data)
        application.listen(port=self.port, parallel=True)

        response = self.http_request('POST', '/', body=body, headers={"content-type": "plain/text"}, port=self.port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)

    def test_should_parse_if_content_type_is_json(self):
        body, boundary = self.encode_multipart_formdata(fields={"field": True}, files={"file": self.file})

        def handler(request: Request, response: Response):
            self.assertTrue(isinstance(request.body, dict))
            self.assertEqual(request.body['fields']['field'], 'True')
            self.assertEqual(request.body['files']['file'].filename, self.file.name)
            return response.json({})

        port = self.port + 1
        application = Application(handler)
        application.use_middleware(parse_body_form_data)
        application.listen(port=port, parallel=True)

        response = self.http_request(method='POST',
                                     path='/',
                                     body=body,
                                     headers={"content-type": 'multipart/form-data; boundary=%s' % boundary},
                                     port=port)
        application.close()
        sleep(1)
        self.assertEqual(response.status, 200)


if __name__ == '__main__':
    unittest.main()
