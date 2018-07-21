import socket
import json
import time
from random import randint
from datetime import datetime
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost', 9090))

while True:
    flag = input('flag: ')
    name = input('name: ')
    cmd = input('cmd: ')
    dataToSend = {"flag": flag, "name": str(name), "command": str(cmd)}
    dataJson = json.dumps(dataToSend)
    sock.send(dataJson.encode())
    time.sleep(0.04)


