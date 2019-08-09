# Standard libs imports
from typing import List, cast
import json
from wsgiref.simple_server import WSGIServer, make_server
import cgi
import os
import sys
import io

# Third party libs imports
from application import Request, Response, Application, NextFunction


def handle(request: Request, response: Response):
    response.status(201)
    return response.json({"hola": "mundo"})

def parse_body_form_data(request: Request, response: Response, next_layer: NextFunction):
    content_type: str = cast(str,request.headers.get('CONTENT_TYPE'))
    is_form_data = content_type.find('multipart/form-data') >= 0
    if is_form_data:
        form_data = cgi.FieldStorage(
            fp=io.BytesIO(request.raw_body),
            environ=request.environ,
            keep_blank_values=True
        )
        
        field_storages: List[cgi.FieldStorage] = cast(List[cgi.FieldStorage], form_data.list)
        request.files = list()
        request.fields = dict()

        for element in field_storages:
            value = form_data.getvalue(element.name)
            if element.filename:
                request.files.append(element)
            else:
                request.fields[element.name] = value
            
        pass

    return next_layer()

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
    app.use_middleware(parse_body_form_data)
    server = make_server('localhost', 5000, app)
    server.serve_forever()
