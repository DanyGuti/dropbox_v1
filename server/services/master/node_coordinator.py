'''
Node coordinator module
'''
from typing import Any
import threading
from rpyc.utils.classic import obtain
from rpyc.utils.server import UDPRegistryClient
from rpyc.utils.factory import discover
from rpyc.utils.factory import DiscoveryError
from server.imports.import_server_base import rpyc, Request, Response,\
    time
from server.services.slave.server_impl import DropBoxV1Service
from server.services.master.task_distributor import TaskDistributor

from server.interfaces.local_fms_interface import IFileManagementService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.election_interface import IElection



class NodeCoordinator(TaskDistributor):
    '''
    Load balancer class
    '''
    def __init__(
            self,
            file_management_service: IFileManagementService,
            client_server_service: IClientServerService
        ) -> None:
        super().__init__()
        self.slaves: dict[int: DropBoxV1Service] = {}
        self.slave_connections: dict[DropBoxV1Service, rpyc.Connection] = {}
        self.slaves_health: list[float] = []
        self.file_management_service: IFileManagementService = file_management_service
        self.client_server_service: IClientServerService = client_server_service
        self.master_coordinator_lock: threading.Lock = threading.Lock()

    def self_apply_request (
        self,
        request: Request,
        # sequence_events: list[dict[str, object]]
    ) -> (Response | Exception):
        '''
        Apply the request to the own master
        '''
        task_action: str = request.action
        try:
            response: Response = None
            match task_action:
                case 'file_created' | 'modified' | 'touch' | 'cp' | 'created':
                    response = self.file_management_service.write_chunk_no_mv(
                        request.file_name,
                        self.client_server_service.get_server_relative_path(),
                        request.chunks,
                        request.action
                    )
                case 'mv':
                    init_state_path: str = self.client_server_service.get_server_relative_path()
                    response = self.file_management_service.write_chunk_mv(
                        self.client_server_service.get_client_path(),
                        request.destination_path,
                        request.file_name,
                        init_state_path
                    )
                    self.client_server_service.set_server_relative_path(init_state_path)
                case 'touch':
                    response = self.file_management_service.file_creation(
                        request.file_name,
                        self.client_server_service.get_server_relative_path()
                    )
                case 'rm':
                    response = self.file_management_service.file_deletion(
                        self.client_server_service.get_server_relative_path(),
                        request.file_name
                    )
                case 'mkdir':
                    response = self.file_management_service.dir_creation(
                        request.file_name,
                        self.client_server_service.get_server_relative_path()
                    )
                case 'rmdir':
                    response = self.file_management_service.dir_deletion(
                        self.client_server_service.get_server_relative_path(),
                        request.file_name
                    )
                case _:
                    response = Response(
                        error="ActionError",
                        message="Error: ",
                        status_code=3,
                        time_sent=time.time(),
                        id_response=request.task.id_task
                    )
            return response
        except FileNotFoundError as e:
            return Response(
                status_code=1,
                message="Error dispatching request to self, TaskDistributor",
                error=str(e)
            )
        except FileExistsError as e:
            return Response(
                status_code=2,
                message="Error dispatching request to self, TaskDistributor",
                error=str(e)
            )
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(
                error=e,
                message=f'Error en action: {e}',
                status_code=13,
                time_sent=time.time()
            )
    def distribute_load_slaves(
        self,
        request: Request,
        sequence_events: list[dict[str, object]]
    ) -> (Response | Exception):
        '''
        Distribute the load
        '''
        try:
            with self.master_coordinator_lock:
                list_acks: list = sequence_events[-1]["acks"]
            for server_id, slave_service in self.slaves.items():
                slave_service: DropBoxV1Service
                server_id: int
                if server_id == slave_service.get_server_id():
                    try:
                        response: Response = self.dispatch_req_slave(
                            request,
                            slave=slave_service,
                        )

                        print(f"Response: {response}")
                        response = obtain(response)
                        if response.status_code == 0:
                            with self.master_coordinator_lock:
                                list_acks.append(
                                    (slave_service.get_ip_service(),
                                    slave_service.get_port(),
                                    response)
                                )
                        else:
                            print(
                                f"Error distributing load to server \
                                    {server_id}, from node coordinator"
                            )
                    except (OSError, IOError) as e:
                        print(
                            f"Error distributing load to server \
                                {server_id}, {e}, from node coordinator, general exception"
                        )
            return Response(
                status_code=0,
                message="Load distributed to slaves from node coordinator",
                error=None,
                is_broadcasted=True
            )
        except (OSError, IOError) as e:
            return Response(
                status_code=1,
                message="Error distributing load to slaves from node coordinator",
                error=str(e)
            )
    def apply_self_set_client_path(
            self,
            request: Request,
            # sequence_events: list[dict[str, object]]
    ) -> Response:
        '''
        Set the initial path of the server in the first call
        '''
        try:
            return self.client_server_service.set_client_path(request=request)
        except (OSError, IOError) as e:
            return Response(
                status_code=1,
                message="Error setting client path to slaves from node coordinator",
                error=str(e)
            )
    def set_client_path(
        self,
        request: Request,
        sequence_events: list[dict[str, object]]
    ) -> None:
        '''
        Set the client path
        '''
        try:
            with self.master_coordinator_lock:
                list_acks: list = sequence_events[-1]["acks"]
            for server_id, slave_service in self.slaves.items():
                slave_service: DropBoxV1Service
                server_id: int
                if server_id == slave_service.get_server_id():
                    try:
                        response: Response = self.disptach_set_client_path(
                            request=request,
                            slave=slave_service,
                        )
                        response = obtain(response)
                        if response.status_code == 0:
                            with self.master_coordinator_lock:
                                list_acks.append(
                                    (slave_service.get_ip_service(),
                                    slave_service.get_port(),
                                    response)
                                )
                        else:
                            print(
                                f"Error setting client path for server\
                                    {server_id}, from node coordinator"
                                )
                    except (OSError, IOError) as e:
                        print(
                            f"Error setting client path for server {server_id},\
                                {e}, from node coordinator, general exception"
                            )
                return Response(
                    status_code=0,
                    message="Client path set to slaves from node coordinator",
                    error=None,
                    is_broadcasted=True
                )
        except (OSError, IOError) as e:
            return Response(
                status_code=1,
                message="Error setting client path to slaves from node coordinator",
                error=str(e)
            )
    def set_slaves(self) -> None:
        '''
        Get the list of slaves
        '''
        registry: UDPRegistryClient = \
        UDPRegistryClient(ip="158.227.125.64", port=50081)  # Discover the registry server
        print("Discovering services...", registry.list())
        discovered_services: (list[tuple] | int | Any) = discover('DROPBOXV1', registrar=registry)
        print("Discovered services", discovered_services)
        for service in discovered_services:
            try:
                conn: rpyc.Connection = rpyc.connect(
                    service[0],
                    service[1],
                    config={
                        'allow_pickle': True,
                        'allow_all_attrs': True,
                        'allow_public_attrs': True
                    },
                )
                service: DropBoxV1Service = conn.root
                self.slave_connections[service] = conn
                self.slaves[service.get_server_id()] = service
            except DiscoveryError as e:
                print(f"Error: {e}")
            except (OSError, IOError) as e:
                print(f"Error: {e}")
        self.broadcast_slaves()
        print("Slaves set", self.slaves)
    def get_slaves_health(self) -> (list[float]):
        '''
        Get the list of slaves health
        '''
    def get_slaves(self) -> (list[dict[int: DropBoxV1Service]]):
        '''
        Get the slaves
        '''
        return self.slaves
    @rpyc.exposed
    def broadcast_slaves(self) -> None:
        '''
        Broadcast the nodes in registry to slaves
        '''
        slaves_to_broadcast: list[tuple[str, int]] = []
        # Normalize dictionary, obtaining only the (server_id, server_port)
        for key in self.slave_connections:
            server_id: str = key.get_server_id()
            server_port: int = key.get_port()
            slaves_to_broadcast.append((server_id, server_port))

        for _, slave_service in self.slaves.items():
            election_service: IElection = obtain(slave_service.get_election_service())
            try:
                election_service.set_slaves_broadcasted(slaves_to_broadcast)
            except (OSError, IOError) as e:
                print(f"Error broadcasting slaves: {e}")
