'''
Custom dataclasses
for request and response objects
'''
from dataclasses import dataclass, field
from typing import Optional
import time

from utils.task import Task

@dataclass
class Response:
    '''
    Response object to be sent back to the client
    '''
    error: Optional[str] = None
    message: str = ""
    is_broadcasted: bool = False
    is_finished: bool = False
    retry: bool = False
    time_sent: time = 0
    status_code: int = 0

@dataclass
class Request(Task):
    '''
    Request object to be sent to the server
    '''
    action: str = ""
    destination_path: str = ""
    file_name: str = ""
    is_directory: bool = ""
    task: Task = field(default_factory=Task)
    time_of_request: time = 0
    src_path: str = ""
