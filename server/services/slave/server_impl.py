'''
Server side of the dropbox application
'''
from server.imports.import_server_base import rpyc, os, shutil\
    , Request, Response, get_diff_path, normalize_path

from server.services.base.base_service import Service
from server.interfaces.common.health_interface import IHealthService
from server.services.base.client_server_service import ClientServerService
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
        self.client_service.set_client_path(cwd)
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def upload_chunk(self, request: Request, chunk: int) -> Response:
        '''
        upload a chunk of a file to the server
        '''
        print(f"Uploading chunk of size {len(chunk)} bytes...")
        #Caso chunk vacio-- file by chunk empty
        self.server_relative_path: str = self.client_service.get_server_relative_path()
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
                diff_path: str = get_diff_path(dst_path, self.client_service.get_client_path())
                new_relative_path: str = os.path.join(self.server_relative_path, diff_path)
                # normalize
                self.server_relative_path: str = normalize_path(new_relative_path)
                # Handle the case when the file does not exist (create empty file)
                print(f"Moving file from {src_path} to {self.server_relative_path}")
                print(diff_path)
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
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def file_creation(self, request: Request) -> Response: #touch en principio hecho
        '''
        Create a file on the server
        '''
        try:
            open(self.client_service.get_server_relative_path(), 'x', encoding='utf-8')
            return Response(message=request.file_name + " succesfully touched!")
        except FileExistsError:
            print(f"Something went wrong: the file {request.file_name}\
                already exists in the given path."
            )
            return Response(error="FileExistsError", message="Error: ", status_code=6)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message=f'Error en action: {e}', status_code=13)

    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def file_deletion(self, request: Request) -> Response: #rm
        '''
        Delete a file on the server
        '''
        try:
            os.remove(self.client_service.get_server_relative_path())
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
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def dir_creation(self, request: Request) -> Response: #mkdir
        '''
        Create a directory on the server
        '''
        try:
            os.mkdir(self.client_service.get_server_relative_path())
            return Response(message = request.file_name + " succesfully cretated directory!")

        except FileExistsError:
            print(f"Something went wrong: the directory {request.file_name}\
                already exists in the given path."
            )
            return Response(error = "FileExistsError", message = "Error: ", status_code = 6)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message="Error: ", status_code=13)
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def dir_deletion(self, request: Request) -> Response: #rmdir
        '''
        Delete a directory on the server
        '''
        try:
            os.rmdir(self.client_service.get_server_relative_path())
            return Response(message = request.file_name + " succesfully deleted directory!")

        except FileNotFoundError:
            print(f"Something went wrong: the directory {request.file_name} not found.")
            return Response(error = "FileNotFoundError", message = "Error: ", status_code = 5)
        except (OSError, IOError) as e:
            print(f"Something went wrong: the directory {request.file_name} is not empty.")
            return Response(error=e, message="Error: ", status_code=13)
