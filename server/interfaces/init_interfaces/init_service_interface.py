'''
This file contains the interface for the Init service.
'''
from server.imports.import_server_base import ABC, abstractmethod,\
    ForkingServer, ThreadedServer, ServerConfig

from server.services.master.master_server import MasterServerService
from server.services.slave.server_impl import DropbBoxV1Service

class IInitService(ABC):
    '''
    Interface for the Init service
    '''
    @abstractmethod
    def create_service(self, config: ServerConfig) -> None:
        '''
        Create the server config
        '''
    @abstractmethod
    def create_master_service(self, config: ServerConfig) -> None:
        '''
        Create the master service
        '''
    @abstractmethod
    def create_slave_service(self, config: ServerConfig) -> None:
        '''
        Create the slave service
        '''
    @abstractmethod
    def start_server(
        self,
        service: (MasterServerService | DropbBoxV1Service),
        config: ServerConfig
    ) -> (ForkingServer | ThreadedServer):
        '''
        Start the master service
        '''
