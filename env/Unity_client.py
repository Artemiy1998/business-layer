import socket
import json
import time
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost', 9090))

while True:
    name = input('robot name:')
    cmd = input('command:')
    dataToSend = {"flag":0,"name": str(name), "command": str(cmd)}
    dataJson = json.dumps(dataToSend)
    sock.send(dataJson.encode())
    time.sleep(1)


