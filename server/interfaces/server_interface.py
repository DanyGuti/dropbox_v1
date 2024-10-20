'''
Interface for the Servers
'''

from abc import ABC, abstractmethod
from utils.custom_req_res import Request

class IServerService(ABC):
    '''
    Interface for the Servers
    '''
    health_status: float = 0.0
    client_path: str = ""
    ip_service: str = ""
    port: int = 0
    server_id: int = 0
    @abstractmethod
    def get_health_status(self) -> float:
        '''
        Get the health status of the server
        '''
    @abstractmethod
    def set_health_status(self, health_status: float) -> None:
        '''
        Set the health status of the server
        '''
    @abstractmethod
    def set_client_path(self, cwd: str) -> str:
        '''
        Set the client path when the connection is established
        '''
    @abstractmethod
    def get_client_path(self) -> str:
        '''
        Get the client path
        '''
    @abstractmethod
    def set_server_id(self, server_id: int) -> None:
        '''
        Set the server id
        '''
    @abstractmethod
    def get_server_id(self) -> int:
        '''
        Get the server id
        '''
    @abstractmethod
    def set_client_state_path(self, request: 'Request') -> bool:
        '''
        Set the client state path
        '''
    @abstractmethod
    def get_ip_service(self) -> str:
        '''
        Get the ip service
        '''
    @abstractmethod
    def get_port(self) -> int:
        '''
        Get the port
        '''
    @abstractmethod
    def set_ip_service(self, ip_service: str) -> None:
        '''
        Set the ip service
        '''
    @abstractmethod
    def set_port(self, port: int) -> None:
        '''
        Set the port
        '''
