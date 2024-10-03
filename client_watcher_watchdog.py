import time
import os
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

CWD = os.path.dirname(os.path.abspath(__file__))

class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        print(event)


event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, CWD, recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
finally:
    observer.stop()
    observer.join()