import os
import re
import time

from client import Client
from system_event_handler import SystemEventHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, \
    FileMovedEvent, FileModifiedEvent, FileDeletedEvent, \
    FileCreatedEvent, DirCreatedEvent, DirDeletedEvent

CWD: str = os.path.dirname(os.path.abspath(__file__))

# Grab the events from local system and send to server via rpyc (RPCs)
class ClientWatcher(Client, SystemEventHandler):
    def __init__(self, client: Client) -> None:
        super().__init__()  # Initialize the parent class (Client)
        self.client: Client = client
        self._dispatcher: list = []
        self.last_event_time: time = time.time()  # Track the time of the last event
        self.accumulation_timeout: float = 0.2
        # self.root_path_stack: list = re.split(r'(\/)', CWD)
        
    # Call the parent class
    def on_any_event(self, event: FileSystemEvent) -> None:
        super().on_any_event(event)
        if not '__pycache__' in event.src_path:
            self._dispatcher.append(event)
    # Start watching with observer
    def start_watching(self) -> None:
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
        self.client.requestResponse = {
            'src_path' : path,
            'action' : action,
            'file_name' : file,
            'destination_path' : dst,
            'is_directory': is_dir
        }
        self.client.sendReq()
    def construct_curr_path(self, path_pattern: str) -> str:
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
        accum_events: list = []
        print(self._dispatcher)
        while (len(self._dispatcher) > 0):
            curr_event: FileSystemEvent = self._dispatcher.pop(0)
            accum_events.append(curr_event)
        while(len(accum_events) > 0):
            event: FileSystemEvent = accum_events[0]
            if (len (accum_events) == 4):
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
                self.send_to_client(event.src_path, 'nano', file_name)
                print("Nano and created a new file") # Nano and created file SAVING IT
            elif isinstance(event, (FileMovedEvent)):
                accum_events.clear() # mv a file
                file_name: str = self.construct_curr_path(event.src_path)
                file_dest : list = re.split(r'(\/)', event.dest_path)
                self.send_to_client(event.src_path, 'mv', file_name, file_dest[-1])
                print("mv a file")
                pass
            elif ((len(accum_events) == 1)
                    and (str(event.event_type) == 'modified')
                    and (isinstance(event, FileModifiedEvent))):
                accum_events.clear() # touch (a file already created) or nano (in disk and exiting or overwriting the file saving and exiting) or head or echo
                file_name: str = self.construct_curr_path(event.src_path)
                self.send_to_client(event.src_path, 'modified', file_name)
                print(" touch (a file already created) or nano (in disk and exiting or overwriting the file saving and exiting) or head or echo")
                pass
            elif ((len(accum_events) == 2)
                    and (str(event.event_type) == 'deleted')
                    and not (event.is_directory)
                    and (isinstance(event, FileDeletedEvent))):
                accum_events.clear() # Deleted a file
                file_name: str = self.construct_curr_path(event.src_path)
                self.send_to_client(event.src_path, 'rm', file_name)
                print("Deleted a file")
                pass
            elif ((len(accum_events) == 2)
                    and (str(event.event_type) == 'created')
                    and not (event.is_directory)
                    and (isinstance(event, FileCreatedEvent))):
                accum_events.clear()
                file_name: str = self.construct_curr_path(event.src_path)
                self.send_to_client(event.src_path, 'touch', file_name)
                print("touch file")
                pass
            elif ((len(accum_events) == 2)
                    and (event.is_directory)
                    and (isinstance(event, DirCreatedEvent)
                        or (isinstance(event, DirDeletedEvent)))):
                if event.event_type == 'created':
                    print("Created directory")
                    accum_events.clear() # Created a directory
                    file_name: str = self.construct_curr_path(event.src_path)
                    self.send_to_client(event.src_path, 'mkdir', file_name)
                else:
                    accum_events.clear() # Deleted a directory
                    print("Erased directory")
                    file_name: str = self.construct_curr_path(event.src_path)
                    self.send_to_client(event.src_path, 'rmdir', file_name)

if __name__ == "__main__":
    client: Client = Client()
    client.startConnection()
    if client.conn:
        client_watcher: ClientWatcher = ClientWatcher(client=client)
        client_watcher.start_watching()