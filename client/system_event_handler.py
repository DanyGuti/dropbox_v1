'''
This module contains the SystemEventHandler class.
'''
from client.imports.import_base import \
    FileSystemEventHandler, FileMovedEvent, FileModifiedEvent, \
        FileDeletedEvent, FileCreatedEvent, \
        DirCreatedEvent, DirDeletedEvent

class SystemEventHandler(FileSystemEventHandler):
    '''
    This class is used to handle file system events.
    It is a child class of FileSystemEventHandler
    '''
    def __init__(self):
        # self.last_directory = None
        # self.last_file = None
    # def on_any_event(self, event: FileSystemEvent) -> FileSystemEvent:
        '''
        Event handler for any file system event
        '''
        # Ignore __pycache__
        # if '__pycache__' in event.src_path:
#             return None # Ignore this event if __pycache__ is in the path
        # return event
    def on_modified(self, event: FileModifiedEvent):
        '''
        Handle the modification of a file
        '''
        # Ignore __pycache__
        # if '__pycache__' in event.src_path:
            # return # Ignore this event if __pycache__ is in the path
        return event
    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''
        Handle the creation of file or of directory
        '''
        # Ignore __pycache__
        # if '__pycache__' in event.src_path:
            # return None# Ignore this event if __pycache__ is in the path
        if isinstance(event, FileCreatedEvent, DirCreatedEvent):
            return event
        return None
    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''
        Handle the deletion of a file or a directory
        '''
        if isinstance(event, FileDeletedEvent, DirDeletedEvent):
            return event
        return None
        # Ignore __pycache__
        # if '__pycache__' in event:
            # return None# Ignore this event if __pycache__ is in the path
    def on_moved(self, event: FileMovedEvent):
        '''
        Handle the moving of a file
        '''
        if isinstance(event, FileMovedEvent):
            return event
        return None
        # Ignore __pycache__
        # if '__pycache__' in event:
            # return None# Ignore this event if __pycache__ is in the path
