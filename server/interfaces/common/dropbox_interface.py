'''
This file contains the interface for the DropBox service.
'''
from server.imports.import_server_base import ABC\
    , abstractmethod, rpyc, Request, Response

class IDropBoxServiceV1(ABC):
    '''
    Interface for the DropBox service
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
    @abstractmethod
    def set_client_path(self, request: Request) -> Response:
        '''
        Set the client path
        '''
    @abstractmethod
    def upload_chunk(self, request: Request) -> Response:
        '''
        Upload a chunk of a file to the server
        '''
    @abstractmethod
    def file_creation(self, request: Request) -> Response:
        '''
        Create a file on the server
        '''
    @abstractmethod
    def file_deletion(self, request: Request) -> Response:
        '''
        Delete a file on the server
        '''
    @abstractmethod
    def dir_creation(self, request: Request) -> Response:
        '''
        Create a directory on the server
        '''
    @abstractmethod
    def dir_deletion(self, request: Request) -> Response:
        '''
        Delete a directory on the server
        '''