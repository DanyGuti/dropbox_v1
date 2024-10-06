from abc import ABC, abstractmethod
from custom_req_res import Request, Response
import rpyc

class IDropBoxServiceV1(ABC):
    @abstractmethod
    def on_connect(self, conn: rpyc.Connection) -> None:
        pass
    @abstractmethod
    def on_disconnect(self, conn: rpyc.Connection) -> None:
        pass
    @abstractmethod
    def upload_chunk(self, request: Request, chunk: int, file_path: str, file_name: str) -> Response:
        pass
    @abstractmethod
    def file_creation(self, request: Request) -> Response:
        pass
    @abstractmethod
    def file_deletion(self, request: Request) -> Response:
        pass
    @abstractmethod
    def dir_creation(self, request: Request) -> Response:
        pass
    @abstractmethod
    def dir_deletion(self, request: Request) -> Response:
        pass