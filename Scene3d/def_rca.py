import os
import logging

def rca_func(client, json_data):
    while True:
        data = client.recv(1024).decode()
        logging.info('def_rca recv' + data)
        json_data.set(data)
        if json_data.exit:
            os._exit(0)
        #TODO: try except construction then client end connection
    client.close()