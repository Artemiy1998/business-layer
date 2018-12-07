import logging

logging.basicConfig(level=logging.DEBUG)
from spyne import Application, rpc, ServiceBase, Float, Unicode, Array, Iterable, ComplexModel, XmlAttribute
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import socket
import os
import configparser
import json

config_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'configBL.ini'
)
config = configparser.ConfigParser()
config.read(config_file)

host = config['HOSTS']['Main_host']
port_cl_ad = int(config['PORTS']['Port_cl_adapter'])

sock = socket.socket()
sock.connect((host,port_cl_ad))


class StartTime(ComplexModel):
    time = Float
    intensity = XmlAttribute(Float)


class EndTime(ComplexModel):
    time = Float


class Operation(ComplexModel):
    id = XmlAttribute(Unicode)
    name = Unicode
    priority = Float
    resource = Unicode
    start = Array(StartTime)
    end = Array(EndTime)


class Process(ComplexModel):
    id = XmlAttribute(Unicode)
    operations = Array(Operation)


class Resource(ComplexModel):
    id = XmlAttribute(Unicode)
    worktime = Float


class Schedule(ComplexModel):
    processes = Array(Process)
    quality = Array(Unicode)
    resources = Array(Resource)


class HelloWorldService(ServiceBase):
    @rpc(Schedule, _returns=Iterable(Unicode))
    def set_scenario(ctx, schedule):
        print(schedule)
        for process in schedule.processes:

            answer = {
                "flag": "0",
                "name": "",
                    "Scenario": [
                        {
                            "parallel": "false",
                            "name": "f",
                            "time": 30,
                            "energy": 0,
                            "command": operation.name

                        } for operation in process.operations
                    ]
                }
            json_data = json.dumps(answer)
            print(json_data)
            sock.send(json_data.encode())
        return dict(status="ok")


application = Application([HelloWorldService],
                          tns='spyne.examples.hello',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11()
                          )

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 3331, wsgi_app)
    server.serve_forever()
