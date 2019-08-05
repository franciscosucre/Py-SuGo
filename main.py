from application import Application, Request, Response, NextFunction
import json
from wsgiref.simple_server import make_server, WSGIServer


class Server(WSGIServer):
    pass

    def finish_request(self, request, client_address):
        return super().finish_request(request, client_address)


def handle(request: Request, response: Response, next=None):
    response.status(201)
    return response.json({"hola": "mundo"})


def parse_body_json(request: Request, response: Response, next_handler: NextFunction):
    try:
        request.body = json.loads(request.raw_body)
    except:
        request.body = dict()
    return next_handler()

def log_response(request: Request, response: Response, next_handler: NextFunction):
    result = next_handler()
    print(response.body)
    return result


if __name__ == "__main__":
    app = Application(handle)
    app.use_middleware(log_response)
    app.use_middleware(parse_body_json)
    server = make_server('localhost', 5000, app)
    server.serve_forever()
