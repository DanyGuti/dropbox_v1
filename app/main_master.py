'''
This module starts the master server
'''
import subprocess
from rpyc.utils.server import UDPRegistryClient
from rpyc.utils.server import ThreadedServer
from utils.server.helpers import SERVERS_IP
from utils.server.server_config import ServerConfig
from server.build.init_service import InitService
from server.build.factories.factory import FactoryServices

def start_registry_subprocessed() -> None:
    '''
    Install and start the registry with subprocess
    '''
    try:
        command: str = "pip install rpyc && rpyc_registry --port 50081 -l true"
        subprocess.Popen(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Non zero status check...{e}")
    except subprocess.SubprocessError as e:
        print(f"Subproccess calling has failed...{e}")

def main() -> None:
    '''
    Main function to start the master server
    '''
    # Start the registry server as a subprocess
    start_registry_subprocessed()
    InitService(factory=FactoryServices()).create_master_service(
        ServerConfig(
            auto_register=True,
            is_master=True,
            port=50082,
            registrar=UDPRegistryClient(
                "158.227.125.64",
                50081
            ),
            type=ThreadedServer,
            server_id=3
        )
    )

if __name__ == "__main__":
    main()
