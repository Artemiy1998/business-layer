import socket
import json
import time


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
                'energy': str(ener),
                'command': str(command)
            } for robot_name, task_time, ener, command in zip(robot_names,
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


def send_data_to_cunit():
    data_to_send = create_simple_parallel_task(
        flag='0',
        task_name='moving',
        robot_names=['fanuc', 'telega', 'fanuc', 'telega'],
        tasks_time=[3, 1, 3, 3],
        energy=[3, 3, 3, 3],
        commands=['cmd1', 'cmd2', 'cmd3', 'cmd4']
    )
    data_json = json.dumps(data_to_send)
    sock.send(data_json.encode())


def send_data_to_3d_scene():
    flag = 1
    parallel = True
    name = 'fanuc'
    cmd = 'cmd1'
    data_to_send = {
        'flag': str(flag),
        'Scenario': [
            {
                'parallel': str(parallel),
                'name': str(name),
                'command': str(cmd)
            }
        ]
    }
    data_json = json.dumps(data_to_send)
    sock.send(data_json.encode())
    data = sock.recv(2048).decode()
    print('3d:', data)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port_cl_adapter = 9090
sock.connect(('localhost', port_cl_adapter))

inp = ''
while inp != '0':
    send_data_to_cunit()
    time.sleep(5)

    send_data_to_3d_scene()

    time.sleep(0.04)
    inp = input('Enter some key for continue and 0 for exit: ')
