import socket
from http.server import BaseHTTPRequestHandler
import json
import xmltodict


class MyRequestHandler(BaseHTTPRequestHandler):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.121', 9090))

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        data_to_send = {
            'flag': str(1),
            'name': 'get_scene',
            'Scenario': []
        }
        data_json = json.dumps(data_to_send)
        MyRequestHandler.sock.send(data_json.encode('utf-8'))
        b = MyRequestHandler.sock.recv(10000)
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        post_data = self.rfile.read(int(self.headers.get('content-length')))
        xml = post_data.decode('utf-8')
        dict_ = xmltodict.parse(xml)
        a = dict(dict_.get('root'))
        a["Scenario"] = a["Scenario"]["element"]
        print(a)
        in_json = json.dumps(a)
        print(in_json)

        try:
            MyRequestHandler.sock.send(in_json.encode('utf-8'))
        except BrokenPipeError:
            self._set_response()
            self.wfile.write('client adapter is not working'.format(self.path).encode('utf-8'))
            return

        self._set_response()
        self.wfile.write('ok'.format(self.path).encode('utf-8'))
