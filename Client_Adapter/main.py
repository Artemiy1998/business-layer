""" @author Morozov Artemii
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

# cnfg
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
listen_var = int(config['PARAMS']['Listen'])

address_client = (host, port_cl_ad)
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
                    level=logging.DEBUG)
message_error = b'Error, somebody don\'t be responsible, please read logs'


def except_func(def_send, socket_component,
                socket_address, socket_another_component):
    for i in range(3):
        time.sleep(60)
        try:
            socket_component.connect(socket_address)
            logging.info(socket_address + '  Reconnect')
            def_send()
        except ConnectionRefusedError:
            pass
    client_Socket_Conn.send(message_error)
    logging.info('send Client ' + message_error)
    socket_another_component.send(b'e')

    socket_component.close()
    socket_another_component.close()
    client_Socket_Conn.close()
    socket_client.close()
    logging.info('3d Scene, Client Adapter, Client close')
    exit()


def data_convert_json_to_str_byte():
    data_str_byte = (str(dict_Name.get(data_Json.get('name')))
                     + ':' + data_Json.get('command')).encode()
    return data_str_byte


def send_planner():
    """@brief Function sends a request to the planer from the client
        all parameters used in this function - global variable
         Function return nothing
    """
    try:
        data_byte_send = data_convert_json_to_str_byte()
        socket_Planner.send(data_byte_send)
        logging.info('send Planner ' + data_byte_send)
    except ConnectionRefusedError:
        logging.error('ConnectionRefusedError')
        client_Socket_Conn.send(b'Error, Connection Refused wait 3 minutes')
        except_func(send_planner(), socket_Planner,
                    address_Planner, socket_3dScene)


def send_3d_scene():
    """@brief Function sends a request to the scene from the client
              all parameters used in this function - global variable
              Function return response frm the scene
        """
    try:
        socket_3dScene.send(str(data_Json.get('flag')).encode())
        data_into_3d_scene = socket_3dScene.recv(2048)
        return data_into_3d_scene
    except ConnectionRefusedError:
        logging.error('ConnectionRefusedError')
        client_Socket_Conn.send(b'Error, Connection Refused wait 3 minutes')
        logging.info('send Client:Refused, wait 3 minutes' )
        except_func(send_3d_scene(), socket_3dScene,
                    address_3dScene, socket_Planner)
    except ConnectionResetError:
        logging.error('ConnectionResetError')
        client_Socket_Conn.send(b'Error, Connection Refused wait 3 minutes')
        logging.info('send Client: Reset, wait 3 min')
        except_func(send_3d_scene(), socket_3dScene,
                    address_3dScene, socket_Planner)


while True:
    client_Socket_Conn, client_Socket_Address = socket_client.accept()
    while True:
        logging.info('Connect ' + client_Socket_Address)

        data_Json = json.loads(client_Socket_Conn.recv(1024).decode())
        logging.info('From ' + client_Socket_Address + '  recv  ' + data_Json)
        if data_Json.get('name') in dict_Name:
            if data_Json.get('flag') == 0:
                send_planner()
            elif data_Json.get('flag') == 1:
                data_Send_Byte = send_3d_scene()
                socket_client.send(data_Send_Byte)
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
                exit()  # planning crash for test builds
        else:
            break
    client_Socket_Conn.close()
