from http.server import HTTPServer
from RequestHandler import MyRequestHandler


addr_server = ('127.0.0.1', 3333)
httpd = HTTPServer(addr_server, MyRequestHandler)
httpd.serve_forever()
