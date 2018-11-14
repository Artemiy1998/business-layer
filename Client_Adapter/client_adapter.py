import json
import time
import logging
import sys
import os

from threading import Thread, RLock


logging.basicConfig(format=u' %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG, filename='clad.log')


# ATTENTION! Before use this class configure your logging.
class ClientAdapter:

    def __init__(self, address_client,
                 client_socket_conn, client_socket_address,
                 address_scene3d, socket_scene3d,
                 address_planner, socket_planner,
                 buffer_size, message_error=b'Error!', clients=None):

        self.client_socket_conn = client_socket_conn
        self.client_socket_address = client_socket_address

        self.socket_scene3d = socket_scene3d
        self.socket_planner = socket_planner

        self.address_client = address_client
        self.address_scene3d = address_scene3d
        self.address_planner = address_planner

        self.buffer_size = buffer_size
        self.message_error = message_error
        self.clients = clients

        self.data_json = None
        self.thread_to_work = Thread(name=f'UClient-{address_client}',
                                     target=self.work)
        self.lock = RLock()

    def except_func(self, def_send, socket_component, socket_address,
                    socket_another_component):
        for _ in range(3):
            time.sleep(60)
            try:
                socket_component.connect(socket_address)
                logging.info(socket_address[0] + '  Reconnect')
                def_send()
            except ConnectionRefusedError:
                pass
        self.client_socket_conn.send(self.message_error)
        logging.info(f'Send Client {self.message_error.decode()}')
        socket_another_component.send(b'e')

        socket_component.close()
        socket_another_component.close()
        self.client_socket_conn.close()
        logging.info('Scene3d, Client Adapter, Client close')
        sys.exit(0)

    def send_planner(self):
        """
        @brief Function sends a request to the planer from the client
        all parameters used in this function - class variables.
        Function return nothing.
        """
        try:
            data_to_send = json.dumps(self.data_json)
            data_to_send = self.add_separator(data_to_send)
            self.socket_planner.send(data_to_send.encode())
            print(data_to_send)
            logging.info(f'Send Planner {data_to_send}')
        except ConnectionRefusedError:
            logging.error('ConnectionRefusedError')
            self.client_socket_conn.send(
                b'Error, Connection Refused wait 3 minutes')
            self.except_func(self.send_planner, self.socket_planner,
                             self.address_planner, self.socket_scene3d)

    def send_scene3d(self):
        """
        @brief Function sends a request to the scene from the client
        all parameters used in this function - class variables.
        Function return response from the scene.
        """
        try:
            self.socket_scene3d.send(str(self.data_json.get('name')).encode())
            data_into_scene3d = self.socket_scene3d.recv(self.buffer_size)
            print('Response from scene3d:', data_into_scene3d.decode())
            return data_into_scene3d
        except ConnectionRefusedError:
            logging.error('ConnectionRefusedError')
            self.client_socket_conn.send(
                b'Error, Connection Refused wait 3 minutes')
            logging.info('Send Client:Refused, wait 3 minutes')
            self.except_func(self.send_scene3d, self.socket_scene3d,
                             self.address_scene3d, self.socket_planner)
        except ConnectionResetError:
            logging.error('ConnectionResetError')
            self.client_socket_conn.send(
                b'Error, Connection Refused wait 3 minutes')
            logging.info('Send Client: Reset, wait 3 min')
            self.except_func(self.send_scene3d, self.socket_scene3d,
                             self.address_scene3d, self.socket_planner)

    def add_separator(self, message):
        message += '|'
        return message

    def process_multiple_json(self, message):
        tasks = message.count('flag')
        if tasks == 1:
            return [message]

        result = []
        pos_1, pos_2 = 2, 0
        for _ in range(tasks - 1):
            pos_2 = message.find('flag', pos_1 + 1)
            result.append(message[pos_1 - 2:pos_2 - 2])
            pos_1 = pos_2

        result.append(message[pos_2 - 2:])
        return result

    # Read all data from socket buffer.
    def receive(self, sock):
        total_data = b''
        try:
            while True:
                recv_data = sock.recv(self.buffer_size)
                if recv_data:
                    total_data += recv_data
                else:
                    break
        except Exception:
            pass
        return total_data.decode()

    def work(self):
        self.lock.acquire()
        self.clients.append(self)
        self.lock.release()

        count = 0
        self.client_socket_conn.setblocking(False)
        print(f'Connected {self.client_socket_address}')
        while True:
            data = ''
            try:
                data = self.receive(self.client_socket_conn)
                messages = self.process_multiple_json(data)
            except ConnectionResetError:
                print('Disconnect by reset', self.client_socket_address)
                break
            except Exception as e:
                print('Exception:', e)
                print('Message received:', data)
                print('Disconnect', self.client_socket_address)
                break

            for msg in messages:
                if not msg:
                    continue
                self.data_json = json.loads(msg)

                print(isinstance(self.data_json, dict))
                if isinstance(self.data_json, dict):
                    # logging.info(f'From {client_Socket_Address[0]} '
                    #              f'recv {data_Json["command"]}')
                    try:
                        if self.data_json.get('flag') == '0':
                            self.send_planner()
                        elif self.data_json.get('flag') == '1':
                            data_send_byte = self.send_scene3d()
                            self.client_socket_conn.send(data_send_byte)
                        elif self.data_json.get('flag') == 'e':
                            self.lock.acquire()
                            self.clients.pop()
                            self.lock.release()

                            if not self.clients:
                                print('Send exit commands')
                                self.socket_scene3d.send(b'e')
                                logging.info('Send Scene3d e')
                                self.socket_planner.send(b'e|')
                                logging.info('Send Planner e')
                                self.socket_planner.close()
                                logging.info('Planner disconnect')
                                self.socket_scene3d.close()
                                logging.info('Scene3d disconnect')
                                self.client_socket_conn.close()
                                logging.info('Client disconnect')
                                time.sleep(3)
                                os._exit(0)  # Planning crash for test builds.
                            else:
                                print('Not the last connection interrupted.')
                    except AttributeError:
                        logging.error('Not JSON')
                else:
                    logging.error('Not JSON')
                count += 1
        self.client_socket_conn.close()

    def run(self):
        self.thread_to_work.start()
