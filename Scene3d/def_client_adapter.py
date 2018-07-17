import os
import logging

def client_adapter_func(client, json_data):
    while True:
        message = client.recv(1024).decode()
        logging.info('def_client_adapter' + message)
        if message == '1':
            data = json_data.get()
            client.send(data.decode())
            logging.info('client send')
        if message=='e':
            json_data.exit = True
            logging.info('exit')
            os._exit(0)
        # TODO: try except construction then client end connection
    client.close()
