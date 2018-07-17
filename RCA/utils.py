""" @author Urazov Dilshod
Documentation for Robot Control Adapter module

@brief Utilities for RCA

"""
import socket
from wrapt import synchronized
import logging

# logging
logging.basicConfig(
    format=u' %(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.DEBUG,
    filename='RCA.log')


@synchronized
class ClientForScene:
    """@class ClientForScene
       @brief This is class represents thread-safe socket client for sending messages to 3dscene

    """

    def __init__(self, port):
        """
        @brief Constrictor of ClientForScene class
        @param self
        @param port Port of 3dscene

        Initialization of socket, connection to 3dscene, sending initiate message to it
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect(('localhost', port))
            self.socket.send(b'RCA')
        except ConnectionRefusedError:
            logging.error('Connection to 3dscene is refused')

    @synchronized
    def send(self, message):
        """
        @brief Send message to 3dscene
        @param self
        @param message
        """
        try:
            self.socket.send(message)
        except ConnectionRefusedError:
            logging.error('Connection to 3dscene is refused')
