from random import randint
import socket

sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_client.connect(('localhost', 9099))
sock_client.send(b't')

while True:
    data = sock_client.recv(1024)
    message = data.decode()
    print(message)
    answer = '\"data\":\"' + message + '\"'
    sock_client.send(answer.encode())