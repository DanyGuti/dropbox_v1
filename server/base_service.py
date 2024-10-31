'''
This module provides the base server service
'''
from server.interfaces.health_interface import IHealthService

class Service():
    '''
    Base server service class
    '''
    client_path: str = ""
    ip_service: str = ""
    port: int = 0
    server_id: int = 0
    def __init__(
        self,
        health_service: IHealthService,
    ) -> None:
        self.health_service: IHealthService = health_service
    def set_server_id(self, server_id: int) -> None:
        '''
        Set the server id
        '''
        self.server_id = server_id
    def get_server_id(self) -> int:
        '''
        Get the server id
        '''
        return self.server_id
    def get_ip_service(self) -> str:
        '''
        Get the IP service
        '''
        return self.ip_service
    def get_port(self) -> int:
        '''
        Get the port
        '''
        return self.port
    def set_ip_service(self, ip_service: str) -> None:
        '''
        Set the IP service
        '''
        self.ip_service = ip_service
    def set_port(self, port: int) -> None:
        '''
        Set the port
        '''
        self.port = port
