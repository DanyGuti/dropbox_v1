'''
This module represents the
master server (coordinator)
will have one replica server
'''

from server.imports.import_server_base import Callable, rpyc, os, inspect\
    , Request, Response

from server.services.base.base_service import Service
from server.services.master.node_coordinator import NodeCoordinator
from server.interfaces.common.dropbox_interface import IDropBoxServiceV1
from server.interfaces.common.health_interface import IHealthService
IP_ADDRESS_SLAVE_SERVER_SERVICE: str = "158.227.124.92"

def apply_slave_distribution_wrapper(
    method: Callable[['MasterServerService', Request, int],
                    (Response | Exception)]) -> Callable[['MasterServerService', Request, int],
                    (Response | Exception)]:
    '''
    Wrapper to distribute load
    on each call to the master server
    '''
    def wrapper(
        self: 'MasterServerService',
        req_client: Request,
        chunk_size: int = 0
    ) -> (Response | Exception):
        try:
            result: (Response | Exception) = self.node_coordinator.distribute_load_slaves(
                req_client,
                chunk=chunk_size
            )
            if isinstance(result, Exception):
                raise result
            sig = inspect.signature(method)
            if len(sig.parameters) == 3:  # method accepts three parameters
                return method(self, req_client, chunk_size)
            else:  # method accepts only two parameters
                return method(self, req_client)
        except (ConnectionError, TimeoutError, ValueError) as e:
            print(f"Error distributing load: {e}")
            return e
    return wrapper

@rpyc.service
class MasterServerService(
    Service,
    IDropBoxServiceV1,
    rpyc.Service
):
    '''
    Master server service class
    '''
    clients: dict[str, str] = {}
    def __init__(
        self,
        coordinator: NodeCoordinator,
        health_service: IHealthService
        ) -> None:
        super().__init__(health_service=health_service)
        self.node_coordinator: NodeCoordinator = coordinator
        self.server_relative_path: str = os.path.join(os.getcwd())
        self.set_server_id(1)
    def on_connect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is established
        with a client
        '''
        print("Hello client!", conn)

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is closed
        with a client
        '''
        print("Goodbye client!", conn)
    @rpyc.exposed
    def set_client_path(self, cwd: str) -> None:
        return self.node_coordinator.set_client_path(cwd)
    @rpyc.exposed
    @apply_slave_distribution_wrapper
    def upload_chunk(self, request: Request, chunk: int) -> (Response | Exception):
        pass
    @rpyc.exposed
    @apply_slave_distribution_wrapper
    def file_creation(self, request: Request) -> (Response | Exception):
        pass
    @rpyc.exposed
    @apply_slave_distribution_wrapper
    def file_deletion(self, request: Request) -> (Response | Exception):
        pass
    @rpyc.exposed
    @apply_slave_distribution_wrapper
    def dir_creation(self, request: Request) -> (Response | Exception):
        pass
    @rpyc.exposed
    @apply_slave_distribution_wrapper
    def dir_deletion(self, request: Request) -> (Response | Exception):
        pass
