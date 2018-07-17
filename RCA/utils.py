import socket
from wrapt import synchronized


@synchronized
class ClientForScene:

    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('', port))
        self.socket.send(b'RCA')

    @synchronized
    def send(self, message):
        self.socket.send(message)
