'''
Custom Server RPYC configuration
'''
from dataclasses import dataclass
from typing import Optional
from rpyc.utils.server import ThreadedServer
from rpyc.utils.server import ForkingServer
from rpyc.utils.server import UDPRegistryClient

@dataclass
class ServerConfig:
    '''
    Server configuration params
    '''
    auto_register: bool = True
    is_master: bool = False
    port: int = 50082
    registrar: Optional[UDPRegistryClient] = None
    server_ip: str = "localhost"
    service: Optional[UDPRegistryClient] = None
    type: Optional[ForkingServer | ThreadedServer] = None
