import queue
import rpyc
import threading

class Client():
    conn: rpyc.Connection = None
    def __init__(self) -> None:
        self.request = {}
        self.responseQueue = queue.Queue()
        self.lock = threading.Lock()
    def start_connection(self) -> None:
        try:
            self.conn = rpyc.connect("localhost", 18861)
            print(f"Connected to server: {self.conn}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
    def upload_chunk(self, chunk: bytes, file_path: str, file_name: str) -> None:
        try:
            print(f"Uploading chunk of size {len(chunk)} bytes...")
            response = self.conn.root.upload_chunk(self.request, chunk, file_path, file_name)
            with self.lock:  # Ensure thread-safe access to the queue
                self.responseQueue.put(response)
        except Exception as e:
            print(f"Failed to send chunk to server: {e}")

    def send_file_by_chunks(self, file_path: str, file_name: str) -> None:
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
    def send_req(self) -> dict:
        if self.conn is None:
            print("No active connection to the server!")
            return
        try:
            # Send request to the server (example method call)
            response = self.conn.root.get_answer()
            self.responseQueue.put(response)
            self.process_responses()
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
            print(f"Failed to send request: {e}")
    def handleError() -> dict:
        pass