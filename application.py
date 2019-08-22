# Standard libs imports
from typing import Any, List, Union, Callable

# Third party libs imports
from wsgiref.simple_server import WSGIServer, make_server

from middleware import Middleware, RequestHandler
from request import Request
from response import Response


class Application:
    middlewares: List[Middleware] = list()
    current_layer: int = 0
    server: WSGIServer

    def __init__(self: 'Application', request_handler: RequestHandler):
        self.request_handler = request_handler

    def __call__(self: 'Application', environ, start_response):
        self.current_layer: int = 0
        request = Request(environ)
        response = Response(start_response, request)

        def next_layer():
            if (self.current_layer >= len(self.middlewares)):
                return self.request_handler(request, response)
            layer = self.middlewares[self.current_layer]
            self.current_layer += 1
            layer(request, response, next_layer)
        next_layer()
        yield str(response.body).encode('utf-8')
        return response.body

    def use_middleware(self: 'Application', middleware: Middleware):
        self.middlewares.append(middleware)

    def listen(self, host='localhost', port= 5000):
        self.server = make_server(host, port, self)
        self.server.serve_forever()
