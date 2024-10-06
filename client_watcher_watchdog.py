import os
import re
import time
import threading

from client import Client
from custom_req_res import Request
from system_event_handler import SystemEventHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, \
    FileMovedEvent, FileModifiedEvent, FileDeletedEvent, \
    FileCreatedEvent, DirCreatedEvent, DirDeletedEvent

CWD: str = os.path.dirname(os.path.abspath(__file__))

# Grab the events from local system and send to server via rpyc (RPCs)
class ClientWatcher(Client, SystemEventHandler):
    '''
    ClientWatcher class to watch for system events
    and send them to the server
    Attributes:
        client: Client
        _dispatcher: list
        last_time_event: time
        accumulation_timeout: float
        lock: threading.Lock
    '''
    def __init__(self, client: Client) -> None:
        super().__init__()  # Initialize the parent class (Client)
        self.client: Client = client
        self._dispatcher: list = []
        self.last_event_time: time = time.time()  # Track the time of the last event
        self.accumulation_timeout: float = 0.2
        self.lock: threading.Lock = threading.Lock()
        # self.root_path_stack: list = re.split(r'(\/)', CWD)
        
    # Call the parent class
    def on_any_event(self, event: FileSystemEvent) -> None:
        '''
        Event handler for any file system event
        '''
        super().on_any_event(event)
        if not '__pycache__' in event.src_path:
            with self.lock:
                self._dispatcher.append(event)
    # Start watching with observer
    def start_watching(self) -> None:
        '''
        Start watching for file system events
        '''
        observer: Observer = Observer() # type: ignore
        observer.schedule(self, CWD, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.1)
                # Wait for batch processing
                if (time.time() - self.last_event_time) > self.accumulation_timeout and len(self._dispatcher) > 0:
                    self.parser()  # Batch processing
        finally:
            observer.stop()
            observer.join()
    def send_to_client(self, path: str, action: str, file: str, dst: str="", is_dir: bool=False) -> None:
        '''
        Send the request to the client
        '''
        self.client.request = Request(
            action=action,
            destination_path=dst,
            file_name=file,
            is_directory=is_dir,
            src_path=path
            )
        if action == 'file_created' or action == 'mv' or action == 'cp' or action == 'modified':
            self.client.send_file_by_chunks(dst, file) if action == 'mv' else self.client.send_file_by_chunks(path, file)
        else:
            self.client.send_req()
    def construct_curr_path(self, path_pattern: str) -> str:
        '''
        Construct the current path from the path pattern
        '''
        return re.split(r'(\/)', path_pattern)[-1]
        # At each event, join the stack string and
        # compare with the src_path
        # If the string is different:
            # New file can be the difference
                # When only the difference does not contain
                # any '/'
            # User has went back in directory
                # When the length is less of the src_path
                # than the stack curr_node
                    # Remove from the curr_node stack until
                    # the complete string is equal to src_path
            # User has went up in another directory
                # When the length of the src_path is greater
                # than the stack curr_node
                    # Add to the currStack the path to it
        
    def parser(self) -> None:
        '''
        Parse the events and send to the client
        '''
        accum_events: list = []
        with self.lock:
            print(self._dispatcher)
            while (len(self._dispatcher) > 0):
                curr_event: FileSystemEvent = self._dispatcher.pop(0)
                accum_events.append(curr_event)
            while(len(accum_events) > 0):
                event: FileSystemEvent = accum_events[0]
                if (len (accum_events) == 4) and not isinstance(event, (FileMovedEvent)):
                    file_event: FileSystemEvent = accum_events[1]
                    file_name: str = self.construct_curr_path(file_event.src_path)
                    accum_events.clear() # cp a file
                    print("cp a file")
                    self.send_to_client(event.src_path, 'cp', file_name)
                elif ((len (accum_events) == 3)
                        and ((str(event.event_type) == 'modified')
                            or (str(event.event_type) == 'created'))
                        and (isinstance(event, FileCreatedEvent))):
                    accum_events.clear()
                    file_name: str = self.construct_curr_path(event.src_path)
                    print("Nano and created a new file") # Nano and created file SAVING IT
                    self.send_to_client(event.src_path, 'file_created', file_name)
                elif isinstance(event, (FileMovedEvent)):
                    accum_events.clear() # mv a file
                    # file_name: str = self.construct_curr_path(event.src_path)
                    file_dest : list = re.split(r'(\/)', event.dest_path)
                    print("mv a file")
                    self.send_to_client(event.src_path, 'mv', file_dest[-1], event.dest_path)
                elif ((len(accum_events) == 1)
                        and (str(event.event_type) == 'modified')
                        and (isinstance(event, FileModifiedEvent))):
                    accum_events.clear() # touch (a file already created) or nano (in disk and exiting or overwriting the file saving and exiting) or head or echo or cp into a file that exists
                    file_name: str = self.construct_curr_path(event.src_path)
                    print(" touch (a file already created) or nano (in disk and exiting or overwriting the file saving and exiting) or head or echo")
                    self.send_to_client(event.src_path, 'modified', file_name)
                elif ((len(accum_events) == 2)
                        and (str(event.event_type) == 'deleted')
                        and not (event.is_directory)
                        and (isinstance(event, FileDeletedEvent))):
                    accum_events.clear() # Deleted a file
                    file_name: str = self.construct_curr_path(event.src_path)
                    print("Deleted a file")
                    self.send_to_client(event.src_path, 'rm', file_name)
                elif ((len(accum_events) == 2)
                        and (str(event.event_type) == 'created')
                        and not (event.is_directory)
                        and (isinstance(event, FileCreatedEvent))):
                    accum_events.clear()
                    file_name: str = self.construct_curr_path(event.src_path)
                    print("touch file")
                    self.send_to_client(event.src_path, 'touch', file_name)
                elif ((len(accum_events) == 2)
                        and (event.is_directory)
                        and (isinstance(event, DirCreatedEvent)
                            or (isinstance(event, DirDeletedEvent)))):
                    if event.event_type == 'created':
                        accum_events.clear() # Created a directory
                        file_name: str = self.construct_curr_path(event.src_path)
                        print("Created directory")
                        self.send_to_client(event.src_path, 'mkdir', file_name, "", True)
                    else:
                        accum_events.clear() # Deleted a directory
                        file_name: str = self.construct_curr_path(event.src_path)
                        print("Erased directory")
                        self.send_to_client(event.src_path, 'rmdir', file_name, "", True)

if __name__ == "__main__":
    client: Client = Client()
    client.start_connection()
    if client.conn:
        client_watcher: ClientWatcher = ClientWatcher(client=client)
        client_watcher.start_watching()