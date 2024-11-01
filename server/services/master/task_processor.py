'''
Task Processor module
'''
from server.imports.import_server_base import Request, Response, rpyc
from server.interfaces.common.dropbox_interface import IDropBoxServiceV1

class TaskProcessor:
    '''
    Task Processor class
    '''
    _dispatcher: list[Request] = []
    def __init__(self) -> None:
        self._dispatcher = []
    def dispatch_req_slave(self, request: Request, slave: tuple, chunk: int) -> (Response | Exception):
        '''
        Dispatch the request to the slave
        '''
        try:
            conn: rpyc.Connection = rpyc.connect(
                slave[0],
                slave[1],
                config={"allow_public_attrs": True
            })
            if conn is None:
                print(f"No avaiable server implementation at port {slave[1]}")
                return
            service: IDropBoxServiceV1 = conn.root
        except ConnectionError as e:
            print(e)
            return e
        print(f"Connected to slave server: {slave[0], slave[1]}")
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
            conn.close()
            return response
        except ConnectionError as e:
            print(e)
            return e
    def disptach_set_client_path(self, cwd: str, slave: tuple) -> None:
        '''
        Dispatch the set client path to the slave
        '''
        try:
            conn: rpyc.Connection = rpyc.connect(
                slave[0],
                slave[1],
                config={"allow_public_attrs": True
            })
            if conn is None:
                print(f"No avaiable server implementation at port {slave[1]}")
                return
            service: IDropBoxServiceV1 = conn.root
        except ConnectionError as e:
            print(e)
            return e
        print(f"Connected to slave server: {slave[0], slave[1]}")
        service.set_client_path(cwd)
        conn.close()
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
        