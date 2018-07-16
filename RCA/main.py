import os, sys
import socket
import threading
from collections import deque

from .utils import ClientForScene

# config
host = ''
size = 1024
port_rca = 9099
port_3d_scene = 9093
# config end

#TODO 1. Фиксировать изменения сообщения роботам, чтобы отправлять только при изменении, а не спамить
#TODO 2. Проблема перезаписывания планером сообщения до отправки роботу
#TODO 3. Рефакторинг
#TODO 4. Логирование


def listen_to_robot(client, who, client_for_scene, queue_messages):

    while True:

        if len(list(queue_messages)) != 0 and list(queue_messages)[0][0] == who:
            cmd = queue_messages.popleft()[1]
            client.send(cmd.encode())
            if cmd == 'e':
                sys.exit(0)

            data = client.recv(size)

            if data:
                client_for_scene.send(data)
            else:
                raise socket.error('Client disconnected')



def listen_to_planner(client, queue_messages):
    while True:

        data = client.recv(size)
        message = data.decode()

        if data:

            if message == 'e':
                os._exit(0)

            queue_messages.append(message.split(':'))

        else:
            raise socket.error('Client disconnected')


queue_messages = deque()
client_for_scene = ClientForScene(port_3d_scene)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port_rca))
sock.listen(5)

while True:
    client, address = sock.accept()
    who = client.recv(size).decode()
    if who != 'p':

        threading.Thread(target = listen_to_robot, args = (client, who, client_for_scene, queue_messages)).start()
    else:
        threading.Thread(target = listen_to_planner, args=(client, queue_messages)).start()


