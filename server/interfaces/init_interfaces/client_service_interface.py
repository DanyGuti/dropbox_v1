'''
This file contains the interface for the client-server service
'''
from server.imports.import_server_base import Callable,\
    Request, ABC, abstractmethod

class IClientServerService(ABC):
    '''
    Interface for the client-server service
    '''
    @staticmethod
    @abstractmethod
    def apply_set_client_dir_state_wrapper(
        method: Callable[['IClientServerService',
        Request], (bool | Exception)],
    ) -> (bool | Exception):
        '''
        Wrapper to set the client directory state
        '''
    @abstractmethod
    def set_client_path(self, cwd: str, user: str) -> None:
        '''
        Get the health status of the server
        '''
    @abstractmethod
    def set_client_state_path(self, request: Request) -> None:
        '''
        Set the health status of the server
        '''
    @abstractmethod
    def get_client_path(self) -> str:
        '''
        Get the client path
        '''
    @abstractmethod
    def get_server_relative_path(self) -> str:
        '''
        Get the server relative path
        '''
