'''
Factory Services module
'''

from server.services.base.client_server_service import ClientServerService
from server.services.base.health_service import HealthService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.common.health_interface import IHealthService
from server.interfaces.local_fms_interface import IFileManagementService
from server.services.base.file_management_service import FileManagementService
from server.interfaces.election_interface import IElection
from server.services.master.node_coordinator import NodeCoordinator
from server.services.master.master_server import MasterServerService
from server.interfaces.init_interfaces.factory_interface import IFactoryService
from server.interfaces.init_interfaces.master_service_interface import IMasterServerService
from server.services.base.election_service import Election

class FactoryServices(IFactoryService):
    '''
    Factory Services
    '''
    def create_client_service(self) -> IClientServerService:
        '''
        Create the client service
        '''
        return ClientServerService()
    def create_health_service(self) -> IHealthService:
        '''
        Create the health service
        '''
        return HealthService(health_status=100.0)
    def create_file_management_service(self) -> IFileManagementService:
        '''
        Create the file management service
        '''
        return FileManagementService()
    def create_election_service(self) -> IElection:
        '''
        Create the election service
        '''
        return Election()
    def create_master_service(self) -> IMasterServerService:
        '''
        Create the master service
        '''
        return MasterServerService(
            coordinator=NodeCoordinator(),
            health_service=HealthService(health_status=100.0)
        )
