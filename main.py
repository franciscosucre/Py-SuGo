# Third party libs imports
from application import Request, Response, Application, NextFunction
from middleware import parse_body_json, parse_body_form_data, log_request, log_response, handle_errors
from router import Router, HttpMethod


def handle(request: Request, response: Response):
    response.status(201)
    route = router.find_route(HttpMethod.GET, '/hello')
    return route.handle(request, response)

def hello_world(request: Request, response: Response, next_layer: NextFunction):
    print("hello world")
    return next_layer()

def goobye_world(request: Request, response: Response):
    print("hello world")
    return response.json({"hola": "mundo"})



if __name__ == "__main__":
    app = Application(handle)
    app.use_middleware(handle_errors)
    app.use_middleware(log_request)
    app.use_middleware(log_response)
    app.use_middleware(parse_body_json)
    app.use_middleware(parse_body_form_data)
    router = Router()
    router.get('/(?P<what>)', hello_world, goobye_world)
    app.listen()

