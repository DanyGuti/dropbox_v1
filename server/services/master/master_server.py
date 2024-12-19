'''
This module represents the
master server (coordinator)
will have one replica server
'''

from server.imports.import_server_base import Callable, rpyc\
    , Request, Response, time

from server.services.base.base_service import Service
from server.services.master.node_coordinator import NodeCoordinator
from server.interfaces.common.dropbox_interface import IDropBoxServiceV1
from server.services.base.client_server_service import ClientServerService
from server.interfaces.common.health_interface import IHealthService
from server.interfaces.election_interface import IElection
from server.interfaces.init_interfaces.master_service_interface import IMasterServerService

IP_ADDRESS_SLAVE_SERVER_SERVICE: str = "158.227.126.106"


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
            health_service: IHealthService,
        ) -> None:
        super().__init__(health_service=health_service)
        self.node_coordinator: NodeCoordinator = coordinator
        self.sequence_events = []
        self.set_server_id(1)
        self.server_thread: rpyc.ThreadedServer = None
        self.update_replicas_timer: int = 40
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
        ) -> (Response | Exception):
            try:
                with self.node_coordinator.master_coordinator_lock:
                    self.sequence_events.append({
                        "timestamp": time.time(),
                        "user": req_client.task.user,
                        "request": req_client,
                        "acks": []
                    })
                result: (Response | Exception) = self.node_coordinator.distribute_load_slaves(
                    req_client,
                    sequence_events=self.sequence_events
                )
                print(result)
                if isinstance(result, Exception):
                    raise result
                return result
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Error distributing load: {e}")
                return e
        return wrapper
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
        ) -> (Response | Exception):
            try:
                with self.node_coordinator.master_coordinator_lock:
                    self.sequence_events.append({
                        "timestamp": time.time(),
                        "user": req_client.task.user,
                        "request": req_client,
                        "acks": []
                    })
                result: (Response | Exception) = self.node_coordinator.self_apply_request(
                    req_client,
                    sequence_events=self.sequence_events
                )
                print(result)
                if isinstance(result, Exception):
                    raise result
                return method(self, req_client)
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Error distributing load: {e}")
                return e
        return wrapper
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
        # cwd_client : str = request.src_path
        # req_client : str = request.task.user
        self.sequence_events.append({
            "timestamp": time.time(),
            "user": request.task.user,
            "request": "set_client_path",
            "acks": []
        })
        self.node_coordinator.apply_self_set_client_path(request, self.sequence_events)
        return self.node_coordinator.set_client_path(request, self.sequence_events)
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    @apply_modification_master_wrapper
    @apply_slave_distribution_wrapper
    def upload_chunk(self, request: Request) -> (Response | Exception):
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
    @rpyc.exposed
    def get_election_service(self) -> IElection:
        pass
    def set_leader_ip(self) -> None:
        pass
    @rpyc.exposed
    def get_leader_ip(self) -> str:
        pass
    @rpyc.exposed
    def periodically_update_slaves(self) -> None:
        '''
        Update the slaves after failing.
        '''
        while True:
            # For every ack not received from a slave
            # call the method to update the slave from its service
            with self.node_coordinator.master_coordinator_lock:
                for event in self.sequence_events:
                    acknowledgements: list[tuple[int, Response]] = event["acks"]
                    if len(acknowledgements) < len(self.node_coordinator.slaves):
                        # Get where the serviceId is missing from the acknowledgements
                        # And four services
                        # {1: Service1, 2: Service2, 3: Service3}
                        missing_elements: list[tuple[int, int]] = list(
                            filter(
                                lambda x, acks=acknowledgements: x not in {
                                    (ack[0], ack[1]) for ack in acks
                                },
                                self.node_coordinator.slaves.keys())
                        )
                        for missing_service_ip, missing_service_port in missing_elements:
                            try:
                                conn: rpyc.Connection = rpyc.connect(
                                    missing_service_ip,
                                    missing_service_port,
                                    config={
                                        'allow_pickle': True,
                                        'allow_all_attrs': True,
                                        'allow_public_attrs': True
                                    },
                                )
                                service = conn.root
                                response: Response = service.task_processor.update_after_failure(
                                    event["request"]
                                )
                                if response.status_code == 0:
                                    acknowledgements.append(
                                        (missing_service_ip, missing_service_port, response)
                                    )
                                else:
                                    print(f"Error when trying to update join of slave: \
                                        {response.message}")
                            except ConnectionError as e:
                                print(f"Error when trying to update join of slave: {e}")
            time.sleep(self.update_replicas_timer)
