'''
Client class to interact with the server
inherits from ClientWatcher
'''
import os
import queue
from typing import Optional
import threading
import rpyc
from rpyc.utils.registry import UDPRegistryClient
from rpyc.utils.factory import discover
from utils.custom_req_res import Request, Response
from utils.helpers import SERVERS_IP
from server.interfaces.dropbox_interface import IDropBoxServiceV1

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
        self.response_queue: queue.Queue[Response] = queue.Queue()
        self.lock: threading.Lock = threading.Lock()
    def start_connection(self, cwd: str) -> None:
        '''
        Start connection to the server (Service)
        '''
        try:
            # self.conn: rpyc.Connection = rpyc.connect(
            #     IP_ADDRESS_SERVER,
            #     50082,
            #     config={"allow_public_attrs": True}
            # )
            # self.service: IDropBoxServiceV1 = self.conn.root
            # talk_to_master = rpyc.connect(
            #     IP_ADDRESS_SERVER,
            #     50081,
            #     config={"allow_public_attrs": True}
            # ).root.talk_to_slave(self.request)
            # print(talk_to_master)
            # registry: (list[tuple]) = rpyc.discover("DROPBBOXV1")  # Discover the registry server
            registry = UDPRegistryClient(ip=SERVERS_IP, port=50081)  # Discover the registry server
            print(registry)
            discovered_services = discover("MASTERSERVER", registrar=registry)
            print(discovered_services)
            for service in discovered_services:
                self.conn: rpyc.Connection = rpyc.connect(
                    service[0],
                    service[1],
                    config={"allow_public_attrs": True
                })
            if self.conn is None:
                print("No available services found.")
                return
            self.service = self.conn.root
            print(f"Connected to server: {self.conn}")
            # self.service: IDropBoxServiceV1 = None
            # # registry = rpyc.connect("localhost", 18861)  # Default port for the registry server
            # for service in registry:
            #     self.conn: rpyc.Connection  = rpyc.connect(
            #         service[0],
            #         service[1],
            #         config={"allow_public_attrs": True
            #     })  # Store the connection
            #     self.service: IDropBoxServiceV1 = self.conn.root  # Get the root of the service
            #     print(f"Connected to server: {self.conn}")
            #     if self.service:
            #         print("Connected to the service successfully.")
            #         break  # Exit the loop if successfully connected
            # if self.service is None:
            #     print("No available services found.")
            #     return
            # Set the client path when the connection is established
            self.service.set_client_path(cwd)
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            self.conn.close()
        except (OSError) as e: # Acknowledge failure
            print(e)
            self.handle_error(e)
    def close_connection(self) -> None:
        '''
        Close connection to the server
        '''
        try:
            if self.conn is not None:
                self.conn.close()
                print("Connection to the server closed.")
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            self.conn.close()
        except (OSError) as e:
            print(f"An error occurred: {e}")
            self.conn.close()
    def upload_chunk(self, chunk: bytes) -> None:
        '''
        Upload a chunk of a file to the server
        '''
        try:
            print(f"Uploading chunk of size {len(chunk)} bytes...")
            response: Response = self.service.upload_chunk(self.request, chunk)
            with self.lock:  # Ensure thread-safe access to the queue
                self.response_queue.put(response)
                self.process_responses()
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            self.conn.close()
        except (OSError) as e: # Acknowledge failure
            self.handle_error(e)

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
                print(
                    f"File '{file_name}' is empty. \
                    Only creating the file on the server without sending data.")
                self.upload_chunk(b'')  # Create the file on the server without data
                return
            with open(file_path, 'rb') as file:
                chunk: bytes = file.read(chunk_size)
                while chunk:
                    threading.Thread(
                        target=self.upload_chunk,
                        args=(chunk,)
                    ).start()
                    chunk = file.read(chunk_size)
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            self.conn.close()
        except (OSError) as e: # Acknowledge failure
            self.handle_error(e)
    def send_req(self) -> Optional[Response]:
        '''
        Send a request to the server
        '''
        if self.conn is None:
            print("No active connection to the server!")
            return None
        if self.service is None:
            print("No active connection to the server!")
            return None
        try:
            # Send request to the server (example method call)
            request_action: str = self.request.action
            response: Optional[Response] = None
            match request_action:
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
                    self.response_queue.put(response)
                    self.process_responses()
            return response
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            self.conn.close()
            return None
        except (OSError) as e: # Acknowledge failure
            self.handle_error(e)
            return None
        ## rpyc.escribirDocumento():
    def process_responses(self) -> None:
        '''
        Process responses from the server
        '''
        try:  # Acknowledge success
            while not self.response_queue.empty():
                response: Response = self.response_queue.get()  # Wait for a response
                if response is None:
                    self.handle_error("Received a None response.")
                    self.response_queue.task_done()
                    continue
                # Check if the error attribute exists before accessing it
                if hasattr(response, 'error') and response.error is not None:
                    self.handle_error(response.error)
                    self.response_queue.task_done()
                    continue
                print(f"Response from server: {response}")
                self.response_queue.task_done()
        except (KeyboardInterrupt, SystemExit):
            print("Exiting...")
            self.conn.close()
        except (OSError) as e: # Acknowledge failure
            self.handle_error(e)
    def handle_error(self, error: Optional[Exception | str] = None) -> dict:
        '''
        Handle application errors
        '''
        if error:
            print(f"An error occurred: {error}")
            return {"error": str(error)}
        return {}
