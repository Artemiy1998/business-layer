import os
import configparser

from http.server import HTTPServer
from RequestHandler import MyRequestHandler


# config
config_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'configBL.ini'
)
config = configparser.ConfigParser()
config.read(config_file)

host = config['HOSTS']['Main_host']
port_cl_ad = int(config['PORTS']['Port_cl_adapter'])
# end config


addr_server = (host, 3331)
httpd = HTTPServer(addr_server, MyRequestHandler)
httpd.serve_forever()
