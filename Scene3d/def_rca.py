import logging
import sys

from datetime import datetime


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='scene3d.log')


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
                msg = (f'def_rca recv {str(datetime.now()).replace(":", ";")} '
                       f': {data}')
                logging.info(msg)
                print(msg)

                json_data.add(data)
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
