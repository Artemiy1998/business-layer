import os
import logging

def rca_func(client, json_data):
    """
    @brief Function accept current data system
    :param client: socket client
    :param json_data: data in json format
    :return:
    """
    while True:
        try:
            data = client.recv(1024).decode()
            logging.info('def_rca recv ' + data)

            json_data.set(data)
            if json_data.exit:
                os._exit(0)
        except ConnectionRefusedError:
            logging.error('RCA disconnected. ConnectionRefusedError')
        except ConnectionAbortedError:
            logging.error('RCA disconnected. ConnectionAbortedError')
        except ConnectionResetError:
            logging.error('RCA disconnected. ConnectionResetError')
    client.close()