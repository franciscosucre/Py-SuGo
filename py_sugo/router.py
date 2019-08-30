# Standard libs imports
import re
from typing import List, Union, Pattern

# First party libs imports
from py_sugo.core import GET, PUT, HEAD, POST, PATCH, DELETE, OPTIONS
from py_sugo.request import Request
from py_sugo.response import Response
from py_sugo.middleware import Middleware, RequestHandler

Handler = Union[RequestHandler, Middleware]


class RouteNotFoundException(Exception):
    message: str
    url: str
    method: str

    def __init__(self, method: str, url: str):
        super(RouteNotFoundException, self).__init__(method, url)
        self.method = method
        self.url = url
        self.message = "Route not found: '%s' '%s' " % (method, url)


class RouteAlreadyExistsException(Exception):
    message: str
    url: str
    method: str

    def __init__(self, method: str, url: str):
        super(RouteAlreadyExistsException, self).__init__(method, url)
        self.method = method
        self.url = url
        self.message = "Already added '%s' '%s' route" % (method, url)


class Route:
    url_pattern: str
    method: str
    layers: List[Handler] = list()
    regex: Pattern
    current_layer: int = 0

    def __init__(self: 'Route', method: str, url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.url_pattern = url_pattern
        self.method = method
        self.regex = re.compile("^%s$" % url_pattern)
        route_handlers: List[Handler] = [first_handler]
        for handler in list(handlers):
            route_handlers.append(handler)
        self.layers = route_handlers

    def handle(self, request: Request, response: Response):
        self.current_layer: int = 0
        match = self.regex.match(request.path)
        assert match is not None
        request.params = match.groupdict()

        def next_layer():
            layer = self.layers[self.current_layer]
            self.current_layer += 1
            if self.current_layer >= len(self.layers):
                return layer(request, response)
            else:
                return layer(request, response, next_layer)

        return next_layer()


class Router:
    routes: List[Route] = list()

    def add_route(self: 'Router', method: str, url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        matches = [r for r in self.routes if r.method == method and r.url_pattern == url_pattern]
        if matches:
            raise RouteAlreadyExistsException(method, url_pattern)
        route = Route(method, url_pattern, first_handler, *handlers)
        self.routes.append(route)
        return self

    def get(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        return self.add_route(GET, url_pattern, first_handler, *handlers)

    def post(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        return self.add_route(POST, url_pattern, first_handler, *handlers)

    def put(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        return self.add_route(PUT, url_pattern, first_handler, *handlers)

    def patch(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        return self.add_route(PATCH, url_pattern, first_handler, *handlers)

    def delete(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        return self.add_route(DELETE, url_pattern, first_handler, *handlers)

    def head(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        return self.add_route(HEAD, url_pattern, first_handler, *handlers)

    def options(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler) -> 'Router':
        return self.add_route(OPTIONS, url_pattern, first_handler, *handlers)

    def find_route(self: 'Router', method: str, url: str) -> Route:
        # We make a search by method first to limit the choices for the regex filter, that is more resource consuming
        method_matched_routes = [r for r in self.routes if r.method == method]
        matches = [r for r in method_matched_routes if r.regex.match(url)]
        if not matches:
            raise RouteNotFoundException(method, url)
        return matches.pop()
