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
    flag = 1
    parallel = 'q'
    name = 'fanuc'
    cmd = 'cmd1'
    parallel1 = 'q'
    name1 = 'telega'
    cmd1 = 'cmd2'
    dataToSend = {"flag": "0","Scenario": [{"parallel": True, "name": str(name), "command": str(cmd),"time": str(3)},
                                             {"parallel": parallel1, "name": str(name1), "command": str(cmd1),"time": str(1)},
                                             {"parallel": parallel1, "name": str(name), "command": "cmd3","time": str(3)},
                                             {"parallel": parallel1, "name": str(name1), "command": "cmd4","time": str(3)}]}
    dataJson = json.dumps(dataToSend)
    sock.send(dataJson.encode())
    time.sleep(5)
    #dataToSend1 = {"flag": str(flag), "Scenario": [{"parallel": True, "name": str(name), "command": str(cmd)}]}
    #dataJson1 = json.dumps(dataToSend1)
    #sock.send(dataJson1.encode())
   # data = sock.recv(2048).decode()
   # print("3d: " + data)
    time.sleep(0.04)
    a = input()


