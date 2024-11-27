'''
Custom dataclasses
for task objects
'''
from dataclasses import dataclass
import time

@dataclass
class Task:
    '''
    Task object to be sent to the server
    '''
    id_client: int = 0
    id_server: int = 0
    time_reception: time = 0
    user: str = ""
    id_task: int = 0
