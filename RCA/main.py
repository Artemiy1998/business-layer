import socket
import logging
import os
import configparser

from common_thread_object import CommonSocket
from switch_thread_object import Switch


logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='RCA.log'
)

logging.info('Program started')

# config
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'configBL.ini'
)
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)

HOST = CONFIG['HOSTS']['Main_host']
BUFFER_SIZE = int(CONFIG['PARAMS']['Buffersize'])
LISTEN = int(CONFIG['PARAMS']['listen'])
PORT_3D_SCENE = int(CONFIG['PORTS']['Port_3d_scene'])
PORT_RCA = int(CONFIG['PORTS']['Port_rca'])
# config end

SWITCH = Switch((HOST, PORT_3D_SCENE))
SWITCH.run()
SERV_SOCK = socket.socket()
SERV_SOCK.setblocking(False)
SERV_SOCK.bind((HOST, PORT_RCA))
SERV_SOCK.listen(LISTEN)

while not SWITCH.exit:
    try:
        conn, address = SERV_SOCK.accept()
        common_conn = CommonSocket(conn, False, False)
        common_conn.start()
        SWITCH.append(common_conn)
        print('Received connection, status:', SWITCH.exit)
    except Exception:
        pass
