import os
from datetime import datetime
import logging
logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename='scene3d.log')

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
            if data:
                logging.info('def_rca recv ' + str(datetime.now()).replace(':', ';') + ' : ' + data)

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