""" @author Urazov Dilshod
Documentation for Robot Control Adapter module

@brief RCA module performs the communication of Business Layer with Computer Unit

"""

import os
import sys
import socket
import threading
from collections import deque
from RCA.utils import ClientForScene
import configparser
import logging

# logging
logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='RCA.log')

logging.info("Program started")

# config
config_file = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)),
    'configBL.ini')
config = configparser.ConfigParser()
config.read(config_file)

host = config['HOSTS']['Main_host']
buffersize = int(config['PARAMS']['Buffersize'])
port_3d_scene = int(config['PORTS']['Port_3d_scene'])
port_rca = int(config['PORTS']['Port_rca'])
# config end


def listen_to_robot(client, who, client_for_scene, queue_messages):
    """@brief Function representing the activity of a separate stream for a particular robot

       @param client current client of RCA thread
       @param who identifier of thread
       @param client_for_scene thread-safe client connected to 3dscene
       @param queue_messages thread-safe queue for messages to be sent to robots
    """

    while True:
        if len(queue_messages) != 0:
            left_message = queue_messages[0]
            if left_message[0] == who:
                cmd = queue_messages.popleft()[1]

                logging.debug('Command to ' + who + ': ' + 'cmd')
                try:
                    client.send(cmd.encode())
                except ConnectionAbortedError:
                    logging.error(who + ' disconnected')

                if cmd == 'e':
                    logging.debug('Thread_' + who + ' is closed')
                    sys.exit(0)

                data = client.recv(buffersize)

                logging.info('Message from ' + who + ':' + data.decode())

                if data:
                    client_for_scene.send(data)
                else:
                    logging.error(who + ' disconnected')


def listen_to_planner(client, queue_messages):
    """@brief Function representing the activity of Planner thread

       @param client current client of RCA thread
       @param queue_messages thread-safe queue for messages to be sent to robots
    """
    while True:

        data = client.recv(buffersize)
        message = data.decode()
        logging.info('Message: ' + message)
        if data:

            if message == 'e':
                logging.debug('Program stopped')
                os._exit(0)

            queue_messages.append(message.split(':'))

        else:
            logging.error('Planner disconnected')


queue_messages = deque()
client_for_scene = ClientForScene(port_3d_scene)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port_rca))
sock.listen(5)

while True:
    client, address = sock.accept()
    who = client.recv(buffersize).decode()
    logging.info(who + ' is connected')
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
