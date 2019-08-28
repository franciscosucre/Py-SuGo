# Standard libs imports
import json
import unittest
from typing import Dict
from http.client import HTTPConnection

# Third party libs imports
from request import Request
from response import Response
from middleware import RequestHandler
from application import Application


class ApplicationTests(unittest.TestCase):
    host: str = 'localhost'
    port: int = 50000
    application: Application

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = Application(cls.get_request_handler())
        cls.application.listen(cls.host, cls.port)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.application.close()

    @classmethod
    def get_request_handler(cls) -> RequestHandler:
        def request_handler(request: Request, response: Response):
            return response.status(200).json({
                "body": request.body,
                "id": request.id,
                "method": request.method,
                "query": request.query,
                "path": request.path,
            })

        return request_handler

    @classmethod
    def http_request(cls, method: str, path: str = '/', body: Dict = None):
        connection = HTTPConnection(host=cls.host, port=cls.port)
        connection.request(method=method, url=path, body=body)
        return connection.getresponse()

    def test_request_path_should_be_set(self):
        response = self.http_request('GET', '/hello')
        response_body: Dict = json.loads(response.read())
        self.assertEqual(response_body.get('path'), '/hello')


if __name__ == '__main__':
    unittest.main()
