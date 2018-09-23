import socket
import logging
import os
import configparser

from common_thread_object import CommonSocket
from switch_thread_object import Switch


# logging
logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='RCA.log'
)

logging.info('Program started')

# config
config_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'configBL.ini'
)
config = configparser.ConfigParser()
config.read(config_file)

host = config['HOSTS']['Main_host']
buffer_size = int(config['PARAMS']['Buffersize'])
listen = int(config['PARAMS']['listen'])
port_3d_scene = int(config['PORTS']['Port_3d_scene'])
port_rca = int(config['PORTS']['Port_rca'])
# config end

switch = Switch((host, port_3d_scene))
switch.run()
serv_sock = socket.socket()
serv_sock.setblocking(False)
serv_sock.bind((host, port_rca))
serv_sock.listen(listen)

while not switch.exit:
    try:
        conn, address = serv_sock.accept()
        common_conn = CommonSocket(conn, False, False)
        common_conn.start()
        switch.append(common_conn)
        print(switch.exit)
    except Exception as e:
        print('Exception:', e)
