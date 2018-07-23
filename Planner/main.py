""" @author Urazov Dilshod
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
import math
# logging

def consistently(list):
    while next(iter(list[i])) == 'who':
       str_send = list[i]['who'][0] + ':' + list[i]['cmd'] + list[i]['params']


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
    print(1)
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

dict_Name = {'fanuc' : 'f', 'telega' : 't'}

def get_scene():
    sock_3d_scene.send(b'get_scene')


def data_convert_json_to_str_byte(name, cmd):
    data_str_byte = (dict_Name[name] + ':'+cmd + '|').encode()
    print(data_str_byte)
    return data_str_byte


while True:
    i = 0
    try:

        message = conn.recv(2048).decode()

    except ConnectionAbortedError:
        logging.error('ClientAdapter aborted connection')



    #time.sleep(0.001)
    if message != '':
            logging.info(message)
    if message == 'e':
        for robot in robo_dict:
            message = robot + ':' + 'e|'
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
        print(data)
        while i != (len(data['Scenario']) - 1):
            if data['Scenario'][i].get('parallel') == 'True':
                sock_rob_ad.send(data_convert_json_to_str_byte(data['Scenario'][i].get('name'),
                                                               data['Scenario'][i].get('command')))
                sock_rob_ad.send(data_convert_json_to_str_byte(data['Scenario'][i+1].get('name'),
                                                               data['Scenario'][i+1].get('command')))
                if int(data['Scenario'][i].get('time')) > int(data['Scenario'][i+1].get('time')):
                    time.sleep(int(data['Scenario'][i].get('time')))
                else:
                    time.sleep(int(data['Scenario'][i+1].get('time')))
                i += 1
            else:
                sock_rob_ad.send(data_convert_json_to_str_byte(data['Scenario'][i].get('name'),
                                                               data['Scenario'][i].get('command')))
                time.sleep(int(data['Scenario'][i].get('time')))
            i += 1
            sock_rob_ad.send(data_convert_json_to_str_byte(data['Scenario'][i].get('name'),
                                                           data['Scenario'][i].get('command')))

    except ConnectionAbortedError:
        logging.error('RCA aborted connection')
    except Exception as n:
        print(n)
    #TODO добавить сюда отказоустойчивость при отловке какого либо осключения. чтобы он постоянно не спамил названием
    #TODO этой ошибки. поставить еще один цикл внешний
    #TODO Логирование