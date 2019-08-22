# Third party libs imports
from application import Application
from middleware import parse_body_json, parse_body_form_data, log_request, log_response, handle_errors, NextFunction
from request import Request
from response import Response
from router import Router


def hello_world(request: Request, response: Response, next_layer: NextFunction):
    print("hello world")
    return next_layer()


def goobye_world(request: Request, response: Response):
    print("hello world")
    return response.json({"hola": "mundo"})


router = Router()
router.get('/(?P<what>[^\/]+)', hello_world, goobye_world)


def handle(request: Request, response: Response):
    route = router.find_route(request.method, request.path)
    return route.handle(request, response)


if __name__ == "__main__":
    app = Application(handle)
    app.use_middleware(handle_errors)
    app.use_middleware(log_request)
    app.use_middleware(log_response)
    app.use_middleware(parse_body_json)
    app.use_middleware(parse_body_form_data)

    app.listen()

