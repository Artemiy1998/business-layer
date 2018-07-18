import socket
from threading import Thread
from RCA.common_thread_object import CommonSocket

class Switch(object, ):
    def __init__(self, scene3d_address):
        self.scene_3d_sock = socket.socket()
        self.scene_3d_sock.connect(scene3d_address)
        self.scene_3d_sock.send(b'RCA')
        self.socket_dict = {}
        self.thread = Thread(name='switch', target=self.process)


    def run(self):
        self.thread.start()

    def append(self, client_sock):
        if not isinstance(client_sock,CommonSocket):
            raise TypeError("not CUSocket type")
        self.socket_dict.update({client_sock.who:client_sock})

    def process(self):
        while True:
            socket_dict = dict(self.socket_dict)
            for sock_name in socket_dict:
                if sock_name == 'p' and socket_dict[sock_name].ready_to_read:
                    planer_message = socket_dict[sock_name].message_from
                    socket_dict[sock_name].ready_to_read = False
                    if planer_message != '':
                        [sock_id, planer_cmd] = planer_message.split(':')
                        if sock_id not in socket_dict:
                            continue
                        socket_dict[sock_id].message_to = planer_cmd
                        socket_dict[sock_id].ready_to_write = True
                elif socket_dict[sock_name].ready_to_read:
                    message = socket_dict[sock_name].message_from
                    socket_dict[sock_name].ready_to_read = False
                    self.scene_3d_sock.send(message.encode())



