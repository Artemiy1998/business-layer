import logging
import sys

from datetime import datetime


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='scene3d.log')

buffer_size = 1024


def rca_func(client, json_data):
    """
    @brief Function accept current data system
    :param client: socket client
    :param json_data: data in json format
    """
    while True:
        try:
            message = client.recv(buffer_size).decode()
            if message:
                data = (f'def_rca recv {str(datetime.now()).replace(":", ";")}'
                        f': {message}')
                logging.info(data)
                print(data)

                json_data.add(message)
                if json_data.exit:
                    sys.exit(0)
        except ConnectionRefusedError:
            # logging.error('RCA disconnected. ConnectionRefusedError')
            pass
        except ConnectionAbortedError:
            # logging.error('RCA disconnected. ConnectionAbortedError')
            pass
        except ConnectionResetError:
            # logging.error('RCA disconnected. ConnectionResetError')
            pass
    # client.close()
