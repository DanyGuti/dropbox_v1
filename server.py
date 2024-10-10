import rpyc
import rpyc.core
import rpyc.core.protocol
from custom_req_res import Response
from custom_req_res import Request

import os

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
        
        #Caso chunk vacio-- file by chunk empty
        if chunk == b'': 
            try:
                if (file_path == ""):
                    open(file_name, "x")
                else:
                    open(file_path + '/' + file_name, "x")
                print(request)
                return Response(message = file_name + " succesfully touched!")
            
            except FileExistsError:
                print(f"Something went wrong: the file {file_name} already exists in the given path.")
                return Response(error = "FileExistsError", message = "Error: ", status_code = -2)
            except Exception as e:
                print(f"Error: {e}")
                return Response(error = e, message = "Error: ", status_code = -1)
    
        else:
            try:
                if (file_path== ""):
                    with open(file_name, "wb") as arc:
                        arc.write(chunk)
                else:
                    with open(file_path + '/' + file_name, 'wb') as arc:
                        arc.write(chunk)
                    
                print(request)
                print(chunk)
                print(f"Chunk succesfully chunked, chunk.\nregards, C. Hunk")

            except Exception as e:
                print(f"Error: {e}")
                return Response(error = e, message = "Error: ", status_code = -1)
            
        return Response()
    
    @rpyc.exposed
    def file_creation(self, request: Request) -> Response: #touch en principio hecho

        try:
            if (request.src_path == ""):
                open(request.file_name, "x")
            else:
                open(request.src_path + '/' + request.file_name, "x")
            print(request)
            return Response(message = request.file_name + " succesfully touched!")
        except FileExistsError:
            print(f"Something went wrong: the file {request.file_name} already exists in the given path.")
            return Response(error = "FileExistsError", message = "Error: ", status_code = -2)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = "Error: ", status_code = -1)
        
    @rpyc.exposed
    def file_deletion(self, request: Request) -> Response: #rm
        
        try:
            if (request.src_path == ""):
                os.remove(request.file_name, "x")
            else:
                os.remove(request.src_path + '/' + request.file_name, "x")

            print(request)
            return Response(message = request.file_name + " succesfully removed!")
        
        except FileNotFoundError:
            print(f"Something went wrong: file {request.file_name} not found.")
            return Response(error = "FileNotFoundError", message = "Something went wrong: file " + {request.file_name} + " not found.", status_code = -2)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = "Error: ", status_code = -1)
        
    @rpyc.exposed
    def dir_creation(self, request: Request) -> Response: #mkdir

        try:
            if (request.src_path == ""):
                os.mkdir(request.file_name, "x")
            else:
                os.mkdir(request.src_path + '/' + request.file_name, "x")
            return Response(message = request.file_name + " succesfully touched!")
        
        except FileExistsError:
            print(f"Something went wrong: the directory {request.file_name} already exists in the given path.")
            return Response(error = "FileExistsError", message = "Error: ", status_code = -2)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = "Error: ", status_code = -1)
    @rpyc.exposed
    def dir_deletion(self, request: Request) -> Response: #rmdir
        
        try:
            if (request.src_path == ""):
                os.rmdir(request.file_name, "x")
            else:
                os.rmdir(request.src_path + '/' + request.file_name, "x")
            return Response(message = request.file_name + " succesfully touched!")
        
        except FileNotFoundError:
            print(f"Something went wrong: the directory {request.file_name} not found.")
            return Response(error = "FileNotFoundError", message = "Error: ", status_code = -2)
        except OSError:
            print(f"Something went wrong: the directory {request.file_name} is not empty.")
            return Response(error = "OSError", message = "Error: ", status_code = -3)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = "Error: ", status_code = -1)
    

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DropbBoxV1Service, port=18861)
    print(t)
    t.start()