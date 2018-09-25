import socket
import json
import time


buffer_size = 1024


def _create_task(flag='0', task_name='moving', parallel=False,
                 robot_names=('f',), tasks_time=(3,), energy=(3,),
                 commands=('m 0 0 0 0 0 0',)):
    data_to_send = {
        'flag': str(flag),
        'name': str(task_name),
        'Scenario': [
            {
                'parallel': str(parallel),
                'name': str(robot_name),
                'time': str(task_time),
                'energy': str(enrg),
                'command': str(command)
            } for robot_name, task_time, enrg, command in zip(robot_names,
                                                              tasks_time,
                                                              energy, commands)
        ]
    }
    return data_to_send


def create_simple_unparallel_task(flag='0', task_name='moving',
                                  robot_names=('f',), tasks_time=(3,),
                                  energy=(3,), commands=('m 0 0 0 0 0 0',)):
    data_to_send = _create_task(flag=flag,
                                task_name=task_name,
                                parallel=False,
                                robot_names=robot_names,
                                tasks_time=tasks_time,
                                energy=energy,
                                commands=commands)
    return data_to_send


def create_simple_parallel_task(flag='0', task_name='moving_together',
                                robot_names=('f',), tasks_time=(3,),
                                energy=(3,), commands=('m 10 0 0 0 0 0',)):
    data_to_send = _create_task(flag=flag,
                                task_name=task_name,
                                parallel=True,
                                robot_names=robot_names[:-1],
                                tasks_time=tasks_time[:-1],
                                energy=energy[:-1],
                                commands=commands[:-1])
    data_to_send['Scenario'].append({
        'parallel': 'False',
        'name': str(robot_names[-1]),
        'time': str(tasks_time[-1]),
        'energy': str(energy[-1]),
        'command': str(commands[-1])
    })
    return data_to_send


def create_complex_unparallel_task(flag='0', task_name='moving_difficult',
                                   commands=('moving',)):
    empty_list = [''] * len(commands)
    data_to_send = _create_task(flag=flag,
                                task_name=task_name,
                                parallel=False,
                                robot_names=empty_list,
                                tasks_time=empty_list,
                                energy=empty_list,
                                commands=commands)
    return data_to_send


def create_complex_parallel_task(flag='0', task_name='moving_difficult2',
                                 commands=('moving',)):
    empty_list = [''] * len(commands)
    data_to_send = _create_task(flag=flag,
                                task_name=task_name,
                                parallel=True,
                                robot_names=empty_list,
                                tasks_time=empty_list,
                                energy=empty_list,
                                commands=commands[:-1])
    data_to_send['Scenario'].append({
        'parallel': 'False',
        'name': '',
        'time': '',
        'energy': '',
        'command': str(commands[-1])
    })
    return data_to_send


def create_command_from_input():
    flag = input('flag: ')
    task_name = input('task_name: ')
    task_number = int(input('tasks_number: '))

    parallel = []
    robot_names = []
    tasks_time = []
    energy = []
    commands = []
    for _ in range(task_number):
        parallel.append(input('parallel: '))
        robot_names.append(input('name: '))
        tasks_time.append(input('time: '))
        energy.append(input('energy: '))
        commands.append(input('command: '))

    data_to_send = _create_task(flag=flag,
                                task_name=task_name,
                                parallel=True,
                                robot_names=robot_names,
                                tasks_time=tasks_time,
                                energy=energy,
                                commands=commands)
    return data_to_send


def send_data(data_to_send, sock):
    data_json = json.dumps(data_to_send)
    sock.send(data_json.encode())
    print('Send data:', data_json)


def send_unparallel_simple_tasks_to_cunit(sock):
    data_to_send = create_simple_unparallel_task(
        flag='0',
        task_name='moving',
        robot_names=['fanuc', 'telega', 'fanuc', 'telega'],
        tasks_time=[3, 1, 3, 3],
        energy=[3, 3, 3, 3],
        commands=['m 10 0 0 0 0 0', 'm 10 10 0 0 0 0',
                  'm 20 10 0 0 0 0', 'm 0 0 0 0 0 0']
    )
    send_data(data_to_send, sock)


def send_parallel_simple_tasks_to_cunit(sock):
    data_to_send = create_simple_parallel_task(
        flag='0',
        task_name='moving_together',
        robot_names=['fanuc', 'telega', 'fanuc', 'telega'],
        tasks_time=[3, 1, 3, 3],
        energy=[3, 3, 3, 3],
        commands=['m 40 10 0 0 0 0', 'm 60 15 0 0 0 0',
                  'm 80 20 0 0 0 0', 'm 80 0 20 0 0 0']
    )
    send_data(data_to_send, sock)


def send_unparallel_complex_tasks_to_cunit(sock):
    data_to_send = create_complex_unparallel_task(
        flag='0',
        task_name='moving_difficult',
        commands=['moving', 'moving']
    )
    send_data(data_to_send, sock)


def send_parallel_complex_tasks_to_cunit(sock):
    data_to_send = create_complex_parallel_task(
        flag='0',
        task_name='moving_difficult_together',
        commands=['moving_together', 'moving_together']
    )
    send_data(data_to_send, sock)


def send_get_scene_request(sock):
    flag = 1
    data_to_send = {
        'flag': str(flag),
        'name': 'get_scene',
        'Scenario': []
    }
    data_json = json.dumps(data_to_send)
    sock.send(data_json.encode())
    data = sock.recv(buffer_size).decode()
    print('Response from 3d scene:', data)


def send_simele_task_with_parameter(sock):
    data_to_send = create_simple_unparallel_task(
        flag='0',
        task_name='moving with parameter',
        robot_names=['fanuc', 'telega'],
        tasks_time=[2, 2],
        energy=[3, 3],
        commands=['m $cube$', 'm $cube$']
    )
    send_data(data_to_send, sock)


def send_complex_task_with_parameter(sock):
    data_to_send = create_complex_unparallel_task(
        flag='0',
        task_name='moving_difficult_with_parameter',
        commands=['moving', 'moving with parameter']
    )
    send_data(data_to_send, sock)


cl_adapter_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port_cl_adapter = 9090
cl_adapter_sock.connect(('localhost', port_cl_adapter))

print('Options:\n'
      '1: send simple tasks\n'
      '2: send complex tasks\n'
      '3: send "get_scene" request to 3d Scene\n'
      '4: send simple task with parameter\n'
      '5: send complex task with parameter\n\n'
      '0: exit')

delay = 3
inp = input('Enter some key [1-5] to start or 0 to exit: ')
while inp != '0':
    if inp == '1':
        send_unparallel_simple_tasks_to_cunit(cl_adapter_sock)
        send_parallel_simple_tasks_to_cunit(cl_adapter_sock)
    elif inp == '2':
        send_unparallel_complex_tasks_to_cunit(cl_adapter_sock)
        send_parallel_complex_tasks_to_cunit(cl_adapter_sock)
    elif inp == '3':
        send_get_scene_request(cl_adapter_sock)
    elif inp == '4':
        send_simele_task_with_parameter(cl_adapter_sock)
    elif inp == '5':
        send_complex_task_with_parameter(cl_adapter_sock)

    time.sleep(delay)
    inp = input('Enter some key [1-5] to continue or 0 to exit: ')
