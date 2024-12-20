'''
ClientWatcher class to watch for system events
child class of Client
'''

from client.imports.import_base import os, re, time, threading

from client.imports.import_base import Observer, FileSystemEvent, \
    FileMovedEvent, FileModifiedEvent, FileDeletedEvent, FileClosedEvent, \
    FileCreatedEvent, DirCreatedEvent, DirDeletedEvent, DirModifiedEvent

from client.client_impl import Client
from client.system_event_handler import SystemEventHandler
from client.imports.import_base import Request, Task

swp_file_pattern = r"^.*\.swp$"
# Get the directory of the current file
current_dir: str = os.path.dirname(os.path.abspath(__file__))
# Move two directories up
CWD: str = os.path.normpath(os.path.join(current_dir, ".."))
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
    def __init__(self, client_instance: Client) -> None:
        super().__init__(user=client_instance.user) # Initialize the parent class with the user
        self.client: Client = client_instance
        self._dispatcher: list = []
        self.last_event_time: time = time.time()  # Track the time of the last event
        self.accumulation_timeout: float = 0.25
        self.lock: threading.Lock = threading.Lock()
        # self.root_path_stack: list = re.split(r'(\/)', CWD)
    def on_modified(self, event: FileModifiedEvent):
        '''
        Event handler for any file system event
        '''
        if not isinstance(event, FileModifiedEvent):
            return None
        super().on_modified(event)
        # if not '__pycache__' in event.src_path:
        with self.lock:
            self._dispatcher.append(event)
    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''
        Event handler for creating a file or directory
        '''
        event_handler: (FileCreatedEvent | DirCreatedEvent) = super().on_created(event)
        if isinstance(event_handler, DirCreatedEvent):
            # Handle a file creation
            # if not '__pycache__' in event.src_path:
            with self.lock:
                self._dispatcher.append(event)
        elif isinstance(event_handler, FileCreatedEvent):
            # Handle a dir creation
            with self.lock:
                self._dispatcher.append(event)
    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        event_handler: (FileDeletedEvent | DirDeletedEvent) = super().on_deleted(event)
        if isinstance(event_handler, DirDeletedEvent):
            # Handle a file creation
            # if not '__pycache__' in event.src_path:
            with self.lock:
                self._dispatcher.append(event)
        elif isinstance(event_handler, FileDeletedEvent):
            # Handle a dir creation
            # if not '__pycache__' in event.src_path:
            with self.lock:
                self._dispatcher.append(event)
    def on_moved(self, event):
        super().on_moved(event)
        # if not '__pycache__' in event.src_path:
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
                if (time.time() - self.last_event_time) > self.accumulation_timeout and\
                    len(self._dispatcher) > 0:
                    self.parser()  # Batch processing
        finally:
            observer.stop()
            observer.join()
    def send_to_client(
        self,
        path: str,
        action: str,
        file: str,
        dst: str="",
        is_dir: bool=False
        ) -> None:
        '''
        Send the request to the client
        '''
        self.client.request = Request(
            action=action,
            destination_path=dst,
            file_name=file,
            is_directory=is_dir,
            task=Task(
                id_client=1,
                user=self.user,
                id_task=self.client.invocation_id
            ),
            time_of_request=time.time(),
            src_path=path
        )
        self.client.invocation_id += 1
        # Append the current request to the list of requests
        self.client.requests.append(self.client.request)
        if action in ['file_created', 'mv', 'cp', 'modified']:
            if action == 'mv':
                self.client.send_file_by_chunks(dst, file)
            else:
                self.client.send_file_by_chunks(path, file)
        else:
            self.client.send_req()
    def construct_curr_path(self, path_pattern: str) -> str:
        '''
        Construct the current path from the path pattern
        '''
        return re.split(r'(\/)', path_pattern)[-1]
    def parser(self) -> None:
        '''
        Parse the events and send to the client
        '''
        accum_events: list = []
        with self.lock:
            while len(self._dispatcher) > 0:
                curr_event: FileSystemEvent = self._dispatcher.pop(0)
                accum_events.append(curr_event)
            if any (re.match(swp_file_pattern, e.src_path) for e in accum_events):
                accum_events = list(
                    filter(
                        lambda e : not re.match(swp_file_pattern, e.src_path),
                        accum_events
                    ))
            print(accum_events)
            while len(accum_events) > 0:
                if all(isinstance(e, (DirModifiedEvent)) for e in accum_events):
                    accum_events.clear()
                    return
                event: FileSystemEvent = accum_events[0]
                if not any(isinstance(e, (FileMovedEvent, FileClosedEvent))\
                    for e in accum_events):
                    accum_events.clear()
                    file_name : str = self.construct_curr_path(event.src_path)
                if any((isinstance(e, (DirCreatedEvent)) for e in accum_events)):
                    self.send_to_client(event.src_path, 'mkdir', file_name, "", True)
                elif any((isinstance(e, (DirDeletedEvent)) for e in accum_events)):
                    self.send_to_client(event.src_path, 'rmdir', file_name, "", True)
                elif any((isinstance(e, (FileMovedEvent)) for e in accum_events)):
                    moved_event = next((e for e in accum_events if isinstance(e
                                    , FileMovedEvent
                                )), None)
                    accum_events.clear()
                    file_dest : list = re.split(r'(\/)', moved_event.dest_path)
                    self.send_to_client(
                        moved_event.src_path,
                        'mv',
                        file_dest[-1],
                        moved_event.dest_path
                    )
                elif any((isinstance(e, (FileDeletedEvent)) for e in accum_events)):
                    self.send_to_client(event.src_path, 'rm', file_name)
                elif (len(accum_events == 1) and isinstance(event, FileCreatedEvent)):
                    self.send_to_client(event.src_path, 'touch', file_name)
                else:
                    if any((isinstance(e, (FileClosedEvent)) for e in accum_events)):
                        file_event: FileSystemEvent = accum_events[1]
                        file_name: str = self.construct_curr_path(file_event.src_path)
                        accum_events.clear()
                        self.send_to_client(event.src_path, 'cp', file_name)
                    else:
                        accum_events.clear()
                        self.send_to_client(event.src_path, 'modified', file_name)
