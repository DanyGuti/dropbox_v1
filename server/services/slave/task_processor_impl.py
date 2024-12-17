'''
This file contains the implementation of the task processor used
to lock or make the updates in the slave
'''

from typing import Generator, Any
from server.interfaces.task_processor_interface import ITaskProcessorSlave
from server.interfaces.init_interfaces.client_service_interface import IClientServerService
from server.interfaces.local_fms_interface import IFileManagementService
from server.imports.import_server_base import Request, Response, rpyc, threading, time

class TaskProcessorSlave(
        ITaskProcessorSlave,
    ):
    '''
    Implementation of the slave Task Processor
    '''
    queue_processor: dict[str, list[Request]]
    # {"fms": [Req1, Req2]}, {"css": [Req1, Req2]}
    def __init__(
        self,
        client_server_service: IClientServerService,
        file_management_service: IFileManagementService,
    ):
        self.file_management_service: IFileManagementService = file_management_service
        self.client_server_service: IClientServerService = client_server_service
        self.queue_processor: dict[str, list[Request]] = {
            "fms": [],
            "css": []
        }
        self.lock: threading.Lock = threading.Lock()
    def process_task_fms(
            self,
            request: Request,
            task_type: str
        ) -> Response:
        '''
        Process a task (delegation to FileManagementService)
        '''
        response: Response = None
        match task_type:
            case "upload_chunk_no_mv":
                response = self.file_management_service.write_chunk_no_mv(
                    request.file_name,
                    self.client_server_service.get_server_relative_path(),
                    request.chunks,
                    request.action
                )
            case "upload_chunk_mv":
                response = self.file_management_service.write_chunk_mv(
                    self.client_server_service.get_client_path(),
                    request.destination_path,
                    request.file_name,
                    self.client_server_service.get_server_relative_path()
                )
            case "touch_file":
                response = self.file_management_service.file_creation(
                    request.file_name,
                    self.client_server_service.get_server_relative_path()
                )
            case "delete_file":
                response = self.file_management_service.file_deletion(
                    self.client_server_service.get_server_relative_path(),
                    request.file_name
                )
            case "dir_creation":
                response = self.file_management_service.dir_creation(
                    request.file_name,
                    self.client_server_service.get_server_relative_path()
                )
            case "dir_deletion":
                response = self.file_management_service.dir_deletion(
                    self.client_server_service.get_server_relative_path(),
                    request.file_name
                )
            case _:
                response = Response(
                    error="ActionError",
                    message="Error: ",
                    status_code=3,
                    time_sent=time.time(),
                    id_response=request.task.id_task
                )
        return response
    def process_task_css(
            self,
            request: Request
        ) -> Response:
        '''
        Process a task (delegation to base service)
        '''
        response: Response = self.client_server_service.set_client_path(request)
        return response
    def append_task(self, request: Request, type_req: str) -> None:
        '''
        Append the task to the task processor (FIFO)
        '''
        with self.lock:
            service_operations: dict[int, list[tuple[int, Response]]] =\
                self.client_server_service.get_operations_log()
            incoming_task_id_req: int = request.task.id_task

            list_invocations: list[tuple[int, Response]] =\
            service_operations.get(request.task.id_client, [])

            if len(list_invocations) == 0:
                self.queue_processor[type_req].append(request)
            else:
                last_invocation: tuple[int, Response] = list_invocations[-1]
                if incoming_task_id_req > last_invocation[0]:
                    self.request_past_task(request)
                else:
                    self.queue_processor[type_req].append(request)
    @rpyc.exposed
    def request_past_task(self, request: Request) -> Response:
        '''
        Request the log of operations to the leader
        '''
        # Sequence of events Data structure:
        # self.sequence_events.append({
        #     "timestamp": time.time(),
        #     "user": req_client.task.user,
        #     "request": req_client,
        #     "acks": []
        # })
        pass
    def process_tasks(self) -> Generator[Response, Any, Any]:
        '''
        Process the tasks infinitely until failure
        '''
        while True:
            request_to_task_fms: str = "fms"
            request_to_task_css: str = "css"
            response: Response = None
            client_service_list: list[Request] =\
                self.queue_processor.get(request_to_task_css, [])
            fms_service_list: list[Request] =\
                self.queue_processor.get(request_to_task_fms, [])
            if len(client_service_list) > 0 or len(fms_service_list) > 0:
                with self.lock:
                    min_request: tuple[int, str] = (10000, "")
                    for i, _ in enumerate(client_service_list):
                        if client_service_list[i].task.id_task < min_request[0]:
                            min_request = (client_service_list[i].task.id_task, "css")

                    for i, _ in enumerate(fms_service_list):
                        if fms_service_list[i].task.id_task < min_request[0]:
                            min_request = (fms_service_list[i].task.id_task, "fms")
                    # Delegate to the file_management_system
                    if min_request[1] == "fms":
                        min_curr_request: Request = fms_service_list[0]
                        min_curr_request_action: str = min_curr_request.action
                        if min_curr_request.action in\
                            ['file_created', 'modified', 'touch', 'cp', 'created']:
                            response = self.process_task_fms(min_curr_request, "upload_chunk_no_mv")
                        elif min_curr_request.action == 'mv':
                            response = self.process_task_fms(min_curr_request, "upload_chunk_mv")
                        else:
                            match min_curr_request_action:
                                case 'touch':
                                    response = self.process_task_fms(
                                        min_curr_request,
                                        "touch_file"
                                    )
                                case 'rm':
                                    response = self.process_task_fms(
                                        min_curr_request,
                                        "delete_file"
                                    )
                                case 'mkdir':
                                    response = self.process_task_fms(
                                        min_curr_request,
                                        "dir_creation"
                                    )
                                case 'rmdir':
                                    response = self.process_task_fms(
                                        min_curr_request,
                                        "dir_deletion"
                                    )
                        fms_service_list.pop(0)
                        self.queue_processor["fms"] = fms_service_list
                        response.id_response = min_curr_request.task.id_task
                        self.client_server_service.append_to_logs(min_curr_request, response)
                    # Delegate to the client_server_service
                    else:
                        min_curr_request: Request = client_service_list[0]
                        response = self.process_task_css(min_curr_request)
                        response.id_response = min_curr_request.task.id_task
                        self.client_server_service.append_to_logs(min_curr_request, response)
                        client_service_list.pop(0)
                        self.queue_processor["css"] = client_service_list
            yield response
