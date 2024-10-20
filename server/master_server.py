'''
This module represents the
master server (coordinator)
will have one replica server
'''
from typing import Callable
import shutil
import os
import sys
import rpyc
import rpyc.core
import rpyc.core.protocol

from server.base_service import BaseServerService
from server.node_coordinator import NodeCoordinator

from utils.custom_req_res import Response
from utils.custom_req_res import Request
from utils.helpers import SERVERS_IP
from server.interfaces.master_server_interface import IMasterServerService
from server.interfaces.dropbox_interface import IDropBoxServiceV1
from server.interfaces.server_interface import IServerService
IP_ADDRESS_SLAVE_SERVER_SERVICE: str = "158.227.124.203"

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
        chunk_size: int
    ) -> (Response | Exception):
        try:
            result: (Response | Exception) = self.node_coordinator.distribute_load_slaves(
                req_client,
                chunk=chunk_size
            )
            if isinstance(result, Exception):
                raise result
        except (ConnectionError, TimeoutError, ValueError) as e:
            print(f"Error distributing load: {e}")
            return e
        return method(self, req_client, chunk_size)
    return wrapper

@rpyc.service
class MasterServerService(
    BaseServerService,
    IDropBoxServiceV1,
    IServerService,
    IMasterServerService,
    rpyc.Service
):
    '''
    Master server service class
    '''
    clients: dict[str, str] = {}
    def __init__(self, coordinator: NodeCoordinator) -> None:
        super().__init__()
        self.node_coordinator: NodeCoordinator = coordinator
        self.server_relative_path: str = os.path.join(os.getcwd(), "..")
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
        
    def update_self(self, request: Request) -> None:
        pass
    @rpyc.exposed
    @BaseServerService.apply_set_client_dir_state_wrapper
    def set_client_path(self, cwd: str) -> None:
        pass
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

if __name__ == "__main__":
    try:
        from rpyc.utils.server import ThreadedServer
        from rpyc.utils.server import UDPRegistryClient
        node_coordinator: NodeCoordinator = NodeCoordinator()
        t: ThreadedServer = ThreadedServer(
            MasterServerService(coordinator=node_coordinator),
            auto_register=True,
            port=50082,
            registrar=UDPRegistryClient(
                SERVERS_IP,
                50081
            )
        )
        print("Master started on port 50082", t)
        t.start()

    except (OSError, IOError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt as e:
        print("Exiting...", e)
        sys.exit(0)
    # finally:
    #     print("Exiting...")
    #     sys.exit(0)
