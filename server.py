import rpyc
import rpyc.core
import rpyc.core.protocol
from custom_req_res import Response
from custom_req_res import Request

import os

# Revisar un mv de un file a otro file que no existe

# /users/desktop/dropboxv1 past state 
# /users/desktop/dropboxv1/dir1 curr state set to that path
# getting the difference between the two
# if client changes, append the new path to the server path
# (just the change from the past state to the current state)
# setting the past state to the current state
# server mounted state dir: dropbox_genial_loli_app
def apply_set_client_dir_state_wrapper(method: callable) -> callable:
    def wrapper(self, *args: tuple, **kwargs: dict[str, any]) -> callable:
        req_client: Request = args[0]
        self.set_client_state_path(req_client)
        return method(self, *args, **kwargs)
    return wrapper

def upload_chunk (chunk: int, relative_path: str) -> (Exception | None):
    try:
        with open(relative_path, "ab") as arc:
            arc.write(chunk)
        #print(chunk)
        print(f"Chunk succesfully chunked, Chunky.\nregards, C. Hunk")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return e

def create_empty_file (relative_path: str) -> (Exception | None):
    try:
        open(relative_path, 'x')
        return None
    except FileExistsError:
        print(f"Something went wrong: the file {relative_path} already exists in the given path.")
        return FileExistsError
    except Exception as e:
        print(f"Error: {e}")
        return e

def delete_file (relative_path: str) -> (Exception | None):
    print("from delete_file:", relative_path)
    try:
        os.remove(relative_path)
        return None
    except FileNotFoundError:
        print(f"Something went wrong: file {relative_path} not found.")
        return FileNotFoundError
    except Exception as e:
        print(f"Error: {e}")
        return e

def create_directory (relative_path: str) -> (Exception | None):
    try:
        os.mkdir(relative_path)
        return None
    except Exception as e:
        print(f"Error: {e}")
        return e

def delete_directory (relative_path: str) -> (Exception | None):
    try:
        os.rmdir(relative_path)
        return None
    except FileNotFoundError:
        print(f"Something went wrong: the directory {relative_path} not found.")
        return FileNotFoundError
    except OSError:
        print(f"Something went wrong: the directory {relative_path} is not empty.")
        return OSError
    except Exception as e:
        print(f"Error: {e}")
        return e

@rpyc.service
class DropbBoxV1Service(rpyc.Service):
    def __init__(self) -> None:
        self.server_relative_path: str = os.getcwd()
        self.client_path: str = ""
        current_id_available: int = 1

    def on_connect(self, conn: rpyc.Connection) -> None:
        # code that runs when a connection is created
        # (to init the service, if needed)
        print("Hello client!", conn)
        return

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        # close the client
        
        print("Goodbye client!", conn)
        return
    
    def set_client_state_path(self, request: Request) -> (bool | Exception):
        def getDiffPath(path: str) -> str:
            return os.path.relpath(path, self.client_path)
        def normalizePath(path: str) -> str:
            return os.path.normpath(path)
        try:
            if (request.src_path == self.client_path or request.src_path == ""):
                return False
            # Getting the difference between the two paths
            diff_path: str = getDiffPath(request.src_path)
            # Update server_relative_path and normalize it
            new_relative_path: str = os.path.join(self.server_relative_path, diff_path)
            # Remove the '..' from the path, if any
            self.server_relative_path: str = normalizePath(new_relative_path)
            self.client_path: str = request.src_path

            # Case of mv a file
            if request.destination_path != "":
                delete_file(self.server_relative_path)
                # Get difference from path to delete, then change to the path to overwrite
                diff_path: str = getDiffPath(request.destination_path)
                new_relative_path: str = os.path.join(self.server_relative_path, diff_path)
                # normalize
                self.server_relative_path: str = normalizePath(new_relative_path)
            # Check if the updated path exists
            if not os.path.exists(self.server_relative_path):
                print(f"Something went wrong: the directory {self.server_relative_path} not found.")
                return False
            
            return True
        except Exception as e:
            print(f"Error: {e}")
            return e

    @rpyc.exposed
    def set_client_path(self, cwd: str) -> str:
        self.client_path = cwd
        return self.client_path

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def upload_chunk(self, request: Request, chunk: int) -> Response:
        #Caso chunk vacio-- file by chunk empty
        if filter(lambda x: x == ('file_created' or 'modified' or 'touch' or 'cp' or 'created'), request.src_path) != []:
            try:
                delete_file(self.server_relative_path)
                with open(self.server_relative_path, "wb") as arc:
                    arc.write(chunk)
                return Response(message = request.file_name + " succesfully modified file!", status_code=0)
            # except FileExistsError:
            #     print(f"Something went wrong: the file {request.file_name} already exists in the given path.")
            #     return Response(error = "FileExistsError", message = "Error: ", status_code = -2)
            except Exception as e:
                print(f"Error: {e}")
                return Response(error = e, message = f'Error in action: {request.action}, error: {e}', status_code = 13)

            #print(self.server_relative_path)
            #create_empty_file(self.server_relative_path)
        elif request.action == "mv":
            print(request.destination_path)
            try:
                with open(self.server_relative_path, "wb") as arc:
                    arc.write(chunk)
                print(request)
                print(chunk)
                print(f"Chunk succesfully chunked, chunk.\nregards, C. Hunk")
                return Response(message = request.file_name + " succesfully modified file!", status_code=0)
            except Exception as e:
                print(f"Error: {e}")
                return Response(error = e, message = "Error: ", status_code = 13)
        else:
            return Response(error = "ActionError", message = "Error: ", status_code = 3)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def file_creation(self, request: Request) -> Response: #touch en principio hecho
        try:
            open(self.server_relative_path, 'x')
            print(request)
            return Response(message = request.file_name + " succesfully touched!")
        except FileExistsError:
            print(f"Something went wrong: the file {request.file_name} already exists in the given path.")
            return Response(error = "FileExistsError", message = "Error: ", status_code = 6)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = f'Error en action: {e}', status_code = 13)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def file_deletion(self, request: Request) -> Response: #rm
        try:
            os.remove(self.server_relative_path)
            print(request)
            return Response(message = request.file_name + " succesfully removed!", status_code=0)
        except FileNotFoundError:
            print(f"Something went wrong: file {request.file_name} not found.")
            return Response(error = "FileNotFoundError", message = "Something went wrong: file " + {request.file_name} + " not found.", status_code = 5)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = "Error: ", status_code = 13)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def dir_creation(self, request: Request) -> Response: #mkdir
        try:
            os.mkdir(self.server_relative_path)
            return Response(message = request.file_name + " succesfully cretated directory!")

        except FileExistsError:
            print(f"Something went wrong: the directory {request.file_name} already exists in the given path.")
            return Response(error = "FileExistsError", message = "Error: ", status_code = 6)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = "Error: ", status_code = 13)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def dir_deletion(self, request: Request) -> Response: #rmdir
        try:
            os.rmdir(self.server_relative_path)
            return Response(message = request.file_name + " succesfully deleted directory!")

        except FileNotFoundError:
            print(f"Something went wrong: the directory {request.file_name} not found.")
            return Response(error = "FileNotFoundError", message = "Error: ", status_code = 5)
        except OSError:
            print(f"Something went wrong: the directory {request.file_name} is not empty.")
            return Response(error = "OSError", message = "Error: ", status_code = 13)
        except Exception as e:
            print(f"Error: {e}")
            return Response(error = e, message = "Error: ", status_code = 13)

if __name__ == "__main__":
    try:
        dir_name = "dropbox_genial_loli_app"
        # Check if the directory exists
        if not os.path.exists(dir_name):
            # If it doesn't exist, create it
            os.mkdir(dir_name)
            print(f"Directory '{dir_name}' created.")
        # Change to the directory
        os.chdir(dir_name)
        print(f"Changed to directory: {os.getcwd()}")
        from rpyc.utils.server import ThreadedServer
        t = ThreadedServer(DropbBoxV1Service, port=50080)
        print(t)
        t.start()
    except Exception as e:
        print(f"Error: {e}")