import logging
import os


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='scene3d.log')

buffer_size = 1024


def _clear_parameter_name(parameter):
    return parameter[1:-1]


def planner_func(client, json_data):
    """
    @brief This Function send planer current state system
    :param client: socket client
    :param json_data: data in json format
    """
    while True:
        try:
            message = client.recv(buffer_size).decode()
            if message:
                logging.info(f'def_planer recv {message}')
                print(f'def_planner recv', message)

                if message == 'get_scene':
                    data = json_data.get()
                    client.send(data.encode())

                    logging.info(f'planner send {data}')
                    print(f'planner send', data)
                elif message.startswith('get '):
                    # Skip 'get ' in received message, clear from special
                    # symbols.
                    parameter_name = _clear_parameter_name(message[4:])
                    print(f"parametr: {parameter_name}")
                    response = json_data.get_by_parameter(parameter_name)
                    print(f"response: {response}")
                    client.send(response.encode())
                    logging.info(f'planner send {response}')
                    print(f'planner send', response)
                elif message.startswith('set '):
                    json_data.add(f'"status": "{message[4:]}"')
                if json_data.exit:
                    logging.info('exit')
                    os._exit(0)
        except ConnectionRefusedError:
            # logging.error('Planner disconnected. ConnectionRefusedError')
            pass
        except ConnectionAbortedError:
            # logging.error('Planner disconnected. ConnectionAbortedError')
            pass
        except ConnectionResetError:
            # logging.error('Planner disconnected. ConnectionResetError')
            pass
    # client.close()
