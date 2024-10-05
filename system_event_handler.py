from watchdog.events import FileSystemEvent, FileSystemEventHandler

class SystemEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        # Ignore __pycache__
        if '__pycache__' in event.src_path:
            return  # Ignore this event if __pycache__ is in the path
        return event