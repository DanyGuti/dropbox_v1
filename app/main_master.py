'''
This module starts the master server
'''

from rpyc.utils.server import UDPRegistryClient
from rpyc.utils.server import ThreadedServer
from utils.server.helpers import SERVERS_IP
from utils.server.server_config import ServerConfig
from server.build.init_service import InitService
from server.build.factories.factory import FactoryServices

def main() -> None:
    '''
    Main function to start the master server
    '''
    InitService(factory=FactoryServices()).create_master_service(
        ServerConfig(
            auto_register=True,
            is_master=True,
            port=50082,
            registrar=UDPRegistryClient(
                SERVERS_IP,
                50081
            ),
            type=ThreadedServer
        )
    )

if __name__ == "__main__":
    main()
