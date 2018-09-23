"""
@author Artemii Morozov and Urazov Dilshod
Documentation for Planner module

@brief Now planner do nothing but transfer
"""


import os
import socket
import sys
import configparser
import logging
import json
import time


# TODO: при отключении клиент адаптера на CUnit, которому была адресована
# последняя команда, начинается спам этой командой, так как в беск. цикле
# вызывается исключение, и так снова и снова.


# logging
logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='Planner.log'
)

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

dict_Name = {'fanuc': 'f', 'telega': 't'}


def get_scene():
    sock_3d_scene.send(b'get_scene')


def data_convert_json_to_str_byte(name, cmd):
    data_str_byte = f'{dict_Name[name]}: {cmd}|'.encode()
    print(data_str_byte)
    return data_str_byte


count = 0
while True:
    conn, addr = sock_serv.accept()
    while True:
        print(count)
        i = 0
        try:
            message = conn.recv(2048).decode()
            if message:
                    logging.info(message)
            if message == 'e':
                for robot in robo_dict:
                    message = f'{robot}: e|'
                    try:
                        sock_rob_ad.send(message.encode())
                        time.sleep(1)
                    except ConnectionAbortedError:
                        logging.error('RCA aborted connection')
                try:
                    sock_rob_ad.send(b'e|')
                except ConnectionAbortedError:
                    logging.error('RCA aborted connection')
                logging.info('Planner stopped')
                sys.exit(0)
            try:
                data = json.loads(message)
                while i != (len(data['Scenario'])):
                    if data['Scenario'][i].get('parallel') == 'True':
                        sock_rob_ad.send(data_convert_json_to_str_byte(
                            data['Scenario'][i].get('name'),
                            data['Scenario'][i].get('command')
                        ))
                        sock_rob_ad.send(data_convert_json_to_str_byte(
                            data['Scenario'][i + 1].get('name'),
                            data['Scenario'][i + 1].get('command')
                        ))
                        if int(data['Scenario'][i].get('time')) > \
                           int(data['Scenario'][i + 1].get('time')):
                            time.sleep(int(data['Scenario'][i].get('time')))
                        else:
                            time.sleep(
                                int(data['Scenario'][i + 1].get('time'))
                            )
                        i += 1
                    else:
                        sock_rob_ad.send(data_convert_json_to_str_byte(
                            data['Scenario'][i].get('name'),
                            data['Scenario'][i].get('command')
                        ))
                        time.sleep(int(data['Scenario'][i].get('time')))
                    i += 1

            except ConnectionAbortedError:
                # logging.error('RCA aborted connection')
                pass
            except Exception as e:
                print(e)
                continue
        except ConnectionAbortedError:
            # logging.error('ClientAdapter aborted connection')
            pass
        except ConnectionResetError:
            # logging.error('ClientAdapter reset connection')
            pass

    # TODO: добавить сюда отказоустойчивость при отловке какого либо
    # осключения. чтобы он постоянно не спамил названием этой ошибки.

    # TODO: Поставить еще один цикл внешний.

    # TODO: Логирование.
