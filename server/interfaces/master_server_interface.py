'''
This file contains the interface for the Master Server service.
'''

from abc import ABC, abstractmethod
import rpyc
from utils.custom_req_res import Request, Response

class IMasterServerService(ABC):
    '''
    Interface for the Master Server service
    '''
    clients: dict[str, str] = {}
    @abstractmethod
    def on_connect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is established
        '''
    @abstractmethod
    def on_disconnect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is closed
        '''
    @abstractmethod
    def update_self(self, request: Request) -> (Response | Exception):
        '''
        Update the master server
        '''
