import rpyc
import rpyc.core
import rpyc.core.protocol
from custom_req_res import Request, Response

@rpyc.service
class DropbBoxV1Service(rpyc.Service):
    def on_connect(self, conn: rpyc.Connection) -> None:
        # code that runs when a connection is created
        # (to init the service, if needed)
        print("Hello client!", conn)
        return

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        print("Goodbye client!", conn)
        return
    @rpyc.exposed
    def upload_chunk(self, request: Request, chunk: int, file_path: str, file_name: str) -> Response:
        print(request)
        print(chunk)
        return Response()
    @rpyc.exposed
    def file_creation(self, request: Request) -> Response:
        print(request)
        return Response()
    @rpyc.exposed
    def file_deletion(self, request: Request) -> Response:
        print(request)
        return Response()
    @rpyc.exposed
    def dir_creation(self, request: Request) -> Response: 
        print(request)
        return Response()
    @rpyc.exposed
    def dir_deletion(self, request: Request) -> Response:
        print(request)
        return Response()
    

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DropbBoxV1Service, port=18861)
    print(t)
    t.start()