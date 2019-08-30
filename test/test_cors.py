# Standard libs imports
import json
import unittest
from unittest import TestCase
from test.mixins import ServerTestMixin, HttpRequestMixin

# First party libs imports
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import CorsMiddleware, RequestHandler


class CorsTestCase(ServerTestMixin, HttpRequestMixin, TestCase):
    port = 50008
    middleware = [CorsMiddleware.get_handler()]

    @classmethod
    def get_request_handler(cls) -> RequestHandler:
        def handler(request: Request, response: Response):
            body = dict()
            for (key, value) in request.headers.items():
                body[key] = value
            return response.json(body)

        return handler

    def test_should_add_cors_headers(self):
        response = self.http_request(method='GET', path='/', port=self.port)
        body = json.loads(response.read())
        self.assertEqual(response.status, 200)
        self.assertEqual(body.get('access-control-allow-credentials'), CorsMiddleware.access_control_allow_credentials)
        self.assertEqual(body.get('access-control-allow-headers'), CorsMiddleware.access_control_allow_headers)
        self.assertEqual(body.get('access-control-allow-methods'), CorsMiddleware.access_control_allow_methods)
        self.assertEqual(body.get('access-control-allow-origin'), CorsMiddleware.access_control_allow_origin)
        self.assertEqual(body.get('access-control-expose-headers'), CorsMiddleware.access_control_expose_headers)
        self.assertEqual(body.get('access-control-max-age'), CorsMiddleware.access_control_max_age)


if __name__ == '__main__':
    unittest.main()
