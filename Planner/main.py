import socket
import sys

# now planner do nothing but transfer

# config
port_cl_ad = 9094
port_rob_ad = 9099
port_3d_scene = 9093
port_planner = 10000
who = 'p'
robo_dict = ['f','t']
# end config

sock_rob_ad = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_rob_ad.connect(('localhost', port_rob_ad)) # connect to RCA
sock_rob_ad.send(who.encode())

sock_3d_scene = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_3d_scene.connect(('localhost', port_3d_scene)) # connect to 3d_scene
sock_3d_scene.send(b'planner')

sock_serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_serv.bind(('localhost',port_planner))
sock_serv.listen(1)
conn, address = sock_serv.accept()

def get_scene():
    sock_3d_scene.send(b'get_scene')

while True:

    data = conn.recv(1024) # receive data from client_adapter
    message = data.decode()
    print(message)
    if message == 'e':
        for robot in robo_dict:
            message = robot + ':' + 'e'
            sock_rob_ad.send(message.encode())
        sock_rob_ad.send(b'e')
        sys.exit(0)

    sock_rob_ad.send(data)

