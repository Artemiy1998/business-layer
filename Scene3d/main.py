from threading import  Thread
from Scene3d.def_planner import planner_func
from Scene3d.def_rca import rca_func
from Scene3d.def_client_adapter import client_adapter_func
from Scene3d.utils import json_data
import socket
import os
import configparser
import logging
# config
logging.info('3dScene start')
config_file = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)),
    'configBL.ini')
config = configparser.ConfigParser()
config.read(config_file)
host = config['HOSTS']['Main_host']
port_3d_scene = int(config['PORTS']['Port_3d_scene'])
size = 1024
# config end

sock_main = socket.socket()
sock_main.bind((host, port_3d_scene))
sock_main.listen(3)

logging.basicConfig(format = u' %(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG)

while True:
    client, address = sock_main.accept()
    logging.info('Connect ' + address)
    who_is_it = client.recv(1024).decode()

    if who_is_it == 'planner':
        planer_thread = Thread(target=planner_func, args=(client, json_data))
        logging.info(who_is_it + ' connect')
        planer_thread.start()
        logging.info('Thread for ' + who_is_it + ' start')
    elif who_is_it == 'RCA':
        rca_thread = Thread(target=rca_func, args=(client, json_data))
        logging.info(who_is_it + ' connect')
        rca_thread.start()
        logging.info('Thread for ' + who_is_it + ' start')
    elif who_is_it == 'ClAd':
        client_adapter_thread = Thread(target=client_adapter_func, args=(client, json_data))
        logging.info(who_is_it + ' connect')
        client_adapter_thread.start()
        logging.info('Thread for ' + who_is_it + ' start')
    else:
        continue



