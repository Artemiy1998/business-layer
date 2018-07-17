import os
import socket
import sys
import configparser

# now planner do nothing but transfer

# config
config_file = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)),
    'configBL.ini')
config = configparser.ConfigParser()
config.read(config_file)

host = config['HOSTS']['Main_host']
port_cl_ad = int(config['PORTS']['Port_cl_adapter'])
port_planner = int(config['PORTS']['Port_planner'])
port_3d_scene = int(config['PORTS']['Port_3d_scene'])
port_rob_ad = int(config['PORTS']['Port_rca'])
buffersize = int(config['PARAMS']['Buffersize'])

who = 'p'
robo_dict = ['f', 't']
# end config

sock_rob_ad = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_rob_ad.connect((host, port_rob_ad))
sock_rob_ad.send(who.encode())

sock_3d_scene = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_3d_scene.connect((host, port_3d_scene))
sock_3d_scene.send(b'planner')

sock_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_serv.bind((host, port_planner))
sock_serv.listen(1)
conn, addr = sock_serv.accept()


def get_scene():
    sock_3d_scene.send(b'get_scene')


while True:

    data = conn.recv(buffersize)
    message = data.decode()
    print(message)
    if message == 'e':
        for robot in robo_dict:
            message = robot + ':' + 'e'
            sock_rob_ad.send(message.encode())
        sock_rob_ad.send(b'e')
        sys.exit(0)

    sock_rob_ad.send(data)
