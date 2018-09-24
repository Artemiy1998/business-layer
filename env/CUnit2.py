import socket
import time
import sys


sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_client.connect(('localhost', 9099))
sock_client.send(b't')

# Telega imitator.
while True:
    data = sock_client.recv(1024)
    messages = data.decode()
    print(messages)
    messages = messages.split('|')
    for message in messages:
        if 'e' == message:
            sys.exit()
        if not message:
            continue
        answer = f'\"cube\":\" {message} \"|'
        time.sleep(1)
        sock_client.send(answer.encode())
