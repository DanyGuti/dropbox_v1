'''
This file contains the interface for the task processor of the slave.
'''
from typing import Generator, Any
from server.imports.import_server_base import ABC\
    , abstractmethod, Response, Request

class ITaskProcessorSlave(ABC):
    '''
    Interface for the slave's task processor
    '''
    @abstractmethod
    def process_task_fms(
            self,
            request: Request,
            task_type: str
        ) -> Response:
        '''
        Process a task (delegation to FileManagementService)
        '''
    @abstractmethod
    def process_task_css(
            self,
            request: Request
        ) -> Response:
        '''
        Process a task (delegation to base service)
        '''
    @abstractmethod
    def append_task(
        self,
        request: Request,
        type_req: str,
        chunk: bytes
    ) -> None:
        '''
        Append a new request to the processor (FIFO)
        '''
    @abstractmethod
    def request_past_task(self, request: Request) -> Response:
        '''
        Exposed request, call the master to update own state
        '''
    @abstractmethod
    def process_tasks(self) -> Generator[Response, Any, Any]:
        '''
        Infinite hearing to record of requests
        '''
