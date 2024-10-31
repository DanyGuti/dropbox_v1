'''
Factory Services module
'''

from server.services.base.client_server_service import ClientServerService
from server.services.base.health_service import HealthService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.common.health_interface import IHealthService

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
