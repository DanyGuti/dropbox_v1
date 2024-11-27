'''
This file contains the interface for the Factory.
'''
from server.imports.import_server_base import ABC, abstractmethod\

from server.interfaces.init_interfaces.master_service_interface import IMasterServerService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.common.health_interface import IHealthService
from server.interfaces.local_fms_interface import IFileManagementService
from server.interfaces.election_interface import IElection


class IFactoryService(ABC):
    '''
    Interface for the Init service
    '''
    @abstractmethod
    def create_client_service(self) -> IClientServerService:
        '''
        Create the client service
        '''
    @abstractmethod
    def create_health_service(self) -> IHealthService:
        '''
        Create the health service
        '''
    @abstractmethod
    def create_file_management_service(self) -> IFileManagementService:
        '''
        Create the file management service
        '''
    def create_election_service(self) -> IElection:
        '''
        Create the election service
        '''
    def create_master_service(self) -> IMasterServerService:
        '''
        Create the master service
        '''
