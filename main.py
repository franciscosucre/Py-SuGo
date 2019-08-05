from application import Application

from wsgiref.simple_server import make_server, WSGIServer

class Server(WSGIServer):
    pass
    def finish_request(self, request, client_address):
        return super().finish_request(request, client_address)





if __name__ == "__main__":
    server = make_server('localhost', 5000, Application)
    server.serve_forever()
