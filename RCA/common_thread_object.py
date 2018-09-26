import socket
import logging
import time

from threading import Thread


logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='RCA.log'
)

buffer_size = 1024


class CommonSocket:
    def __init__(self, sock, ready_to_read, ready_to_write):
        if not isinstance(sock, socket.socket):
            raise TypeError(f'Expected socket type, got {type(sock)}.')
        if not isinstance(ready_to_read, bool):
            raise TypeError(f'Expected bool type, got {type(ready_to_read)}.')
        if not isinstance(ready_to_write, bool):
            raise TypeError(f'Expected bool type, got {type(ready_to_write)}.')
        self.sock = sock
        self.sock.setblocking(False)
        self.who = sock.recv(buffer_size).decode()
        logging.info(self.who)
        self.ready_to_read = ready_to_read
        self.ready_to_write = ready_to_write
        self.thread_to_read = Thread(name=f'{self.who}_read',
                                     target=self.read_func)
        self.thread_to_write = Thread(name=f'{self.who}_write',
                                      target=self.write_func)
        self.message_from = ''
        self.message_to = ''
        self.exit = False
        self._DELAY = 0.01

    def recv(self):
        total_data = b''
        try:
            while True:
                data = self.sock.recv(buffer_size)
                if data:
                    total_data += data
                else:
                    break
        except Exception:
            pass
        return total_data.decode()

    def read_func(self):
        while True:
            if not self.ready_to_read:
                self.message_from = self.recv()
                if self.message_from:
                    logging.info(f'{self.who} -> {self.message_from}')
                    self.ready_to_read = True
            else:
                time.sleep(self._DELAY)
            if self.exit:
                break

    def write_func(self):
        while True:
            if self.ready_to_write:
                logging.info(f'{self.who} <- {self.message_to}')
                try:
                    self.sock.send(self.message_to.encode())
                    print('Send', self.message_to)
                    self.ready_to_write = False
                except Exception:
                    pass
            else:
                time.sleep(self._DELAY)
            if self.exit:
                break

    def start(self):
        if self.who != 'p':
            self.thread_to_write.start()
        self.thread_to_read.start()

    def close(self):
        logging.debug(f'{self.who} exit')
        self.ready_to_write = False
        self.ready_to_read = False
        self.thread_to_read.join()
        self.thread_to_write.join()
        self.exit = True
        self.sock.close()
