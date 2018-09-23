import socket
import logging

from threading import Thread


logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='RCA.log'
)


class CommonSocket(object):
    def __init__(self, sock, ready_to_read, ready_to_write):
        if not isinstance(sock, socket.socket):
            raise TypeError("not Socket type")
        if not isinstance(ready_to_read, bool) or \
           not isinstance(ready_to_write, bool):
            raise TypeError("not Bool type")
        self.sock = sock
        self.sock.setblocking(False)
        self.who = sock.recv(1024).decode()
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

    def recv(self):
        total_data = ''
        try:
            while True:
                data = self.sock.recv(1024)
                if data:
                    total_data += data.decode()
                else:
                    break
        except Exception:
            pass
        return total_data

    def read_func(self):
        while True:
            if not self.ready_to_read:
                self.message_from = self.recv()
                if self.message_from:
                    logging.info(f'{self.who} : {self.message_from}')
                    self.ready_to_read = True
            if self.exit:
                break

    def write_func(self):
        while True:
            if self.ready_to_write:
                logging.info(f'{self.who} : {self.message_to}')
                try:
                    self.sock.send(self.message_to.encode())
                    self.ready_to_write = False
                except Exception:
                    pass
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
