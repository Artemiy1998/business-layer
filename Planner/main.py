""" @author Urazov Dilshod
Documentation for Planner module

@brief Now planner do nothing but transfer

"""

import os
import socket
import sys
import configparser
import logging
import time
# logging


logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='Planner.log')

# config
config_file = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)),
    'configBL.ini')
config = configparser.ConfigParser()
config.read(config_file)

host = config['HOSTS']['Main_host']
port_cl_ad = int(config['PORTS']['Port_cl_adapter'])
port_planner = int(config['PORTS']['Port_planner'])
port_3d_scene = int(config['PORTS']['Port_3d_scene'])
port_rob_ad = int(config['PORTS']['Port_rca'])
buffersize = int(config['PARAMS']['Buffersize'])

who = 'p'
robo_dict = ['f', 't']
# end config

sock_rob_ad = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock_rob_ad.connect((host, port_rob_ad))
    sock_rob_ad.send(who.encode())
except ConnectionRefusedError:
    logging.error('RCA refused connection')


sock_3d_scene = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock_3d_scene.connect((host, port_3d_scene))
    sock_3d_scene.send(b'planner')
except ConnectionRefusedError:
    logging.error('3dscene refused connection')


sock_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_serv.bind((host, port_planner))
sock_serv.listen(1)
conn, addr = sock_serv.accept()


def get_scene():
    sock_3d_scene.send(b'get_scene')


while True:
    global data
    try:
        data = conn.recv(buffersize)

    except ConnectionAbortedError:
        logging.error('ClientAdapter aborted connection')
    message = data.decode()
    #time.sleep(0.001)
    if message != '':
            logging.info(message)
    if message == 'e':
        for robot in robo_dict:
            message = robot + ':' + 'e'
            try:
                sock_rob_ad.send(message.encode())
            except ConnectionAbortedError:
                logging.error('RCA aborted connection')
        try:
            sock_rob_ad.send(b'e')
        except ConnectionAbortedError:
            logging.error('RCA aborted connection')
        logging.info('Planner stopped')
        sys.exit(0)
    try:
        sock_rob_ad.send(data)
    except ConnectionAbortedError:
        logging.error('RCA aborted connection')
