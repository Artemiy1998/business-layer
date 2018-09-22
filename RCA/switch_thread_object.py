import socket
import logging
import os
import time

from threading import Thread
from common_thread_object import CommonSocket


logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='RCA.log'
)


class Switch(object):
    def __init__(self, scene3d_address):
        self.scene_3d_sock = socket.socket()
        self.scene_3d_sock.connect(scene3d_address)
        self.scene_3d_sock.send(b'RCA')
        self.socket_dict = {}
        self.thread = Thread(name='switch', target=self.process)
        self.exit = False

    def run(self):
        self.thread.start()

    def append(self, client_sock):
        if not isinstance(client_sock, CommonSocket):
            raise TypeError('not CommonSocket type')
        self.socket_dict.update({client_sock.who: client_sock})

    def process(self):
        while True:
            socket_dict = dict(self.socket_dict)
            for sock_name in socket_dict:
                if sock_name == 'p' and socket_dict[sock_name].ready_to_read:
                    planer_messages = socket_dict[sock_name].message_from
                    if planer_messages:
                        planer_messages = planer_messages.split('|')
                        for planer_message in planer_messages:
                            logging.debug(f'planner message: {planer_message}')
                            if planer_message == 'e':
                                time.sleep(5)
                                logging.info('exit')
                                os._exit(0)
                            if not planer_message:
                                continue
                            [sock_id, planer_cmd] = planer_message.split(':')
                            if sock_id not in socket_dict:
                                continue

                            # ATTENTION: only for local testing env.
                            socket_dict[sock_id].message_to = f'{planer_cmd} '

                            socket_dict[sock_id].ready_to_write = True
                    socket_dict[sock_name].ready_to_read = False
                elif socket_dict[sock_name].ready_to_read and sock_name != 'p':
                    messages = socket_dict[sock_name].message_from
                    if messages:
                        messages = messages.split('|')
                        for message in messages:
                            logging.debug(f'{sock_name} message: {message}')
                            self.scene_3d_sock.send(message.encode())
                    socket_dict[sock_name].ready_to_read = False
            del socket_dict
