'''
Custom dataclasses
for request and response objects
'''
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Response:
    '''
    Response object to be sent back to the client
    '''
    data: dict = field(default_factory=dict)
    error: Optional[str] = None
    message: str = ""
    status_code: int = 0

@dataclass
class Request:
    '''
    Request object to be sent to the server
    '''
    action: str = ""
    destination_path: str = ""
    file_name: str = ""
    is_directory: bool = ""
    src_path: str = ""
