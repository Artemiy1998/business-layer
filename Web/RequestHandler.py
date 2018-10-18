import socket
from http.server import BaseHTTPRequestHandler
import json
import xmltodict


class MyRequestHandler(BaseHTTPRequestHandler):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.104', 9090))

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        post_data = self.rfile.read(int(self.headers.get('content-length')))
        xml = post_data.decode('utf-8')
        dict_ = xmltodict.parse(xml)
        print(dict_)
        in_json = json.dumps(dict_.get('root'))
        print(in_json)

        try:
            MyRequestHandler.sock.send(in_json.encode('utf-8'))
        except BrokenPipeError:
            self._set_response()
            self.wfile.write('client adapter is not working'.format(self.path).encode('utf-8'))
            return

        self._set_response()
        self.wfile.write('ok'.format(self.path).encode('utf-8'))
