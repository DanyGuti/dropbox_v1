'''
Server side of the dropbox application
'''
from typing import Any
import time
import threading
from rpyc.utils.server import UDPRegistryClient
from rpyc.utils.factory import discover
from utils.server.helpers import SERVERS_IP

from server.imports.import_server_base import subprocess
from server.services.base.base_service import Service
from server.imports.import_server_base import rpyc, Request, Response, ThreadedServer
from server.interfaces.common.health_interface import IHealthService
from server.services.base.client_server_service import ClientServerService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.election_interface import IElection
from server.interfaces.common.dropbox_interface import IDropBoxServiceV1
from server.interfaces.local_fms_interface import IFileManagementService
from server.interfaces.init_interfaces.factory_interface import IFactoryService

@rpyc.service
class DropBoxV1Service(
    IDropBoxServiceV1,
    Service,
    rpyc.Service,
):
    '''
    DropBox service
    '''
    def __init__(
        self,
            client_service: IClientServerService,
            file_management_service: IFileManagementService,
            health_service: IHealthService,
            election_service: IElection,
            factory: IFactoryService,
            ip_service: str,
            port: int,
        ) -> None:
        super().__init__(health_service)
        self.client_service: IClientServerService = client_service
        self.file_management_service: IFileManagementService = file_management_service
        self.health_service: IHealthService = health_service
        self.election_service: IElection = election_service
        self.server_relative_path: str = client_service.get_server_relative_path()
        self.thread = None
        self.factory: IFactoryService = factory
        self.leader_ip: str = ""
        self.set_ip_service(ip_service)
        self.set_port(port)

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
    def start_bully_algorithm(
        self,
        message_election: str,
        nodes: list[tuple[str, int]],
        curr_node: int
    ) -> None:
        '''
        Propagate an election message
        '''
        responses: tuple[list[str], int] = self.election_service.send_election_message(
            message_election,
            nodes,
            curr_node
        )
        all_empty_from_nodes: bool = all("" == res for res in responses[0])
        if all_empty_from_nodes:
            self.election_service.elect_leader()
            self.promote_self_to_master()
        else:
            self.election_service.send_election_message("election", responses[1])
    @rpyc.exposed
    def set_client_path(self, request: Request) -> Response:
        response: Response = self.client_service.set_client_path(request)
        self.client_service.append_to_logs(request, response)
        return response
    @rpyc.exposed
    @ClientServerService.apply_set_client_dir_state_wrapper
    def upload_chunk(self, request: Request, chunk: int) -> Response:
        '''
        upload a chunk of a file to the server
        '''
        print(f"Uploading chunk of size {len(chunk)} bytes...")
        #Caso chunk vacio-- file by chunk empty
        self.server_relative_path: str = self.client_service.get_server_relative_path()
        response: Response = None
        if request.action in ['file_created', 'modified', 'touch', 'cp', 'created']:
            response =  self.file_management_service.write_chunk_no_mv(
                request.file_name,
                self.server_relative_path,
                chunk,
                request.action
            )
            self.client_service.append_to_logs(request, response)
            return response
        if request.action == 'mv':
            response = self.file_management_service.write_chunk_mv(
                self.client_service.get_server_relative_path(),
                request.destination_path,
                request.file_name,
                self.server_relative_path
            )
            self.client_service.append_to_logs(request, response)
            return response
        response = Response(error="ActionError", message="Error: ", status_code=3)
        self.client_service.append_to_logs(
            request,
            response
        )
        return response
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
    def promote_self_to_master(self) -> None:
        '''
        Promote self to master
        '''
        try:
            # Stop the past thread
            self.stop_thread()
            # Create the master service with the factory
            master_service = self.factory.create_master_service()
            # Set the server id
            master_service.set_server_id(self.get_server_id())
            # Set the IP service
            master_service.set_ip_service(self.get_ip_service())
            # Set the port
            master_service.set_port(self.get_port())
            # Create a new registry client to register the master(self and slaves)
            subprocess.run(["rpyc_registry", "--port", "50081", "-l", "true"], check=True)
            # Start the master service
            t: ThreadedServer = ThreadedServer(
                master_service,
                auto_register=True,
                port=master_service.get_port(),
                registrar=UDPRegistryClient(
                    SERVERS_IP,
                    50081
                ),
            )
            t.start()
            print("Promoted to master")
            return None
        except subprocess.CalledProcessError as error:
            print(f"Error in the promotion from slave to master subprocess {error}")
            return None
        except Exception as error:
            print(f"Error promoting slave to master has failed after bully algorithm: {error}")
            return None
    def set_thread(self, thread: ThreadedServer) -> None:
        '''
        Set the thread
        '''
        self.thread = thread
    def get_thread(self) -> ThreadedServer:
        '''
        Get the thread
        '''
        return self.thread
    def stop_thread(self) -> None:
        '''
        Stop the thread
        '''
        self.thread.stop()
        print("Thread has been stopped successfully")
    def send_heartbeat(self) -> None:
        '''
        Send a heartbeat
        '''
        while True:
            try:
                subprocess.run(["ping", "-c", "1", self.leader_ip], check=True)
                time.sleep(5)
            except subprocess.CalledProcessError as error:
                print(f"Error in the heartbeat subprocess {error}")
                self.start_bully_algorithm(
                    "election",
                    [(self.leader_ip, 50000), (SERVERS_IP, 50000)],
                    self.get_server_id()
                )
                break
            time.sleep(5)
    def set_leader_ip(self) -> None:
        '''
        Set the leader IP
        '''
        registry: UDPRegistryClient = \
                UDPRegistryClient(ip=SERVERS_IP, port=50081)  # Discover the registry server
        discovered_services: (list[tuple] | int | Any) = \
            discover("MASTERSERVER", registrar=registry)
        if not discovered_services:
            print("No master server found")
            return
        self.leader_ip = discovered_services[0][0]
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()
