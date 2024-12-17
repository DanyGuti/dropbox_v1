'''
This file contains the interface for the client-server service
'''
from server.imports.import_server_base import Callable,\
    Request, ABC, abstractmethod, rpyc, Response

class IMasterServerService(ABC):
    '''
    Interface for the Primary client-server service
    '''
    @staticmethod
    @abstractmethod
    def apply_slave_distribution_wrapper(
        method: Callable[['IMasterServerService', Request, int],
                    (Response | Exception)]) -> Callable[['IMasterServerService', Request, int],
                    (Response | Exception)]:
        '''
        Wrapper to set the client directory state
        '''
    @abstractmethod
    def on_connect(self, conn: rpyc.Connection) -> None:
        '''
        On connect with the client
        '''
    @abstractmethod
    def on_disconnect(self, conn: rpyc.Connection) -> None:
        '''
        On disconnect with the client
        '''
    @abstractmethod
    def upload_chunk(self, request: Request) -> (Response | Exception):
        '''
        Expose the upload chunk method
        '''
    @abstractmethod
    def file_creation(self, request: Request) -> (Response | Exception):
        '''
        Expose the file creation method
        '''
    @abstractmethod
    def file_deletion(self, request: Request) -> (Response | Exception):
        '''
        Expose the file deletion method
        '''
    @abstractmethod
    def dir_creation(self, request: Request) -> (Response | Exception):
        '''
        Expose the directory creation method
        '''
    @abstractmethod
    def dir_deletion(self, request: Request) -> (Response | Exception):
        '''
        Expose the directory deletion method
        '''
    @abstractmethod
    def set_thread(self, server: rpyc.ThreadedServer) -> None:
        '''
        Set the threaded server
        '''
    @abstractmethod
    def get_thread(self) -> rpyc.ThreadedServer:
        '''
        Get the threaded server
        '''
