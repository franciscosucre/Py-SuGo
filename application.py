# Standard libs imports
from threading import Thread
from typing import List

# Third party libs imports
from wsgiref.simple_server import WSGIServer, make_server

from middleware import Middleware, RequestHandler
from request import Request
from response import Response
from server import PySuGoServer


class Application:
    middlewares: List[Middleware]
    current_layer: int
    server: WSGIServer
    server_thread: Thread

    def __init__(self: 'Application', request_handler: RequestHandler):
        self.middlewares = list()
        self.current_layer = 0
        self.request_handler = request_handler

    def __call__(self: 'Application', environ, start_response):
        self.current_layer: int = 0
        request = Request(environ)
        response = Response(start_response, request)

        def next_layer():
            if self.current_layer >= len(self.middlewares):
                return self.request_handler(request, response)
            layer = self.middlewares[self.current_layer]
            self.current_layer += 1
            return layer(request, response, next_layer)

        next_layer()
        yield response.body
        return response.body

    def use_middleware(self: 'Application', middleware: Middleware):
        self.middlewares.append(middleware)

    def listen(self, host='localhost', port=5000, parallel=False):
        self.server = make_server(host, port, self, server_class=PySuGoServer)
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()
        if not parallel:
            self.wait_for_interrupt()

    def is_listening(self) -> bool:
        return self.server_thread.is_alive()

    def wait_for_interrupt(self):
        try:
            while self.is_listening():
                pass
        except (KeyboardInterrupt, SystemExit):
            self.close()

    def close(self):
        self.server.shutdown()
        while self.server_thread.is_alive():
            self.server_thread.join()
        self.server_thread = None
