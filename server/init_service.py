'''
This is a class to implement for the i_initService.
'''
import os
import sys

from rpyc.utils.server import ThreadedServer
from rpyc.utils.server import ForkingServer

from utils.server_config import ServerConfig

from server.interfaces.i_init_service_interface import IInitService
from server.node_coordinator import NodeCoordinator
from server.master_server import MasterServerService
from server.server_impl import DropbBoxV1Service
DIR_NAME: str = "dropbox_genial_loli_app"

class InitService(IInitService):
    '''
    Init service class
    '''
    def create_service(self, config: ServerConfig) -> None:
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
        finally:
            print("Exiting...")
            sys.exit(0)
    def create_slave_service(self, config: ServerConfig) -> None:
        '''
        Create the slave service
        '''
        try:
            server_impl: DropbBoxV1Service = DropbBoxV1Service(
                client_service=None,
                health_service=None
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
        finally:
            print("Exiting...")
            sys.exit(0)
    def start_server(
            self,
            service: (MasterServerService | DropbBoxV1Service),
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
            t.start()
            return t
        t: ThreadedServer = ThreadedServer(
            service=service,
            auto_register=config.auto_register,
            port=config.port,
            registrar=config.registrar
        )
        t.start()
        return t
