import socket
import configparser
import os
import logging

from client_adapter import ClientAdapter


# config
config_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'configBL.ini'
)
config = configparser.ConfigParser()
config.read(config_file)
host = config['HOSTS']['Main_host']
port_cl_ad = int(config['PORTS']['Port_cl_adapter'])
port_planner = int(config['PORTS']['Port_planner'])
port_scene3d = int(config['PORTS']['Port_3d_scene'])
buffer_size = int(config['PARAMS']['Buffersize'])
listen_var = int(config['PARAMS']['Listen'])
# end config

# TODO: fix connection to client adapter because send
# localhost != socket.gethostbyname(socket.gethostname())

# print(socket.gethostbyname(socket.gethostname()))

test_ip = '192.168.1.42'

address_client = (test_ip, port_cl_ad)
address_scene3d = (host, port_scene3d)
address_planner = (host, port_planner)

socket_scene3d = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_scene3d.connect(address_scene3d)
socket_scene3d.send(b'ClAd')

socket_planner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_planner.connect(address_planner)

socket_client_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client_listener.bind(address_client)
socket_client_listener.listen(listen_var)

message_error = b'Error, somebody don\'t be responsible, please read logs!'

# Deal with Unity clients.
while True:
    client_socket_conn, client_socket_address = socket_client_listener.accept()

    client_adapter = ClientAdapter(address_client, client_socket_conn,
                                   client_socket_address, address_scene3d,
                                   socket_scene3d, address_planner,
                                   socket_planner, buffer_size, message_error)
    client_adapter.run()
