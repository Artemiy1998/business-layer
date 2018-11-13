import logging
import os


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='scene3d.log')

buffer_size = 1024


def client_adapter_func(client, json_data):
    """
    @brief This Function send planer current state system
    :param client: socket client
    :param json_data: data in json format
    """
    while True:
        try:
            message = client.recv(buffer_size).decode()
            if message:
                logging.info(f'def_client_adapter {message}')
                print(f'def_client_adapter {message}')

                if message == 'get_scene':
                    data = json_data.get()
                    client.send(data.encode())

                    logging.info(f'client send {data}')
                    print(f'client send {data}')
                if message == 'e':
                    json_data.exit = True
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
