from enum import Enum


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


class HttpHeader(Enum):
    CONTENT_TYPE = 'Content-Type'
    CONTENT_LENGTH = 'Content-Length'