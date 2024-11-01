'''
This file contains the interface for exposing the service
'''
from server.imports.import_server_base import ABC, abstractmethod, rpyc

class IServiceExposed(ABC):
    '''
    Interface for the service exposed
    '''
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
