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

from task_loader import TaskLoader


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


def process_simple_task(task, task_loader, save_task=True):
    if save_task:
        task_loader.save_task(task)

    i = 0
    while i != len(task['Scenario']):
        time_1 = int(task['Scenario'][i].get('time'))

        if task['Scenario'][i].get('parallel') == 'True':
            sock_rob_ad.send(data_convert_json_to_str_byte(
                task['Scenario'][i].get('name'),
                task['Scenario'][i].get('command')
            ))
            sock_rob_ad.send(data_convert_json_to_str_byte(
                task['Scenario'][i + 1].get('name'),
                task['Scenario'][i + 1].get('command')
            ))

            time_2 = int(task['Scenario'][i + 1].get('time'))
            if time_1 > time_2:
                time.sleep(time_1)
            else:
                time.sleep(time_2)
            i += 1
        else:
            sock_rob_ad.send(data_convert_json_to_str_byte(
                task['Scenario'][i].get('name'),
                task['Scenario'][i].get('command')
            ))
            time.sleep(time_1)
        i += 1


def process_complex_task(task, task_loader):
    i = 0
    while i != len(task['Scenario']):
        print('Task name:', task['Scenario'][i].get('command'))
        simple_task = task_loader.load_task(task['Scenario'][i].get('command'))
        process_simple_task(simple_task, task_loader, save_task=False)
        i += 1


taskloader = TaskLoader()
count = 0
while True:
    conn, addr = sock_serv.accept()
    while True:
        print('Command iteration:', count)
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
                is_simple = bool(data['Scenario'][0].get('name'))
                if is_simple:
                    process_simple_task(data, taskloader)
                else:
                    process_complex_task(data, taskloader)

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

    # TODO: Поставить еще один цикл внешний.

    # TODO: Логирование.
