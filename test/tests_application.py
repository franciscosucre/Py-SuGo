# Standard libs imports
import json
import unittest
from unittest import TestCase
from test.mixins import HttpRequestMixin

# First party libs imports
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import NextFunction
from py_sugo.application import Application


class MiddlewareTestCase(HttpRequestMixin, TestCase):
    def get_first_middleware(self):
        def first_middleware(request: Request, response: Response, next_layer: NextFunction):
            request.body = dict()
            request.body['first'] = True
            next_layer()

        return first_middleware

    def get_second_middleware(self):
        def second_middleware(request: Request, response: Response, next_layer: NextFunction):
            request.body['second'] = True
            next_layer()
            self.assertEqual(request.body['handler'], True)

        return second_middleware

    def test_should_run_added_middleware(self):
        def request_handler(request: Request, response: Response):
            return response.status(201).json(request.body)

        app = Application(request_handler)
        app.use_middleware(self.get_first_middleware())
        app.listen(port=50002, parallel=True)
        response = self.http_request('GET', '/', port=50002)
        app.close()
        body = json.loads(response.read())
        self.assertTrue(body.get('first'))

    def test_should_handle_the_route_then_continue_the_middleware(self):
        def request_handler(request: Request, response: Response):
            request.body['handler'] = True
            self.assertTrue(request.body['second'])
            return response.status(201).json(request.body)

        app = Application(request_handler)
        app.use_middleware(self.get_first_middleware())
        app.use_middleware(self.get_second_middleware())
        app.listen(port=50003, parallel=True)
        response = self.http_request('GET', '/', port=50003)
        app.close()
        body = json.loads(response.read())
        self.assertTrue(body.get('first'))
        self.assertTrue(body.get('second'))


if __name__ == '__main__':
    unittest.main()
