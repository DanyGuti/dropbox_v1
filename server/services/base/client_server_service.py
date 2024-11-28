'''
Module for the client_server_service
'''

from server.imports.import_server_base import os, Request, Callable, Response
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
import time

def get_diff_path(path: str, client_path: str) -> str:
    '''
    Get the difference between the two paths
    '''
    return os.path.relpath(path, client_path)
def normalize_path(path: str) -> str:
    '''
    Normalize the path
    '''
    return os.path.normpath(path)

class ClientServerService(IClientServerService):
    '''
    Client Server Service
    '''
    def __init__(self) -> None:
        self.client_path: str = ""
        self.clients_paths: dict[str, str] = {}
        self.server_relative_path: str = os.path.join(os.getcwd() + "/dropbox_genial_loli_app")
    @staticmethod
    def apply_set_client_dir_state_wrapper(
        method: Callable[['ClientServerService',
        Request], (bool | Exception)],
    ) -> (bool | Exception):
        '''
        Wrapper to set the client directory state
        '''
        def wrapper(
            self: 'ClientServerService',
            *args: tuple[Request],
            **kwargs: dict[str, any]
        ) -> (bool | Exception):
            req_client: Request = args[0]
            result = self.client_service.set_client_state_path(req_client)
            if result is False:
                print(f"Failed to set client state path: {result}")
                return result  # Exit early if setting client path fails
            return method(self, *args, **kwargs)
        return wrapper
    def set_client_path(self, cwd: str, user: str) -> Response:
        '''
        Set the client path when the connection is established
        '''
        self.client_path = cwd
        # Set the clients paths
        self.clients_paths[user] = cwd
        return Response(
            status_code=0,
            message="Client path set",
            error=None,
            time_sent=time.time()
        )
    def get_client_path(self) -> str:
        '''
        Get the client path
        '''
        return self.client_path
    def set_client_state_path(self, request: Request) -> Response:
        '''
        Set the client state path
        '''
        try:
            if request.task.user not in self.clients_paths:
                return Response(
                    status_code=1,
                    message="User not found",
                    error="Error setting client path",
                    time_sent=time.time()
                )
            # if request.src_path in [self.client_path, ""]:
            #     return False
            # Getting the difference between the two paths
            diff_path: str = get_diff_path(
                request.src_path,
                self.clients_paths[request.task.user]
            )
            # Update server_relative_path and normalize it
            new_relative_path: str = os.path.join(self.server_relative_path, diff_path)
            # Remove the '..' from the path, if any
            self.server_relative_path: str = normalize_path(new_relative_path)
            # Update the client path
            self.client_path: str = request.src_path
            self.clients_paths[request.task.user] = request.src_path
            # Check if the updated path exists
            print(f"Checking existence of path: {self.server_relative_path}")
            if request.action not in [
                'file_created',
                'modified',
                'touch',
                'cp',
                'created',
                'mv',
                'mkdir'
            ]:
                if not os.path.exists(self.server_relative_path):
                    print(self.server_relative_path)
                    print(f"Something went wrong: the parent directory\
                        {os.path.dirname(self.server_relative_path)}\
                    not found.")
                    return Response(
                        status_code=2,
                        message="Parent directory not found",
                        error="Error setting client path",
                        time_sent=time.time()
                    )
            return Response(
                status_code=0,
                message="Client path set",
                error=None,
                time_sent=time.time()
            )
        except (OSError, IOError) as e:
            print("ERRORRRR")
            print(f"Error: {e}")
            return Response(
                status_code=3,
                message="Error setting client path",
                error=str(e),
                time_sent=time.time()
            )
    def get_server_relative_path(self) -> str:
        '''
        Get the server relative path
        '''
        return self.server_relative_path
