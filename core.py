from enum import Enum
from typing import Callable, Any

from request import Request
from response import Response


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


NextFunction = Callable[[], Any]
Middleware = Callable[[Request, Response, NextFunction], Any]
RequestHandler = Callable[[Request, Response], Any]
