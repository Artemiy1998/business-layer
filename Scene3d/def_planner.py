import os
import logging

def planner_func(client, json_data):
    while True:
        data = json_data.get()
        try:
            message = client.recv(1024).encode()
            logging.info('def_planer recv' + message)
            if message == "get_scene":
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