import os
import logging


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='scene3d.log')


def planner_func(client, json_data):
    """
    @brief This Function send planer current state system
    :param client: socket client
    :param json_data: data in json format
    :return:
    """
    while True:
        data = json_data.get()
        try:
            message = client.recv(1024).decode()

            if message == "get_scene":
                logging.info(f'def_planer recv {message}')
                client.send(data.encode())
                logging.info('planner send')
            if json_data.exit:
                logging.info('exit')
                os._exit(0)
        except ConnectionRefusedError:
            logging.error('Planner disconnected. ConnectionRefusedError')
        except ConnectionAbortedError:
            logging.error('Planner disconnected. ConnectionAbortedError')
        except ConnectionResetError:
            logging.error('Planner disconnected. ConnectionResetError')
    client.close()
