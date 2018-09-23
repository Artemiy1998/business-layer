import logging


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='scene3d.log')


def client_adapter_func(client, json_data):
    """
    @brief This Function send planer current state system
    :param client: socket client
    :param json_data: data in json format
    :return:
    """
    while True:
        try:
            message = client.recv(1024).decode()
            if message == '1':
                logging.info(f'def_client_adapter {message}')
                data = json_data.get()
                client.send(data.encode())
                logging.info('client send')
            if message == 'e':
                json_data.exit = True
                logging.info('exit')
                exit(0)
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
