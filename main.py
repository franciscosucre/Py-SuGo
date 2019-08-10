# Standard libs imports
from wsgiref.simple_server import make_server

# Third party libs imports
from application import Request, Response, Application
from middleware import parse_body_json, parse_body_form_data, log_request, log_response, handle_errors


def handle(request: Request, response: Response):
    response.status(201)
    return response.json({"hola": "mundo"})


if __name__ == "__main__":
    app = Application(handle)
    app.use_middleware(handle_errors)
    app.use_middleware(log_request)
    app.use_middleware(log_response)
    app.use_middleware(parse_body_json)
    app.use_middleware(parse_body_form_data)
    server = make_server('localhost', 5000, app)
    server.serve_forever()
