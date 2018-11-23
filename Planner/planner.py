import logging
import json
import time


# ATTENTION! Before use this class configure your logging.
class Planner:
    SPECIAL_SYMBOL = '$'
    CONCAT_SYMBOL = '+'
    SEPARATED_SYMBOL = '!'
    EPS = 2000

    def __init__(self, sock_rob_ad, sock_scene3d, robo_dict, buffer_size):
        self.ROBO_DICT = robo_dict
        self.RD = {'f': 'fanuc_world', 't': 'telega'}
        self.BUFFER_SIZE = buffer_size

        self.sock_rob_ad = sock_rob_ad
        self.sock_scene3d = sock_scene3d

    def get_all_data_from_scene3d(self):
        self.sock_scene3d.send(b'get_scene')
        message_from_scene3d = \
            self.sock_scene3d.recv(self.BUFFER_SIZE).decode()
        return json.loads(message_from_scene3d)

    def data_convert_json_to_str_byte(self, command, receiver,
                                      default_robot_with_sensors='f'):
        if command == 'sensors':
            # WARNING: make sure that robot with further ID has sensors!
            command = default_robot_with_sensors
        data_str_byte = f'{receiver}: {command}|'.encode()
        print(data_str_byte)
        return data_str_byte

    def is_exist_in_scene3d(self, object_name):
        data_from_scene3d = self.get_all_data_from_scene3d()
        return object_name in data_from_scene3d

    def try_get_data_from_sensors(self, receiver, object_name, checks_number=3,
                                  time_delay=3):
        print('Try to found', object_name, 'in', receiver)

        for _ in range(checks_number):
            if self.is_exist_in_scene3d(object_name):
                return True

            self.sock_rob_ad.send(
                self.data_convert_json_to_str_byte('sensors', receiver)
            )
            time.sleep(time_delay)

        return False

    def find_parameter(self, command, symbol=SPECIAL_SYMBOL):
        parameter_begin = command.find(symbol)
        if parameter_begin != -1:
            parameter_end = command.find(symbol, parameter_begin + 1)
            if parameter_end == -1:
                raise ValueError(f'Did not find end of parameter in command: '
                                 f'{command}.')
            return command[parameter_begin:parameter_end + 1]
        return None

    def get_data_and_replace_parameter(self, command, receiver, parameter):
        self.sock_scene3d.send(f'get {parameter}'.encode())
        data_from_3d_scene = self.sock_scene3d.recv(self.BUFFER_SIZE).decode()

        if data_from_3d_scene == 'None':
            if not self.try_get_data_from_sensors(receiver, parameter):
                return None

        new_command = command.replace(parameter, data_from_3d_scene)

        return self.add_offset(new_command, data_from_3d_scene)

    def add_offset(self, command, data_from_3d_scene,
                   concat_symbol=CONCAT_SYMBOL,
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
        raise NotImplementedError('Need to add processing for '
                                  'non-standard offset')

    def get_data_from_scene_and_compare(self, sent_command, receiver):
        # Get all data from scene3d.
        data_from_scene3d = self.get_all_data_from_scene3d()

        # Remove all blank chars and last parameter.
        coords_to_check = sent_command.strip()[1:-1].strip()
        print(f"coords to check {coords_to_check}")
        if self.RD[receiver] in data_from_scene3d:
            # Remove all blank chars.
            coords_for_check = data_from_scene3d[self.RD[receiver]].strip()
            print(f"coords for check {coords_for_check}")
            if coords_to_check == coords_for_check:
                return True

            for c, r in set(zip(coords_to_check.split(' '),
                                coords_for_check.split(' '))):
                if abs(abs(float(c)) - abs(float(r))) > self.EPS:
                    print(float(c))
                    print(float(r))
                    return False
            return True

        return None

    def check_command_execution(self, sent_command, receiver):
        if 'm' not in sent_command:
            return True

        result = self.get_data_from_scene_and_compare(sent_command, receiver)
        if result is not None:
            if not result:
                self.sock_scene3d.send(b'set "status": "error_command"')
                print("Status: error_command")
                logging.info("Status: error_command")
                return False

            self.sock_scene3d.send(b'set "status": "ok"')
            print("Status: ok")
            logging.info("Status: ok")
            return True

        self.sock_scene3d.send(b'set "status": "error_object"')
        print("Status: error_object")
        logging.info("Status: error_object")
        return False

    def check_execution_with_delay(self, sent_command, receiver,
                                   checks_number=3, time_delay=1):
        # Check command execution with some delays.
        if 'm' in sent_command:
            is_executed = False
            for j in range(checks_number):
                if self.check_command_execution(sent_command, receiver):
                    is_executed = True
                    break

                time.sleep(time_delay * j + time_delay)

            if not is_executed:
                print(f"Error: {self.RD[receiver]} in {sent_command}")
                return False

        return True

    def process_simple_task(self, task, task_loader, save_task=True):
        if save_task:
            task_loader.save_task(task)

        result_status = True

        i = 0
        command_number = len(task['Scenario'])
        while i < command_number:
            time_1 = int(task['Scenario'][i].get('time'))

            receiver_1 = task['Scenario'][i].get('name')
            command_1 = task['Scenario'][i].get('command')

            # Find parameter in command, try to replace it to data from
            # scene3d.
            parameter_name_1 = self.find_parameter(command_1)
            if parameter_name_1 is not None:
                command_1 = self.get_data_and_replace_parameter(
                    command_1, receiver_1, parameter_name_1
                )
                if not command_1:
                    result_status = False
                    break

            # Imitation of parallel work. Need to improve this piece of code.
            if task['Scenario'][i].get('parallel') == "true" and \
                    i + 1 < command_number:
                self.sock_rob_ad.send(
                    self.data_convert_json_to_str_byte(command_1, receiver_1)
                )
                print('Send to', receiver_1, 'command:', command_1)

                receiver_2 = task['Scenario'][i + 1].get('name')
                command_2 = task['Scenario'][i + 1].get('command')

                parameter_name_2 = self.find_parameter(command_2)
                if parameter_name_2 is not None:
                    command_2 = self.get_data_and_replace_parameter(
                        command_2, receiver_1, parameter_name_2
                    )

                self.sock_rob_ad.send(
                    self.data_convert_json_to_str_byte(command_2, receiver_2)
                )
                print('Send to', receiver_2, 'command:', command_2)

                time_2 = int(task['Scenario'][i + 1].get('time'))
                time.sleep(max(time_1, time_2))

                check_1 = self.check_command_execution(command_1, receiver_1)
                check_2 = self.check_command_execution(command_2, receiver_2)

                if not check_1:
                    print(f"Error: {self.RD[receiver_1]} in {command_1}")
                    result_status = False
                    break
                if not check_2:
                    print(f"Error: {self.RD[receiver_2]} in {command_2}")
                    result_status = False
                    break

                i += 1

            else:
                self.sock_rob_ad.send(
                    self.data_convert_json_to_str_byte(command_1, receiver_1)
                )
                print('Send to', receiver_1, 'command:', command_1)
                time.sleep(time_1)

                if not self.check_execution_with_delay(command_1, receiver_1):
                    result_status = False
                    break

            i += 1

        return result_status

    def process_complex_task(self, task, task_loader):
        for scenario_task in task['Scenario']:
            print('Task name:', scenario_task.get('command'))

            # Load tasks from loader and process it as simple task.
            if len(scenario_task.get('command').split(' ')) == 1 and \
                    scenario_task.get('command') != 'f':
                simple_task = task_loader.load_task(
                    scenario_task.get('command')
                )
            else:
                simple_task = scenario_task
            if not self.process_simple_task(
                    simple_task, task_loader,
                    save_task=bool(scenario_task.get('name'))):
                break
