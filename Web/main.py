from http.server import HTTPServer
from RequestHandler import MyRequestHandler


addr_server = ('localhost', 3331)
httpd = HTTPServer(addr_server, MyRequestHandler)
httpd.serve_forever()
