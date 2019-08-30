# Standard libs imports
import json
import unittest
from unittest import TestCase
from http.client import HTTPResponse
from test.mixins import ServerTestMixin, HttpRequestMixin

# First party libs imports
from py_sugo.core import GET, PUT
from py_sugo.router import Route, Router, RouteNotFoundException, RouteAlreadyExistsException
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import RequestHandler


class RouterTestCase(ServerTestMixin, HttpRequestMixin, TestCase):
    port = 50010
    router: Router

    @staticmethod
    def simple_handler(request: Request, response: Response):
        return response.json({"method": request.method})

    @staticmethod
    def param_handler(request: Request, response: Response):
        return response.json({"params": request.params, "method": request.method})

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        router = Router()
        router.get('/', cls.simple_handler).post('/', cls.simple_handler)
        router.get('/(?P<param>[^\/]+)', cls.param_handler).post('/:id', cls.param_handler)
        cls.router = router

    @classmethod
    def get_request_handler(cls) -> RequestHandler:
        def request_handler(request: Request, response: Response):
            try:
                route: Route = cls.router.find_route(method=request.method, url=request.path)
                return route.handle(request=request, response=response)
            except RouteNotFoundException:
                return response.status(404).json({"name": RouteNotFoundException.__name__})
            except RouteAlreadyExistsException:
                return response.status(422).json({"name": RouteNotFoundException.__name__})

        return request_handler

    def test_should_find_the_route(self):
        response: HTTPResponse = self.http_request(method=GET, path='/', port=self.port)
        body = json.loads(response.read())
        self.assertEqual(body['method'], GET)
        self.assertIsNone(body.get('params', None))

    def test_should_raise_an_exception_if_route_is_not_found(self):
        response: HTTPResponse = self.http_request(method=PUT, path='/hello/world', port=self.port)
        body = json.loads(response.read())
        self.assertEqual(body['name'], RouteNotFoundException.__name__)

    def test_should_add_params(self):
        response: HTTPResponse = self.http_request(method=GET, path='/hello', port=self.port)
        body = json.loads(response.read())
        self.assertEqual(body['method'], GET)
        self.assertEqual(body['params']['param'], 'hello')


if __name__ == '__main__':
    unittest.main()
