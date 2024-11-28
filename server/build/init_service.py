'''
This is a class to implement for the i_initService.
'''
from server.imports.import_server_base import os, sys, ForkingServer, ThreadedServer
from server.imports.import_server_base import ServerConfig

from server.interfaces.common.health_interface import IHealthService
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.election_interface import IElection
from server.interfaces.local_fms_interface import IFileManagementService
from server.services.master.master_server import MasterServerService
from server.services.master.node_coordinator import NodeCoordinator
from server.services.slave.server_impl import DropBoxV1Service
from server.interfaces.init_interfaces.factory_interface import IFactoryService
DIR_NAME: str = "dropbox_genial_loli_app"

class InitService():
    '''
    Init service class
    '''
    def __init__(self, factory: IFactoryService) -> None:
        self.factory: IFactoryService = factory
    def create_service(self, config: ServerConfig) -> None:
        '''
        Create the server config
        '''
        if config.is_master:
            self.create_master_service(config)
        else:
            self.create_slave_service(config)
    def create_master_service(self, config: ServerConfig) -> None:
        '''
        Create the master service
        '''
        try:
            node_coordinator: NodeCoordinator = NodeCoordinator()
            master_service: MasterServerService = MasterServerService(
                coordinator=node_coordinator,
                health_service=None
            )
            self.start_server(master_service, config)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)
    def create_slave_service(self, config: ServerConfig) -> None:
        '''
        Create the slave service
        '''
        try:
            client_service: IClientServerService = self.factory.create_client_service()
            file_management_service: IFileManagementService = \
                self.factory.create_file_management_service()
            election_service: IElection = self.factory.create_election_service()
            health_service: IHealthService  = self.factory.create_health_service()
            server_impl: DropBoxV1Service = DropBoxV1Service(
                client_service=client_service,
                file_management_service=file_management_service,
                health_service=health_service,
                election_service=election_service,
                factory=self.factory
            )
            # Check if the directory exists
            if not os.path.exists(DIR_NAME):
                # If it doesn't exist, create it
                os.mkdir(DIR_NAME)
                print(f"Directory '{DIR_NAME}' created.")
            # Change to the directory
            os.chdir(DIR_NAME)
            print(f"Changed to directory: {os.getcwd()}")
            self.start_server(server_impl, config)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)
    def start_server(
            self,
            service: (MasterServerService | DropBoxV1Service),
            config: ServerConfig
        ) -> (ForkingServer | ThreadedServer):
        '''
        Start the server
        '''
        if config.type == ForkingServer:
            t: ForkingServer = ForkingServer(
                service=service,
                auto_register=config.auto_register,
                port=config.port,
                registrar=config.registrar
            )
            service.set_thread(t.start())
            return t
        t: ThreadedServer = ThreadedServer(
            service=service,
            auto_register=config.auto_register,
            port=config.port,
            registrar=config.registrar
        )
        print(f"Starting server on port {config.port}")
        if not isinstance(service, MasterServerService):
            service.set_leader_ip()
        service.set_thread(t.start())
        print(f"Server started on port, after {config.port}")
        return t
