""" @author Urazov Dilshod
Documentation for Robot Control Adapter module.

@brief RCA module performs the communication of Business Layer with Computer Unit.

"""

import os
import sys
import socket
import threading
from collections import deque
from RCA.utils import ClientForScene
import configparser

# config
config_file = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)),
    'configRCA.ini')
config = configparser.ConfigParser()
config.read(config_file)

host = config['HOSTS']['Main_host']
buffersize = int(config['PARAMS']['Buffersize'])
port_3d_scene = int(config['PORTS']['Port_3d_scene'])
port_rca = int(config['PORTS']['Port_rca'])
# config end


def listen_to_robot(client, who, client_for_scene, queue_messages):

    while True:
        if len(queue_messages) != 0:
            left_message = queue_messages[0]
            if left_message[0] == who:
                cmd = queue_messages.popleft()[1]
                client.send(cmd.encode())
                if cmd == 'e':
                    sys.exit(0)

                data = client.recv(buffersize)

                if data:
                    client_for_scene.send(data)
                else:
                    raise socket.error('Client disconnected')


def listen_to_planner(client, queue_messages):
    while True:

        data = client.recv(buffersize)
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
    who = client.recv(buffersize).decode()
    if who != 'p':

        threading.Thread(
            target=listen_to_robot,
            args=(
                client,
                who,
                client_for_scene,
                queue_messages)).start()
    else:
        threading.Thread(
            target=listen_to_planner, args=(
                client, queue_messages)).start()
