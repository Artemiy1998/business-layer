"""
@author Morozov Artemii
Documentation for Client Adapter module.

@brief Client Adapter module performs the
communication of Business Layer with client.
"""


import socket
import json
import time
import configparser
import os
import logging
import sys


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
port_3d_scene = int(config['PORTS']['Port_3d_scene'])
listen_var = int(config['PARAMS']['Listen'])
# end config

# TODO: fix connection to client adapter because
# localhost != socket.gethostbyname(socket.gethostname())

# print(socket.gethostbyname(socket.gethostname()))
address_client = ('localhost', port_cl_ad)
address_3dScene = (host, port_3d_scene)
address_Planner = (host, port_planner)
dict_Name = {'fanuc': 'f', 'telega': 't'}

socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.bind(address_client)
socket_client.listen(listen_var)

socket_3dScene = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_3dScene.connect(address_3dScene)
socket_3dScene.send(b'ClAd')

socket_Planner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_Planner.connect(address_Planner)
logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='clad.log')
message_error = b'Error, somebody don\'t be responsible, please read logs'


def except_func(def_send, socket_component, socket_address,
                socket_another_component):
    for _ in range(3):
        time.sleep(60)
        try:
            socket_component.connect(socket_address)
            logging.info(socket_address[0] + '  Reconnect')
            def_send()
        except ConnectionRefusedError:
            pass
    client_Socket_Conn.send(message_error)
    logging.info(f'send Client {message_error.decode()}')
    socket_another_component.send(b'e')

    socket_component.close()
    socket_another_component.close()
    client_Socket_Conn.close()
    socket_client.close()
    logging.info('3d Scene, Client Adapter, Client close')
    sys.exit()


def send_planner():
    """
    @brief Function sends a request to the planer from the client
    all parameters used in this function - global variable
    Function return nothing.
    """
    try:
        data_to_send = json.dumps(data_Json)
        data_to_send = add_separator(data_to_send)
        socket_Planner.send(data_to_send.encode())
        print(data_to_send)
        logging.info(f'send Planner {data_to_send}')
    except ConnectionRefusedError:
        logging.error('ConnectionRefusedError')
        client_Socket_Conn.send(b'Error, Connection Refused wait 3 minutes')
        except_func(send_planner, socket_Planner,
                    address_Planner, socket_3dScene)


def send_3d_scene():
    """
    @brief Function sends a request to the scene from the client
    all parameters used in this function - global variable
    Function return response from the scene.
    """
    try:
        socket_3dScene.send(str(data_Json.get('flag')).encode())
        data_into_3d_scene = socket_3dScene.recv(2048)
        print('3d')
        print(data_into_3d_scene)
        return data_into_3d_scene
    except ConnectionRefusedError:
        logging.error('ConnectionRefusedError')
        client_Socket_Conn.send(b'Error, Connection Refused wait 3 minutes')
        logging.info('send Client:Refused, wait 3 minutes')
        except_func(send_3d_scene, socket_3dScene,
                    address_3dScene, socket_Planner)
    except ConnectionResetError:
        logging.error('ConnectionResetError')
        client_Socket_Conn.send(b'Error, Connection Refused wait 3 minutes')
        logging.info('send Client: Reset, wait 3 min')
        except_func(send_3d_scene, socket_3dScene,
                    address_3dScene, socket_Planner)


def add_separator(message):
    message += '|'
    return message


count = 0
while True:
    client_Socket_Conn, client_Socket_Address = socket_client.accept()
    print('Connect', client_Socket_Address)
    while True:
        print('Command iteration:', count)
        try:
            data = client_Socket_Conn.recv(1024).decode()
            data_Json = json.loads(data)
        except ConnectionResetError:
            print('Disconnect by reset', client_Socket_Address)
            break
        except Exception:
            print('Disconnect', client_Socket_Address)
            break
        print(isinstance(data_Json, dict))
        if isinstance(data_Json, dict):
            # logging.info(f'From {client_Socket_Address[0]} '
            #              f'recv {data_Json["command"]}')
            try:
                if data_Json.get('flag') == '0':
                    send_planner()
                elif data_Json.get('flag') == '1':
                    data_Send_Byte = send_3d_scene()
                    client_Socket_Conn.send(data_Send_Byte)
                elif data_Json.get('flag') == 'e':
                    socket_3dScene.send(b'e')
                    logging.info('send 3dScene e')
                    socket_Planner.send(b'e')
                    logging.info('send Planner e')
                    socket_Planner.close()
                    logging.info('Planner disconnect')
                    socket_3dScene.close()
                    logging.info('3dScene disconnect')
                    client_Socket_Conn.close()
                    logging.info('Client disconnect')
                    time.sleep(3)
                    sys.exit()  # Planning crash for test builds.
            except AttributeError:
                logging.error('not JSON')
        else:
            logging.error('not JSON')
        count += 1
    client_Socket_Conn.close()
