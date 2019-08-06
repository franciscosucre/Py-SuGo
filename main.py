# Standard libs imports
import json
from wsgiref.simple_server import WSGIServer, make_server

# Third party libs imports
from application import Request, Response, Application, NextFunction


def handle(request: Request, response: Response):
    response.status(201)
    return response.json({"hola": "mundo"})


def parse_body_json(request: Request, response: Response, next_layer: NextFunction):
    try:
        request.body = json.loads(request.raw_body)
    except json.JSONDecodeError as e:
        request.body = dict()
    return next_layer()


def log_response(request: Request, response: Response, next_layer: NextFunction):
    next_layer()
    print(response.body)
    return


if __name__ == "__main__":
    app = Application(handle)
    app.use_middleware(log_response)
    app.use_middleware(parse_body_json)
    server = make_server('localhost', 5000, app)
    server.serve_forever()
