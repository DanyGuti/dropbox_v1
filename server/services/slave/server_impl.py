'''
Server side of the dropbox application
'''
from server.imports.import_server_base import rpyc, Request, Response

from server.services.base.base_service import Service
from server.interfaces.common.health_interface import IHealthService
from server.services.base.client_server_service import ClientServerService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.common.dropbox_interface import IDropBoxServiceV1
from server.interfaces.local_fms_interface import IFileManagementService

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
        file_management_service: IFileManagementService,
        health_service: IHealthService
        ) -> None:
        super().__init__(health_service)
        self.client_service: IClientServerService = client_service
        self.file_management_service: IFileManagementService = file_management_service
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
            return self.file_management_service.write_chunk_no_mv(
                self.server_relative_path,
                chunk,
                request.action
            )
        if request.action == 'mv':
            return self.file_management_service.write_chunk_mv(
                self.client_service.get_server_relative_path(),
                request.destination_path,
                request.file_name,
                self.server_relative_path
            )
        return Response(error="ActionError", message="Error: ", status_code=3)
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def file_creation(self, request: Request) -> Response: #touch
        '''
        Create a file on the server
        '''
        return self.file_management_service.file_creation(
            request.file_name,
            self.client_service.get_server_relative_path()
        )
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def file_deletion(self, request: Request) -> Response: #rm
        '''
        Delete a file on the server
        '''
        return self.file_management_service.file_deletion(
            self.client_service.get_server_relative_path(),
            request.file_name,
        )
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def dir_creation(self, request: Request) -> Response: #mkdir
        '''
        Create a directory on the server
        '''
        return self.file_management_service.dir_creation(
            request.file_name,
            self.client_service.get_server_relative_path()
        )
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def dir_deletion(self, request: Request) -> Response: #rmdir
        '''
        Delete a directory on the server
        '''
        return self.file_management_service.dir_deletion(
            self.client_service.get_server_relative_path(),
            request.file_name
        )
