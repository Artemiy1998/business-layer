import socket
import json
import time
from random import randint
from datetime import datetime
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('localhost', 9090))

while True:
    '''flag = input('flag: ')
    parallel = input('parallel: ')
    name = input('name: ')
    cmd = input('cmd: ')
    parallel1 = input('parallel: ')
    name1 = input('name: ')
    cmd1 = input('cmd: ')'''
    flag = 0
    parallel = 'q'
    name = 'fanuc'
    cmd = 'cmd9'
    parallel1 = 'q'
    name1 = 'telega'
    cmd1 = 'cmd'
    dataToSend = {"flag": str(flag),"Scenario": [{"parallel": True, "name": str(name), "command": str(cmd)},
                                                 {"parallel": parallel1, "name": str(name1), "command": str(cmd1)},
                                                 {"parallel": parallel1, "name": str(name), "command": "cmd1"},
                                                 {"parallel": parallel1, "name": str(name1), "command": "cmd7"}]}
    dataJson = json.dumps(dataToSend)
    sock.send(dataJson.encode())
    print(dataJson.encode())
    time.sleep(0.04)
    a = input()


