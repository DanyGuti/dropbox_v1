import os
import queue
import rpyc
import threading
from typing import Optional
from custom_req_res import Request, Response
from dropbox_interface import IDropBoxServiceV1

class Client():
    '''
    Client class to interact with the server
    
    Attributes:
        conn: rpyc.Connection
        service: DropbBoxV1Service
        request: Request
        responseQueue: queue.Queue[Response]
        lock: threading.Lock
    '''
    def __init__(self) -> None:
        self.conn: Optional[rpyc.Connection] = None
        self.service: Optional[IDropBoxServiceV1] = None
        self.request: Request = Request()
        self.responseQueue: queue.Queue[Response] = queue.Queue()
        self.lock: threading.Lock = threading.Lock()
    def start_connection(self) -> None:
        '''
        Start connection to the server (Service)
        '''
        try:
            self.conn: rpyc.Connection = rpyc.connect("localhost", 18861)
            self.service: IDropBoxServiceV1 = self.conn.root  # Assign the service to the type
            print(f"Connected to server: {self.conn}")
        except Exception as e:
            self.handleError(f"Failed to send chunk to server: {e}")
    def upload_chunk(self, chunk: bytes, file_path: str, file_name: str) -> None:
        '''
        Upload a chunk of a file to the server
        '''
        try:
            print(f"Uploading chunk of size {len(chunk)} bytes...")
            response = self.service.upload_chunk(self.request, chunk, file_path, file_name)
            with self.lock:  # Ensure thread-safe access to the queue
                self.responseQueue.put(response)
                self.process_responses()
        except Exception as e:
            self.handleError(e)

    def send_file_by_chunks(self, file_path: str, file_name: str) -> None:
        '''
        Send a file to the server in chunks
        '''
        # Before sending to the server, compare with current file's state
        chunk_size: int = 1024 * 1024  # 1MB chunks
        try:
            # Check if the file is empty
            if os.path.getsize(file_path) == 0:
                self.request.action = 'touch'
                print(f"File '{file_name}' is empty. Only creating the file on the server without sending data.")
                self.upload_chunk(b'', file_path, file_name)  # Create the file on the server without data
                return
            with open(file_path, 'rb') as file:
                chunk: bytes = file.read(chunk_size)
                while(chunk):
                    threading.Thread(
                        target=self.upload_chunk,
                        args=(chunk, file_path, file_name)
                    ).start()
                    chunk = file.read(chunk_size)
        except Exception as e:
            self.handleError(e)
    def send_req(self) -> Optional[Response]:
        '''
        Send a request to the server
        '''
        if self.conn is None:
            print("No active connection to the server!")
            return
        if self.service is None:
            print("No active connection to the server!")
            return
        try:
            # Send request to the server (example method call)
            requestAction: str = self.request.action
            response: Optional[Response] = None
            match requestAction:
                case 'touch':
                    response: Response = self.service.file_creation(self.request)
                case 'rm':
                    response: Response = self.service.file_deletion(self.request)
                case 'mkdir':
                    response: Response = self.service.dir_creation(self.request)
                case 'rmdir':
                    response: Response = self.service.dir_deletion(self.request)
            if response is not None:
                with self.lock:
                    self.responseQueue.put(response)
                    self.process_responses()
            return response
        except Exception as e:
            self.handleError(e)
        ## rpyc.escribirDocumento():
    def process_responses(self) -> None:
        '''
        Process responses from the server
        '''
        try:  # Acknowledge success
            while(not self.responseQueue.empty()):
                response: Response = self.responseQueue.get()  # Wait for a response
                if response is None:
                    self.handleError("Received a None response.")
                    self.responseQueue.task_done()
                    continue
                # Check if the error attribute exists before accessing it
                if hasattr(response, 'error') and response.error is not None:
                    self.handleError(response.error)
                    self.responseQueue.task_done()
                    continue
                print(f"Response from server: {response}")
                self.responseQueue.task_done()
        except Exception as e: # Acknowledge failure
            self.handleError(e)
    def handleError(self, error: Optional[Exception | str] = None) -> dict:
        '''
        Handle application errors
        '''
        if error:
            print(f"An error occurred: {error}")
            return {"error": str(error)}
        return {}