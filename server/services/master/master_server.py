'''
This module represents the
master server (coordinator)
will have one replica server
'''

from server.imports.import_server_base import Callable, rpyc, os, inspect\
    , Request, Response, time

from server.services.base.base_service import Service
from server.services.master.node_coordinator import NodeCoordinator
from server.interfaces.common.dropbox_interface import IDropBoxServiceV1
from server.services.base.client_server_service import ClientServerService
from server.interfaces.common.health_interface import IHealthService
from server.interfaces.init_interfaces.master_service_interface import IMasterServerService

IP_ADDRESS_SLAVE_SERVER_SERVICE: str = "158.227.124.92"


@rpyc.service
class MasterServerService(
    Service,
    IDropBoxServiceV1,
    rpyc.Service,
    IMasterServerService
):
    '''
    Master server service class
    '''
    clients: dict[str, str] = {}
    sequence_events: list[dict[str, object]]
    def __init__(
            self,
            coordinator: NodeCoordinator,
            health_service: IHealthService#,
        ) -> None:
        super().__init__(health_service=health_service)
        self.node_coordinator: NodeCoordinator = coordinator
        self.server_relative_path: str = os.path.join(os.getcwd())
        self.sequence_events = []
        self.set_server_id(1)
        self.server_thread: rpyc.ThreadedServer = None
        
    @staticmethod
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
                self.sequence_events.append({
                    "timestamp": time.time(),
                    "user": req_client.task.user,
                    "request": req_client,
                    "acks": []
                })
                result: (Response | Exception) = self.node_coordinator.distribute_load_slaves(
                    req_client,
                    chunk=chunk_size,
                    sequence_events=self.sequence_events
                )
                print(result)
                if isinstance(result, Exception):
                    raise result
                sig = inspect.signature(method)
                if len(sig.parameters) == 3:  # method accepts three parameters
                    return method(self, req_client, chunk_size)
                return method(self, req_client)
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Error distributing load: {e}")
                return e
        return wrapper
    
    ###################################################

    @staticmethod
    def apply_modification_master_wrapper(
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
                self.sequence_events.append({
                    "timestamp": time.time(),
                    "user": req_client.task.user,
                    "request": req_client,
                    "acks": []
                })
                result: (Response | Exception) = self.node_coordinator.self_apply_request(
                    req_client,
                    chunk=chunk_size,
                    sequence_events=self.sequence_events
                )
                print(result)
                if isinstance(result, Exception):
                    raise result
                sig = inspect.signature(method)
                if len(sig.parameters) == 3:  # method accepts three parameters
                    return method(self, req_client, chunk_size)
                return method(self, req_client)
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Error distributing load: {e}")
                return e
        return wrapper
    
    ###################################################
    
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
    def set_client_path(self, request: Request) -> None:
        self.node_coordinator.set_slaves()
        cwd_client : str = request.src_path
        req_client : str = request.task.user
        self.sequence_events.append({
            "timestamp": time.time(),
            "user": request.task.user,
            "request": "set_client_path",
            "acks": []
        })
            
        return self.node_coordinator.set_client_path(cwd_client, req_client, self.sequence_events)
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    @apply_modification_master_wrapper
    @apply_slave_distribution_wrapper
    def upload_chunk(self, request: Request, chunk: int) -> (Response | Exception):
        pass
        
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    @apply_modification_master_wrapper
    @apply_slave_distribution_wrapper
    def file_creation(self, request: Request) -> (Response | Exception):
        pass  
        
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    @apply_modification_master_wrapper
    @apply_slave_distribution_wrapper
    def file_deletion(self, request: Request) -> (Response | Exception):
        pass
        
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    @apply_modification_master_wrapper
    @apply_slave_distribution_wrapper
    def dir_creation(self, request: Request) -> (Response | Exception):
        pass
        
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    @apply_modification_master_wrapper
    @apply_slave_distribution_wrapper
    def dir_deletion(self, request: Request) -> (Response | Exception):
        pass
        
    def set_thread(self, server: rpyc.ThreadedServer) -> None:
        '''
        Set the threaded server
        '''
        self.server_thread = server
    def get_thread(self) -> rpyc.ThreadedServer:
        '''
        Get the threaded server
        '''
        return self.server_thread
