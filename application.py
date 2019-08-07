# Standard libs imports
from typing import Any, Callable, List, Union

# Third party libs imports
from request import Request
from response import Response

NextFunction = Callable[[], Any]
Middleware = Union[Callable[[Request, Response, NextFunction], Any], Callable[[Request, Response], Any]]


class Application():
    middlewares: List[Middleware] = list()
    current_layer: int = 0

    def __init__(self: 'Application', request_handler: Middleware):
        self.request_handler = request_handler

    def __call__(self: 'Application', environ, start_response):
        self.current_layer: int = 0
        request = Request(environ)
        response = Response(start_response, request)

        def next_handler():
            if self.current_layer >= len(self.middlewares):
                return self.request_handler(request, response)
            layer = self.middlewares[self.current_layer]
            self.current_layer += 1
            return layer(request, response, next_handler)

        yield next_handler()

    def use_middleware(self: 'Application', middleware: Middleware):
        self.middlewares.append(middleware)
