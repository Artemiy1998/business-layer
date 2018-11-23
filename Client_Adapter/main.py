import socket
import configparser
import os

from client_adapter import ClientAdapter


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
PORT_SCENE3D = int(CONFIG['PORTS']['Port_3d_scene'])
BUFFER_SIZE = int(CONFIG['PARAMS']['Buffersize'])
LISTEN_VAR = int(CONFIG['PARAMS']['Listen'])
# end config

# TODO: fix connection to client adapter because send
# localhost != socket.gethostbyname(socket.gethostname())
# If we want to separate client adapter on dedicated server.

# print(socket.gethostbyname(socket.gethostname()))

ADDRESS_CLIENT = (HOST, PORT_CL_AD)
ADDRESS_SCENE3D = (HOST, PORT_SCENE3D)
ADDRESS_PLANNER = (HOST, PORT_PLANNER)

SOCKET_SCENE3D = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_SCENE3D.connect(ADDRESS_SCENE3D)
SOCKET_SCENE3D.send(b'ClAd')

SOCKET_PLANNER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_PLANNER.connect(ADDRESS_PLANNER)

SOCKET_CLIENT_LISTENER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCKET_CLIENT_LISTENER.bind(ADDRESS_CLIENT)
SOCKET_CLIENT_LISTENER.listen(LISTEN_VAR)

MESSAGE_ERROR = b'Error, somebody don\'t be responsible, please read logs!'

# Deal with Unity clients.
CLIENTS = []
while True:
    client_socket_conn, client_socket_address = SOCKET_CLIENT_LISTENER.accept()

    client_adapter = ClientAdapter(ADDRESS_CLIENT, client_socket_conn,
                                   client_socket_address, ADDRESS_SCENE3D,
                                   SOCKET_SCENE3D, ADDRESS_PLANNER,
                                   SOCKET_PLANNER, BUFFER_SIZE, MESSAGE_ERROR,
                                   CLIENTS)
    client_adapter.run()
