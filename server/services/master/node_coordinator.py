'''
Node coordinator module
'''
from typing import Any
from rpyc.utils.classic import obtain
from rpyc.utils.server import UDPRegistryClient
from rpyc.utils.factory import discover
from rpyc.utils.factory import DiscoveryError
from server.imports.import_server_base import rpyc, Request, Response,\
    SERVERS_IP
from server.services.slave.server_impl import DropBoxV1Service
from server.services.master.task_distributor import TaskDistributor
#CAmbios hechos 4
from server.interfaces.local_fms_interface import IFileManagementService


class NodeCoordinator(TaskDistributor):
    '''
    Load balancer class
    '''
    def __init__(self, file_management_service: IFileManagementService) -> None:
        super().__init__()
        self.slaves: dict[int: DropBoxV1Service] = {}
        self.slave_connections: dict[DropBoxV1Service, rpyc.Connection] = {}
        self.slaves_health: list[float] = []
        self.file_management_service: IFileManagementService = file_management_service

    def self_apply_request (
        self,
        request: Request,
        sequence_events: list[dict[str, object]]
    ) -> (Response | Exception):
        task_action: str = request.action
        try:
            response: Response
            match task_action:
                case 'mv' | 'file_created' | 'cp' | 'modified':
                    response = self.file_management_service.upload_chunk(request)
                case 'touch':
                    response = self.file_management_service.file_creation(request)
                case 'rm':
                    response = self.file_management_service.file_deletion(request)
                case 'mkdir':
                    response = self.file_management_service.dir_creation(request)
                case 'rmdir':
                    response = self.file_management_service.dir_deletion(request)
            return response
        except Exception as e:
            print(e)
            return Response(
                status_code=1,
                message="Error dispatching request, TaskDistributor",
                error=str(e)
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
                            list_acks.append((slave_service.get_ip_service(), response))
                        else:
                            print(
                                f"Error distributing load to server \
                                    {server_id}, from node coordinator"
                            )
                    except Exception as e:
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
        except Exception as e:
            return Response(
                status_code=1,
                message="Error distributing load to slaves from node coordinator",
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
                            list_acks.append((slave_service.get_ip_service(), response))
                        else:
                            print(
                                f"Error setting client path for server\
                                    {server_id}, from node coordinator"
                                )
                    except Exception as e:
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
        except Exception as e:
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
        UDPRegistryClient(ip="158.227.126.125", port=50081)  # Discover the registry server
        print(registry)
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
            except Exception as e:
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
        print(self.slave_connections)
        for key in self.slave_connections.keys():
            server_id: str = key.get_server_id()
            server_port: int = key.get_port()
            slaves_to_broadcast.append((server_id, server_port))

        for _, slave_service in self.slaves.items():
            slave_service: DropBoxV1Service
            ## Set the (ip, port) of the slaves to all registred nodes
            print(slave_service.election_service)
            try:
                slave_service.election_service.set_slaves_broadcasted(slaves_to_broadcast)
            except Exception as e:
                print(f"Error broadcasting slaves from 'broadcast_slaves': {e}")
