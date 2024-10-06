import queue
import rpyc
import threading
from typing import Optional
from custom_req_res import Request, Response
from server import DropbBoxV1Service

class Client():
    conn: Optional[rpyc.Connection] = None
    service: Optional[DropbBoxV1Service] = None
    def __init__(self) -> None:
        self.request: Request = Request()
        self.responseQueue: queue.Queue[Response] = queue.Queue()
        self.lock: threading.Lock = threading.Lock()
    def start_connection(self) -> None:
        try:
            self.conn: rpyc.Connection = rpyc.connect("localhost", 18861)
            self.service: DropbBoxV1Service = self.conn.root  # Assign the service to the type
            print(f"Connected to server: {self.conn}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
    def upload_chunk(self, chunk: bytes, file_path: str, file_name: str) -> None:
        try:
            print(f"Uploading chunk of size {len(chunk)} bytes...")
            response = self.service.upload_chunk(self.request, chunk, file_path, file_name)
            with self.lock:  # Ensure thread-safe access to the queue
                self.responseQueue.put(response)
                self.process_responses()
        except Exception as e:
            print(f"Failed to send chunk to server: {e}")

    def send_file_by_chunks(self, file_path: str, file_name: str) -> None:
        # Before sending to the server, compare with current file's state
        chunk_size: int = 1024 * 1024  # 1MB chunks
        try:
            with open(file_path, 'rb') as file:
                chunk: bytes = file.read(chunk_size)
                while(chunk):
                    threading.Thread(
                        target=self.upload_chunk,
                        args=(chunk, file_path, file_name)
                    ).start()
                    chunk = file.read(chunk_size)
        except Exception as e:
            print(f"Failed to send file to server by chunks: {e}")
    def send_req(self) -> Optional[Response]:
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
                    response = self.service.file_creation(self.request)
                case 'rm':
                    response = self.service.file_deletion(self.request)
                case 'mkdir':
                    response = self.service.dir_creation(self.request)
                case 'rmdir':
                    response = self.service.dir_deletion(self.request)
            if response is not None:
                with self.lock:
                    self.responseQueue.put(response)
                    self.process_responses()
            return response
        except Exception as e:
            print(f"Failed to send request: {e}")
        ## rpyc.escribirDocumento():
    def process_responses(self) -> None:
        try:  # Acknowledge success
            while(not self.responseQueue.empty()):
                response = self.responseQueue.get()  # Wait for a response
                print(f"Response from server: {response}")
                self.responseQueue.task_done()
        except Exception as e: # Acknowledge failure
            self.handleError()
            print(f"Failed to process response: {e}")
    def handleError(self) -> dict:
        pass