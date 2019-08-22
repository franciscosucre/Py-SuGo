# Standard libs imports
import re
from typing import List, Union, Pattern

# Third party libs imports
from core import HttpMethod
from request import Request
from response import Response
from application import Middleware, RequestHandler

Handler = Union[RequestHandler, Middleware]


class RouteNotFoundException(Exception):
    message: str
    route: str
    method: HttpMethod

    def __init__(self, method: HttpMethod, route: str):
        super(RouteNotFoundException, self).__init__(method, route)
        self.method = method
        self.route = route


class Route:
    url_pattern: str
    method: HttpMethod
    layers: List[Handler] = list()
    regex: Pattern
    current_layer: int = 0

    def __init__(self: 'Route', method: HttpMethod, url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.url_pattern = url_pattern
        self.method = method
        self.regex = re.compile(url_pattern)
        route_handlers: List[Handler] = [first_handler]
        for handler in list(handlers):
            route_handlers.append(handler)
        self.layers = route_handlers

    def handle(self, request: Request, response: Response):
        self.current_layer: int = 0

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

    def add_route(self: 'Router', method: HttpMethod, url_pattern: str, first_handler: Handler, *handlers: Handler):
        matches = [r for r in self.routes if r.method == method and r.url_pattern == url_pattern]
        if matches:
            raise Exception("Already added '%s' '%s' route" % (method, url_pattern))
        route = Route(method, url_pattern, first_handler, *handlers)
        self.routes.append(route)
        return self

    def get(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.add_route(HttpMethod.GET, url_pattern, first_handler, *handlers)
        return self

    def post(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.add_route(HttpMethod.POST, url_pattern, first_handler, *handlers)
        return self

    def put(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.add_route(HttpMethod.POST, url_pattern, first_handler, *handlers)
        return self

    def patch(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.add_route(HttpMethod.POST, url_pattern, first_handler, *handlers)
        return self

    def delete(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.add_route(HttpMethod.POST, url_pattern, first_handler, *handlers)
        return self

    def head(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.add_route(HttpMethod.POST, url_pattern, first_handler, *handlers)
        return self

    def options(self: 'Router', url_pattern: str, first_handler: Handler, *handlers: Handler):
        self.add_route(HttpMethod.POST, url_pattern, first_handler, *handlers)
        return self

    def find_route(self: 'Router', method: HttpMethod, url: str) -> Route:
        # We make a search by method first to limit the choices for the regex filter, that is more resource consuming
        method_matched_routes = [r for r in self.routes if r.method == method]
        [route] = [r for r in method_matched_routes if r.regex.match(url)]
        if not route:
            raise Exception("Route not found: '%s' '%s' " % (method, url))
        return route
