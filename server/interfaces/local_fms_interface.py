'''
This file contains the interface for the LOCAL file management.
'''
from server.imports.import_server_base import ABC\
    , abstractmethod, Response

class IFileManagementService(ABC):
    '''
    Interface for the File Management service
    '''
    @abstractmethod
    def write_chunk_no_mv(
        self,
        file_name: str,
        server_relative_path: str,
        chunk: bytes,
        action :str
    ) -> None:
        '''
        Write chunk of a file to the server no 'mv'
        '''
    @abstractmethod
    def write_chunk_mv(
        self,
        client_path: str,
        dst_path: str,
        file_name: str,
        server_relative_path: str,
    ) -> Response:
        '''
        Write a chunk of a file to the server with mv
        '''
    @abstractmethod
    def file_creation(
        self,
        file_name: str,
        server_relative_path: str,
    )-> Response:
        '''
        create a file
        '''
    @abstractmethod
    def file_deletion(
        self,
        server_relative_path: str,
        file_name: str,
    ) -> Response:
        '''
        Delete a file on the server
        '''
    @abstractmethod
    def dir_creation(
        self,
        dir_name: str,
        server_relative_path: str,
    ) -> Response:
        '''
        Create a directory on the server
        '''
    @abstractmethod
    def dir_deletion(
        self,
        server_relative_path: str,
        dir_name: str,
    ) -> Response:
        '''
        Delete a directory on the server
        '''
