import socket
import json
import time

socket3dScene = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addres3dScene = ('localhost',9093)
socket3dScene.connect(addres3dScene)
socket3dScene.send(b'ClAd')

socketPlanner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addresPlanner = ('localhost',10000)
socketPlanner.connect(addresPlanner)


def dataConvertJsonToStrByte(dataJson):
    dictName = {'fanuc': 'f', 'telega':'t'}
    if dictName.get(dataJson.get('name')) != None:
        dataStr = str(dictName.get(dataJson.get('name')))+':'+dataJson.get('command')
        dataStrByte = dataStr.encode()
        return dataStrByte
    else:
        return False


def sendPlanner(dataJson,sockUnity):
    try:
        dataByteSend = dataConvertJsonToStrByte(dataJson)
        if dataByteSend:
            socketPlanner.send(dataByteSend)
    except ConnectionRefusedError:
        sockUnity.send(b'Error, Connection Refused wait 3 minutes')
        for i in range(3):
            time.sleep(60)
            try:
                socketPlanner.connect(addresPlanner)
                sendPlanner(dataJson, sockUnity)
            except ConnectionRefusedError:
                pass
        sockUnity.send(b'Error, somebody don\'t be responsible, please read logs')
        socket3dScene.send(b'e')
        socket3dScene.close()
        socketPlanner.close()
        sockUnity.close()
        exit()


def send3dScene(dataJson, sockUnity):
    try:
        dataSend = str(dataJson.get('flag'))
        dataByteSend = dataSend.encode()
        socket3dScene.send(dataByteSend)
        dataInto3dScene = socket3dScene.recv(2048)
        print('hui')
        return dataInto3dScene
    except ConnectionRefusedError:
        sockUnity.send(b'Error, Connection Refused wait 3 minutes')
        for i in range(3):
            time.sleep(60)
            try:
                socket3dScene.connect(addres3dScene)
                send3dScene(dataJson,sockUnity)
            except ConnectionRefusedError:
                pass
        sockUnity.send(b'Error, somebody don\'t be responsible, please read logs')
        socket3dScene.close()
        socketPlanner.send(b'e')
        socketPlanner.close()
        sockUnity.close()
        exit()

    except ConnectionResetError:
        sockUnity.send(b'Error, Connection Refused wait 3 minutes')
        for i in range(3):
            time.sleep(60)
            try:
                socket3dScene.connect(addres3dScene)
                send3dScene(dataJson, sockUnity)
            except ConnectionRefusedError:
                pass
        sockUnity.send(b'Error, somebody don\'t be responsible, please read logs')
        socket3dScene.close()
        socketPlanner.send(b'e')
        socketPlanner.close()
        sockUnity.close()
        exit()



socketUnity = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketUnity.bind(('localhost', 9090))
socketUnity.listen(100)
while True:
    clientSocketUnity, addrUnity = socketUnity.accept()
    while True:
        print(addrUnity)
        dataByte = clientSocketUnity.recv(1024)
        print(dataByte)
        dataJson = json.loads(dataByte.decode("utf-8"))
        print(type(dataJson))
        if dataJson.get('flag')==0:
            sendPlanner(dataJson,clientSocketUnity)
        elif dataJson.get('flag') == 1:
            dataSendByte = send3dScene(dataJson)
            clientSocketUnity.send(dataSendByte)
        elif dataJson.get('flag') == 'e':
            socket3dScene.send(b'e')
            socketPlanner.send(b'e')
            socketPlanner.close()
            socket3dScene.close()
            time.sleep(3)
            exit() #planning crash for test builds
    clientSocketUnity.close()


clientSocketUnity.close()
socket3dScene.close()
