import logging
import sys


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='scene3d.log')


def client_adapter_func(client, json_data):
    """
    @brief This Function send planer current state system
    :param client: socket client
    :param json_data: data in json format
    """
    while True:
        data = json_data.get()
        try:
            message = client.recv(1024).decode()
            if message == 'get_scene':
                logging.info(f'def_client_adapter {message}')
                print(f'def_client_adapter {message}')

                client.send(data.encode())
                logging.info(f'client send {data}')
                print(f'client send {data}')
            if message == 'e':
                json_data.exit = True
                logging.info('exit')
                sys.exit(0)
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
