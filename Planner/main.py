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
buffer_size = int(config['PARAMS']['Buffersize'])

who = 'p'
robo_dict = ['f', 't']
rd = {'f': 'fanuc_world', 't': 'telega'}
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
    logging.error('Scene3d refused connection')

sock_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_serv.bind((host, port_planner))
sock_serv.listen(1)

SPECIAL_SYMBOL = '$'
CONCAT_SYMBOL = '+'
SEPARATED_SYMBOL = '!'
EPS = 10


def data_convert_json_to_str_byte(name, cmd):
    if cmd == 'sensors':
        cmd = 'f'
    data_str_byte = f'{name}: {cmd}|'.encode()
    print(data_str_byte)
    return data_str_byte


def find_parameter(command, symbol=SPECIAL_SYMBOL):
    parameter_begin = command.find(symbol)
    if parameter_begin != -1:
        parameter_end = command.find(symbol, parameter_begin + 1)
        if parameter_end == -1:
            raise ValueError(f'Did not find end of parameter in command: '
                             f'{command}.')
        return command[parameter_begin:parameter_end + 1]
    return None


def get_data_and_replace_parameter(command, parameter, sock_scene3d):
    sock_scene3d.send(f'get {parameter}'.encode())
    data_from_3d_scene = sock_scene3d.recv(buffer_size).decode()
    new_command = command.replace(parameter, data_from_3d_scene)
    return add_offset(new_command, data_from_3d_scene)


def add_offset(command, data_from_3d_scene, concat_symbol=CONCAT_SYMBOL,
               separated_symbol=SEPARATED_SYMBOL, command_offset=None):
    # Find symbol for command with offset.
    con_pos = command.find(concat_symbol)
    if con_pos == -1:
        return command

    # Find command coordinate.
    sep_pos = command.find(separated_symbol)
    if sep_pos == -1:
        raise ValueError(f'Did not found control symbol at the end of the'
                         f'command: {command}')

    # Skip space symbols: con_pos + 2 and sep_pos - 1.
    data_to_add = command[con_pos + 2:sep_pos - 1]
    coords = [str(float(x) + float(y)) for x, y in zip(
        data_from_3d_scene.split(' '), data_to_add.split(' ')
    )]
    if command_offset is None:
        # Get command literal (because it place in the beginning)
        # with space symbol. Add command coordinate at the end.
        return command[:2] + ' '.join(coords) + command[sep_pos + 1:]
    raise NotImplementedError('Need to add processing for non-standard offset')


def get_data_from_scene_and_compare(sent_command, receiver, sock_scene3d):
    # Get all data from scene3d.
    sock_scene3d.send(b'get_scene')
    message_from_scene3d = sock_scene3d.recv(buffer_size).decode()
    data_from_scene3d = json.loads(message_from_scene3d)

    # Remove all blank chars and last parameter.
    coords_to_check = sent_command.strip()[1:-1].strip()
    print(f"coords to check {coords_to_check}")
    if rd[receiver] in data_from_scene3d:
        # Remove all blank chars.
        coords_for_check = data_from_scene3d[rd[receiver]].strip()
        print(f"coords for check {coords_for_check}")
        if coords_to_check == coords_for_check:
            return True
        
        for c, r in set(zip(coords_to_check.split(' '),
                            coords_for_check.split(' '))):
            if abs(abs(float(c)) - abs(float(r))) > EPS:
                print(float(c))
                print(float(r))
                return False
        return True

    return None


def check_command_execution(sent_command, receiver, sock_scene3d):
    if 'm' not in sent_command:
        return True

    result = get_data_from_scene_and_compare(sent_command, receiver,
                                             sock_scene3d)
    if result is not None:
        if not result:
            sock_scene3d.send(b'set "status": "error_command"')
            return False
        else:
            sock_scene3d.send(b'set "status": "ok"')
            return True
    else:
        sock_scene3d.send(b'set "status": "error_object"')
        return False


def process_simple_task(task, task_loader, save_task=True):
    if save_task:
        task_loader.save_task(task)

    i = 0
    command_number = len(task['Scenario'])
    while i < command_number:
        time_1 = int(task['Scenario'][i].get('time'))

        name_1 = task['Scenario'][i].get('name')
        command_1 = task['Scenario'][i].get('command')

        # Find parameter in command, try to replace it to data from 3d scene.
        parameter_name_1 = find_parameter(command_1)
        if parameter_name_1 is not None:
            command_1 = get_data_and_replace_parameter(
                command_1, parameter_name_1, sock_3d_scene
            )

        # Imitation of parallel work. Need to improve this piece of code.
        if bool(task['Scenario'][i].get('parallel') == "True") and \
           i + 1 < command_number:
            sock_rob_ad.send(data_convert_json_to_str_byte(name_1, command_1))
            print('Send to', name_1, 'command:', command_1)

            name_2 = task['Scenario'][i + 1].get('name')
            command_2 = task['Scenario'][i + 1].get('command')

            parameter_name_2 = find_parameter(command_2)
            if parameter_name_2 is not None:
                command_2 = get_data_and_replace_parameter(
                    command_2, parameter_name_2, sock_3d_scene
                )

            sock_rob_ad.send(data_convert_json_to_str_byte(name_2, command_2))
            print('Send to', name_2, 'command:', command_2)

            time_2 = int(task['Scenario'][i + 1].get('time'))
            time.sleep(max(time_1, time_2))

            check_1 = check_command_execution(command_1, name_1, sock_3d_scene)
            check_2 = check_command_execution(command_2, name_2, sock_3d_scene)

            if not (check_1 and check_2):
                break

            i += 1

        else:
            sock_rob_ad.send(data_convert_json_to_str_byte(name_1, command_1))
            print('Send to', name_1, 'command:', command_1)
            time.sleep(time_1)
            if 'm' in command_1:
                for j in range(3):
                    if check_command_execution(command_1, name_1, sock_3d_scene):
                        break

                    time.sleep(3 * j + 3)
                if not check_command_execution(command_1, name_1, sock_3d_scene):
                    print(f"Error {rd[name_1]} in {command_1}")
                    break
        i += 1


def process_complex_task(task, task_loader):
    for task in task['Scenario']:
        print('Task name:', task.get('command'))

        # Load tasks from loader and process it as simple task.
        simple_task = task_loader.load_task(task.get('command'))
        process_simple_task(simple_task, task_loader, save_task=False)


# Read all data from socket buffer.
def receive(sock):
    total_data = b''
    try:
        while True:
            recv_data = sock.recv(buffer_size)
            if recv_data:
                total_data += recv_data
            else:
                break
    except Exception:
        pass
    return total_data.decode()


taskloader = TaskLoader()
count = 0
while True:
    conn, addr = sock_serv.accept()
    conn.setblocking(False)
    while True:
        try:
            messages = receive(conn)
            if messages:
                logging.info(messages)
                print('Command iteration:', count)
            else:
                continue

            messages = messages.split('|')
            for message in messages[:-1]:  # Skip last empty list.
                if message == 'e':
                    for robot in robo_dict:
                        message = f'{robot}: e|'
                        try:
                            print('Send exit message to robots:', message)
                            sock_rob_ad.send(message.encode())
                            time.sleep(1)
                        except ConnectionAbortedError:
                            logging.error('RCA aborted connection')
                    try:
                        print('Send exit message to RCA:', message)
                        sock_rob_ad.send(b'e|')
                    except ConnectionAbortedError:
                        logging.error('RCA aborted connection')
                    logging.info('Planner stopped')
                    sys.exit(0)
                try:
                    print(message)
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
