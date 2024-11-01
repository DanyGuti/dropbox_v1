'''
Node coordinator module
'''
import rpyc
from server.services.slave.server_impl import DropbBoxV1Service
from server.services.master.task_processor import TaskProcessor
from utils.server.helpers import SERVERS_IP, SLAVE_SERVER_PORT
from utils.custom_req_res import Request, Response

class NodeCoordinator(TaskProcessor):
    '''
    Load balancer class
    '''
    def __init__(self) -> None:
        super().__init__()
        self.slaves: list[DropbBoxV1Service] = []
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
    def set_client_path(self, cwd: str) -> None:
        '''
        Set the client path
        '''
        try:
            return self.disptach_set_client_path(
                cwd=cwd,
                slave=(SERVERS_IP, SLAVE_SERVER_PORT),
            )
        except Exception as e:
            return e
    def get_slaves(self) -> (list[DropbBoxV1Service]):
        '''
        Get the list of slaves
        '''
    def get_slaves_health(self) -> (list[float]):
        '''
        Get the list of slaves health
        '''
    def set_slaves(self, slaves: list[DropbBoxV1Service]) -> None:
        '''
        Set the list of slaves
        '''
