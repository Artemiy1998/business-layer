from random import randint
import socket
import time

sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_client.connect(('localhost', 9099))
sock_client.send(b'f')

while True:

    data = sock_client.recv(1024)
    messages = data.decode()
    print(messages)
    messages = messages.split('|')
    for message in messages:
        if 'e' == message:
            exit()
        if message == '':
            continue
        answer = '\"fanuc\":\"' + message + '\"|'
        time.sleep(1)
        sock_client.send(answer.encode())


