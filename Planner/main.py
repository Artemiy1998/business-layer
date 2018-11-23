import os
import socket
import sys
import configparser
import logging
import json
import time

from task_loader import TaskLoader
from planner import Planner


# TODO: при отключении клиент адаптера на CUnit, которому была адресована
# последняя команда, начинается спам этой командой, так как в беск. цикле
# вызывается исключение, и так снова и снова.


logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='Planner.log'
)

# config
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'configBL.ini'
)
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)

HOST = CONFIG['HOSTS']['Main_host']
PORT_CL_AD = int(CONFIG['PORTS']['Port_cl_adapter'])
PORT_PLANNER = int(CONFIG['PORTS']['Port_planner'])
PORT_3D_SCENE = int(CONFIG['PORTS']['Port_3d_scene'])
PORT_ROB_AD = int(CONFIG['PORTS']['Port_rca'])
BUFFER_SIZE = int(CONFIG['PARAMS']['Buffersize'])

WHO = 'p'
ROBO_DICT = ['f', 't']
# end config

SOCK_ROB_AD = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    SOCK_ROB_AD.connect((HOST, PORT_ROB_AD))
    SOCK_ROB_AD.send(WHO.encode())
except ConnectionRefusedError:
    logging.error('RCA refused connection')

SOCK_3D_SCENE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    SOCK_3D_SCENE.connect((HOST, PORT_3D_SCENE))
    SOCK_3D_SCENE.send(b'planner')
except ConnectionRefusedError:
    logging.error('Scene3d refused connection')

SOCK_SERV = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK_SERV.bind((HOST, PORT_PLANNER))
SOCK_SERV.listen(1)


# Read all data from socket buffer.
def receive(sock):
    total_data = b''
    try:
        while True:
            recv_data = sock.recv(BUFFER_SIZE)
            if recv_data:
                total_data += recv_data
            else:
                break
    except Exception:
        pass
    return total_data.decode()


planner = Planner(SOCK_ROB_AD, SOCK_3D_SCENE, ROBO_DICT, BUFFER_SIZE)
taskloader = TaskLoader()
count = 0
while True:
    conn, addr = SOCK_SERV.accept()
    conn.setblocking(False)
    while True:
        try:
            messages = receive(conn)
            if messages:
                logging.info(messages)
                print('Command iteration:', count)
            else:
                continue

            messages = messages.split('|')
            for message in messages[:-1]:  # Skip last empty list.
                if message == 'e':
                    for robot in ROBO_DICT:
                        message = f'{robot}: e|'
                        try:
                            print('Send exit message to robots:', message)
                            SOCK_ROB_AD.send(message.encode())
                            time.sleep(1)
                        except ConnectionAbortedError:
                            logging.error('RCA aborted connection')
                    try:
                        print('Send exit message to RCA:', message)
                        SOCK_ROB_AD.send(b'e|')
                    except ConnectionAbortedError:
                        logging.error('RCA aborted connection')
                    logging.info('Planner stopped')
                    sys.exit(0)
                try:
                    print(message)
                    data = json.loads(message)
                    planner.process_complex_task(data, taskloader)
                except ConnectionAbortedError:
                    # logging.error('RCA aborted connection')
                    pass
                except Exception as e:
                    print('Exception:', e)
                    continue
        except ConnectionAbortedError:
            # logging.error('ClientAdapter aborted connection')
            pass
        except ConnectionResetError:
            # logging.error('ClientAdapter reset connection')
            pass
        count += 1

    # TODO: добавить сюда отказоустойчивость при отловке какого либо
    # осключения. чтобы он постоянно не спамил названием этой ошибки.
