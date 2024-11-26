'''
This module contains the SystemEventHandler class.

'''
import re
from watchdog.events import FileSystemEvent, FileSystemEventHandler
SWP_REGEX_FILE_PATTERN = r"^.*\.swp$"

class SystemEventHandler(FileSystemEventHandler):
    '''
    This class is used to handle file system events.
    It is a child class of FileSystemEventHandler
    '''
    def on_any_event(self, event: FileSystemEvent) -> FileSystemEvent:
        '''
        Event handler for any file system event
        '''
        # Ignore __pycache__
        if '__pycache__' in event.src_path or re.match(SWP_REGEX_FILE_PATTERN, event.src_path):
            return # Ignore this event if __pycache__ is in the path
        print(event)
        return event
