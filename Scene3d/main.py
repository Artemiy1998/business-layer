from threading import  Thread
from Scene3d.def_planner import planner_func
from Scene3d.def_rca import rca_func
from Scene3d.def_client_adapter import client_adapter_func
from Scene3d.utils import json_data
import socket

# config
host = ''
size = 1024
port_rca = 9099
port_planner = 10000
port_3dscene = 9093
port_rcv_fanuc = 9080
port_rcv_cart = 9081
robo_dict = {'f': 'none', 't': 'none'}
# config end

sock_main = socket.socket()
sock_main.bind(('localhost',9093))
sock_main.listen(3)

while True:
    client, address = sock_main.accept()
    who_is_it = client.recv(1024).decode()
    if who_is_it == 'planner':
        planer_thread = Thread(target=planner_func, args=(client, json_data))
        print("planner")
        planer_thread.start()
    elif who_is_it == 'RCA':
        rca_thread = Thread(target=rca_func, args=(client, json_data))
        print("rca")
        rca_thread.start()
    elif who_is_it == 'ClAd':
        client_adapter_thread = Thread(target=client_adapter_func, args=(client, json_data))
        print("clad")
        client_adapter_thread.start()
    else:
        continue



