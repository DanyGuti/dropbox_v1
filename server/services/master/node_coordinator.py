'''
Node coordinator module
'''
from typing import Any
from time import time
from rpyc.utils.server import UDPRegistryClient
from rpyc.utils.factory import discover
from server.imports.import_server_base import rpyc, Request, Response\
    , SERVERS_IP, SLAVE_SERVER_PORT
from server.services.slave.server_impl import DropbBoxV1Service
from server.services.master.task_processor import TaskProcessor

class NodeCoordinator(TaskProcessor):
    '''
    Load balancer class
    '''
    def __init__(self) -> None:
        super().__init__()
        self.slaves: dict[int: DropbBoxV1Service] = {}
        self.slave_connections: dict[tuple, rpyc.Connection] = {}
        self.slaves_health: list[float] = []
    def distribute_load_slaves(self, request: Request, chunk: int) -> (Response | Exception):
        '''
        Distribute the load
        '''
        try:
            return self.dispatch_req_slave(
                request,
                slave=(SERVERS_IP, SLAVE_SERVER_PORT),
                chunk=chunk,
            )
        except Exception as e:
            return e
    def set_client_path(self, cwd: str, user: str, sequence_events: list[dict[str, object]]) -> None:
        '''
        Set the client path
        '''
        try:
            for server_id, slave_service in self.slaves.items():
                slave_service: DropbBoxV1Service
                server_id: int
                if server_id == slave_service.get_server_id():
                    try:
                        response: Response = self.disptach_set_client_path(
                            cwd=cwd,
                            user=user,
                            slave=(slave_service.get_ip_service(), slave_service.get_port()),
                        )
                        if response.status_code == 0:
                            list_acks: list = sequence_events[-1]["acks"]
                            list_acks.append(server_id)
                            sequence_events.append({
                                "timestamp": time.time(),
                                "user": user,
                                "request": "set_client_path",
                                "acks": list_acks
                            })
                    except Exception as e:
                        print(f'Error: {e}')
                        print(f"Error setting client path for server {server_id}")
        except Exception as e:
            return e
    def set_slaves(self) -> None:
        '''
        Get the list of slaves
        '''
        registry: UDPRegistryClient = \
        UDPRegistryClient(ip=SERVERS_IP, port=50081)  # Discover the registry server
        discovered_services: (list[tuple] | int | Any) = \
        discover("DROPBOXV1", registrar=registry)
        for service in discovered_services:
            try:
                conn: rpyc.Connection = rpyc.connect(
                    service[0],
                    service[1]
                )
                service: DropbBoxV1Service = conn.root
                self.slave_connections[service] = conn
                self.slaves[service.get_server_id()] = service
            except Exception as e:
                print(f"Error: {e}")
    def get_slaves_health(self) -> (list[float]):
        '''
        Get the list of slaves health
        '''
    def get_slaves(self) -> (list[dict[int: DropbBoxV1Service]]):
        '''
        Get the slaves
        '''
        return self.slaves
