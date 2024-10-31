'''
Server side of the dropbox application
'''
import shutil
import os

import rpyc
import rpyc.core
import rpyc.core.protocol

from utils.custom_req_res import Response
from utils.custom_req_res import Request
from utils.server.helpers import get_diff_path, normalize_path

from server.services.base.base_service import Service
from server.interfaces.common.health_interface import IHealthService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.common.dropbox_interface import IDropBoxServiceV1

@rpyc.service
class DropbBoxV1Service(
    IDropBoxServiceV1,
    Service,
    rpyc.Service
):
    '''
    DropBox service
    '''
    def __init__(
        self,
        client_service: IClientServerService,
        health_service: IHealthService
        ) -> None:
        super().__init__(health_service)
        self.client_service: IClientServerService = client_service
        self.health_service: IHealthService = health_service
        self.server_relative_path: str = client_service.get_server_relative_path()

    def on_connect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is established
        with the master server
        '''
        print("Hello Master!", conn)

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is closed
        with a client
        '''
        print("Goodbye client!", conn)
    @rpyc.exposed
    def set_client_path(self, cwd: str) -> None:
        return
    @rpyc.exposed
    def upload_chunk(self, request: Request, chunk: int) -> Response:
        '''
        upload a chunk of a file to the server
        '''
        @self.client_service.apply_set_client_dir_state_wrapper
        def inner_upload(request: Request, chunk: int) -> Response:
            print(f"Uploading chunk: {chunk} for request: {request}")
            print(f"Uploading chunk of size {len(chunk)} bytes...")
            #Caso chunk vacio-- file by chunk empty
            if request.action in ['file_created', 'modified', 'touch', 'cp', 'created']:
                try:
                    # delete_file(self.server_relative_path)
                    with open(self.server_relative_path, "wb") as arc:
                        arc.write(chunk)
                    return Response(
                        message=request.file_name \
                        + " succesfully modified file!",
                        status_code=0
                    )
                except (OSError, IOError) as e:
                    print(f"Error: {e}")
                    return Response(
                        error=e,
                        message=f'Error in action: {request.action}, error: {e}',
                        status_code=13
                    )
            elif request.action == "mv":
                dst_path: str = request.destination_path
                print(dst_path)
                print(self.server_relative_path)
                try:
                    print(f"destination_path: {dst_path}")
                    src_path: str = self.server_relative_path
                    # Get difference from path to delete, then change to the path to overwrite
                    diff_path: str = get_diff_path(dst_path, self.client_path)
                    new_relative_path: str = os.path.join(self.server_relative_path, diff_path)
                    # normalize
                    self.server_relative_path: str = normalize_path(new_relative_path)
                    # Handle the case when the file does not exist (create empty file)
                    if not os.path.exists(self.server_relative_path):
                        with open(self.server_relative_path, "wb") as empty_file:
                            empty_file.write(b'')
                    shutil.move(src_path, self.server_relative_path)
                    return Response(
                        message=request.file_name +\
                        " succesfully moved file!",
                        status_code=0
                    )
                except (OSError, IOError) as e:
                    print(f"Error: {e}")
                    return Response(error=e, message="Error: ", status_code=13)
            else:
                return Response(error="ActionError", message="Error: ", status_code=3)
        return inner_upload(request, chunk)
    @rpyc.exposed
    def file_creation(self, request: Request) -> Response: #touch en principio hecho
        '''
        Create a file on the server
        '''
        @self.client_service.apply_set_client_dir_state_wrapper
        def inner_file_creation(request: Request) -> Response:
            try:
                open(self.server_relative_path, 'x', encoding='utf-8')
                print(request)
                return Response(message=request.file_name + " succesfully touched!")
            except FileExistsError:
                print(f"Something went wrong: the file {request.file_name}\
                    already exists in the given path."
                )
                return Response(error="FileExistsError", message="Error: ", status_code=6)
            except (OSError, IOError) as e:
                print(f"Error: {e}")
                return Response(error=e, message=f'Error en action: {e}', status_code=13)
        return inner_file_creation(request)

    @rpyc.exposed
    def file_deletion(self, request: Request) -> Response: #rm
        '''
        Delete a file on the server
        '''
        @self.client_service.apply_set_client_dir_state_wrapper
        def inner_file_deletion(request: Request) -> Response:
            try:
                os.remove(self.server_relative_path)
                print(request)
                return Response(message=request.file_name + " succesfully removed!", status_code=0)
            except FileNotFoundError:
                print(f"Something went wrong: file {request.file_name} not found.")
                return Response(error="FileNotFoundError",
                                message="Something went wrong: file " +\
                                    {request.file_name} + " not found.",
                                status_code=5
                            )
            except (OSError, IOError) as e:
                print(f"Error: {e}")
                return Response(error=e, message="Error: ", status_code=13)
        return inner_file_deletion(request)
    @rpyc.exposed
    def dir_creation(self, request: Request) -> Response: #mkdir
        '''
        Create a directory on the server
        '''
        @self.client_service.apply_set_client_dir_state_wrapper
        def inner_dir_creation(request: Request) -> Response:
            try:
                os.mkdir(self.server_relative_path)
                return Response(message = request.file_name + " succesfully cretated directory!")

            except FileExistsError:
                print(f"Something went wrong: the directory {request.file_name}\
                    already exists in the given path."
                )
                return Response(error = "FileExistsError", message = "Error: ", status_code = 6)
            except (OSError, IOError) as e:
                print(f"Error: {e}")
                return Response(error=e, message="Error: ", status_code=13)
        return inner_dir_creation(request)
    @rpyc.exposed
    def dir_deletion(self, request: Request) -> Response: #rmdir
        '''
        Delete a directory on the server
        '''
        @self.client_service.apply_set_client_dir_state_wrapper
        def inner_dir_deletion(request: Request) -> Response:
            try:
                os.rmdir(self.server_relative_path)
                return Response(message = request.file_name + " succesfully deleted directory!")

            except FileNotFoundError:
                print(f"Something went wrong: the directory {request.file_name} not found.")
                return Response(error = "FileNotFoundError", message = "Error: ", status_code = 5)
            except (OSError, IOError) as e:
                print(f"Something went wrong: the directory {request.file_name} is not empty.")
                return Response(error=e, message="Error: ", status_code=13)
        return inner_dir_deletion(request)
