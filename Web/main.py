from http.server import HTTPServer
from RequestHandler import MyRequestHandler


addr_server = ('192.168.1.42', 3331)
httpd = HTTPServer(addr_server, MyRequestHandler)
httpd.serve_forever()
