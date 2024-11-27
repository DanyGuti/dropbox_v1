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

class FactoryServices:
    '''
    Factory Services
    '''
    def create_client_service(self) -> IClientServerService:
        '''
        Create the client service
        '''
        return ClientServerService()
    def create_master_coordinator(self) -> None:
        '''
        Create the master coordinator
        '''
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
        return IElection
    def create_master_service(self) -> MasterServerService:
        '''
        Create the master service
        '''
        # Create the master service by including a NodeCoordinator or any relevant services
        node_coordinator = NodeCoordinator()
        return MasterServerService(coordinator=node_coordinator, health_service=None)
