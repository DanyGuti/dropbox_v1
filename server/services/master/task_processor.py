'''
Task Processor module
'''
from server.imports.import_server_base import Request, Response
from server.services.slave.server_impl import DropBoxV1Service

class TaskProcessor:
    '''
    Task Processor class
    '''
    _dispatcher: list[Request] = []
    def __init__(self) -> None:
        self._dispatcher = []
    def dispatch_req_slave(
        self,
        request: Request,
        slave: DropBoxV1Service,
        chunk: int
    ) -> (Response | Exception):
        '''
        Dispatch the request to the slave
        '''
        try:
            service: DropBoxV1Service = slave
        except ConnectionError as e:
            print(e)
            return Response(status_code=1,\
                message="Error dispatching request, TaskProcessor", error=str(e)
            )
        print(f"Connected to slave server: {service.get_server_id(), service.get_ip_service()}")
        task_action: str = request.action
        try:
            response: Response
            match task_action:
                case 'mv' | 'file_created' | 'cp' | 'modified':
                    response = service.upload_chunk(request, chunk)
                case 'touch':
                    response = service.file_creation(request)
                case 'rm':
                    response = service.file_deletion(request)
                case 'mkdir':
                    response = service.dir_creation(request)
                case 'rmdir':
                    response = service.dir_deletion(request)
            return response
        except ConnectionError as e:
            print(e)
            return Response(
                status_code=1,
                message="Error dispatching request, TaskProcessor",
                error=str(e)
            )
    def disptach_set_client_path(self, cwd: str, user: str, slave: DropBoxV1Service) -> Response:
        '''
        Dispatch the set client path to the slave
        '''
        try:
            service: DropBoxV1Service = slave
            print(f"Connected to slave server: {slave.get_server_id(), slave.get_ip_service()}")
            response: Response = service.set_client_path(cwd, user)
            print(f"Response: {response}, from task processor")
            return response
        except ConnectionError as e:
            print(e)
            return Response(
                status_code=1,
                message="Error dispatching request, set_client_path, TaskProcessor",
                error=str(e)
            )
    def process_dispatcher(self, request: Request) -> (Response | Exception):
        '''
        Process the dispatcher (from response of the slave and broadcast results)
        '''
    def get_dispatcher(self) -> (list[Request]):
        '''
        Get the dispatcher
        '''
    def add_req_dispatcher(self, request: Request) -> None:
        '''
        Add request to the dispatcher
        '''
    def remove_req_dispatcher(self, request: Request) -> None:
        '''
        Remove request from the dispatcher
        '''
    def clear_dispatcher(self) -> None:
        '''
        Clear the dispatcher
        '''
        