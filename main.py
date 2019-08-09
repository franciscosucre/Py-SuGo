# Standard libs imports
from typing import List, cast, Any, Dict
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

class FileData():
    def __init__(self:'FileData', content: bytes, filename: str, content_type: str):
        self.content = content
        self.filename = filename
        self.content_type = content_type

def parse_body_form_data(request: Request, response: Response, next_layer: NextFunction):
    content_type: str = cast(str,request.headers.get('CONTENT_TYPE'))
    is_form_data = content_type.find('multipart/form-data') >= 0
    if is_form_data:
        form_data: cgi.FieldStorage = cgi.FieldStorage(
            fp=io.BytesIO(request.raw_body),
            environ=request.environ,
            keep_blank_values=True
        )
        field_storages: List[cgi.FieldStorage] = cast(List[cgi.FieldStorage], form_data.list)
        files : List[FileData] = list()
        fields: Dict[str, Any] = dict()

        for element in field_storages:
            value = form_data.getvalue(element.name)
            if element.filename:
                files.append(FileData(value, element.filename, element.type))
            else:
                fields[element.name] = value
        request.body['files'] = files
        request.body['fields'] = fields

    return next_layer()

def parse_body_json(request: Request, response: Response, next_layer: NextFunction):
    content_type: str = cast(str,request.headers.get('CONTENT_TYPE'))
    if content_type.find('application/json') >= 0:
        request.body = json.loads(request.raw_body)
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
