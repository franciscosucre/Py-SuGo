# Standard libs imports
import io
import cgi
import json
import logging
import traceback
from typing import Any, Dict, List, Callable
from datetime import datetime

# First party libs imports
from py_sugo.core import CONTENT_TYPE
from py_sugo.request import Request
from py_sugo.response import Response

NextFunction = Callable[[], Any]
Middleware = Callable[[Request, Response, NextFunction], Any]
RequestHandler = Callable[[Request, Response], Any]

logger = logging.Logger('APP_LOGGER')


class FileData():
    def __init__(self: 'FileData', content: bytes, filename: str, content_type: str):
        self.content = content
        self.filename = filename
        self.content_type = content_type


def parse_body_form_data(request: Request, response: Response, next_layer: NextFunction):
    content_type = request.headers.get(CONTENT_TYPE)
    assert content_type is not None
    is_form_data = content_type.find('multipart/form-data') >= 0
    if is_form_data:
        form_data: cgi.FieldStorage = cgi.FieldStorage(fp=io.BytesIO(request.raw_body), environ=request.environ, keep_blank_values=True)
        assert form_data.list is not None
        field_storages: List[cgi.FieldStorage] = form_data.list
        keys = form_data.keys()
        files: Dict[str, FileData] = dict()
        fields: Dict[str, Any] = dict()

        for element in field_storages:
            name: str = element.disposition_options.get('name', '')
            value: Any = form_data.getvalue(name)
            if element.filename:
                files[name] = FileData(value, element.filename, element.type)
            else:
                fields[name] = value

        request.body['files'] = files
        request.body['fields'] = fields

    return next_layer()


def parse_body_json(request: Request, response: Response, next_layer: NextFunction):
    content_type: str = request.headers.get(CONTENT_TYPE, '')
    if content_type.find('application/json') >= 0 and request.raw_body:
        request.body = json.loads(request.raw_body)
    return next_layer()


def handle_errors(request: Request, response: Response, next_layer: NextFunction):
    try:
        return next_layer()
    except Exception as exception:
        log_format: str = "%s Error Response (%s): %s %s --> status: %d | body: %s"
        req_id = request.id
        method = request.method
        path = request.path
        keys = dir(exception)
        body = dict()
        for key in keys:
            value = getattr(exception, key)
            if not key.startswith('__') and not callable(value):
                body[key] = value
        body['traceback'] = traceback.format_exc()
        body['message'] = getattr(exception, 'message', repr(exception))
        status_code = getattr(exception, 'status_code', 500)
        now = datetime.now().isoformat()
        logger.error(log_format, now, req_id, method, path, status_code, str(body))
        response.status(status_code)
        response.json(body)
        return


def log_request(request: Request, response: Response, next_layer: NextFunction):
    log_format: str = "%s Request (%s): %s %s --> body: %s | query: %s "
    req_id = request.id
    method = request.method
    path = request.path
    body = str(request.body)
    query = str(request.query)
    now = datetime.now().isoformat()
    logger.info(log_format, now, req_id, method, path, body, query)
    return next_layer()


def log_response(request: Request, response: Response, next_layer: NextFunction):
    next_layer()
    log_format: str = "%s Response (%s): %s %s --> status: %d | body: %s"
    req_id = request.id
    method = request.method
    path = request.path
    body = str(response.body)
    query = str(request.query)
    status_code = response.status_code
    now = datetime.now().isoformat()
    logger.info(log_format, now, req_id, method, path, status_code, body)
    return


class CorsMiddleware:
    access_control_allow_credentials = 'true'
    access_control_allow_headers = ''
    access_control_allow_methods = 'GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS'
    access_control_allow_origin = '*'
    access_control_expose_headers = 'authorization'
    access_control_max_age = '2592000'

    @classmethod
    def get_handler(cls):
        middleware = CorsMiddleware()

        def fn(request: Request, response: Response, next_layer: NextFunction):
            request.headers.add_header('access-control-allow-credentials', middleware.access_control_allow_credentials)
            request.headers.add_header('access-control-allow-headers', middleware.access_control_allow_headers)
            request.headers.add_header('access-control-allow-methods', middleware.access_control_allow_methods)
            request.headers.add_header('access-control-allow-origin', middleware.access_control_allow_origin)
            request.headers.add_header('access-control-expose-headers', middleware.access_control_expose_headers)
            request.headers.add_header('access-control-max-age', middleware.access_control_max_age)
            return next_layer()

        return fn
