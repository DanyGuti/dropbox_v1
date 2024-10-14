'''
Server side of the dropbox application
'''
from typing import Callable
import shutil
import os
import sys

import rpyc
import rpyc.core
import rpyc.core.protocol
from custom_req_res import Response
from custom_req_res import Request

# /users/desktop/dropboxv1 past state
# /users/desktop/dropboxv1/dir1 curr state set to that path
# getting the difference between the two
# if client changes, append the new path to the server path
# (just the change from the past state to the current state)
# setting the past state to the current state
# server mounted state dir: dropbox_genial_loli_app
def apply_set_client_dir_state_wrapper(
    method: Callable[['DropbBoxV1Service',
    Request], (bool | Exception)]
) -> (bool | Exception):
    '''
    Wrapper to set the client directory state
    '''
    def wrapper(
        self: 'DropbBoxV1Service',
        *args: tuple[Request],
        **kwargs: dict[str, any]
    ) -> (bool | Exception):
        req_client: Request = args[0]
        result = self.set_client_state_path(req_client)
        if result is False:
            print(f"Failed to set client state path: {result}")
            return result  # Exit early if setting client path fails
        return method(self, *args, **kwargs)
    return wrapper

def upload_chunk (chunk: int, relative_path: str) -> (Exception | None):
    '''
    Upload a chunk of a file to the server
    '''
    try:
        with open(relative_path, "ab") as arc:
            arc.write(chunk)
        #print(chunk)
        print("Chunk succesfully chunked, Chunky.\nregards, C. Hunk")
        return None
    except (OSError, IOError) as e:
        print(f"Error: {e}")
        return e

def create_empty_file (relative_path: str) -> (Exception | None):
    '''
    Create an empty file in the given path
    '''
    try:
        open(relative_path, 'x', encoding='utf-8')
        return None
    except FileExistsError:
        print(f"Something went wrong: the file {relative_path} already exists in the given path.")
        return FileExistsError
    except (OSError, IOError) as e:
        print(f"Error: {e}")
        return e

def delete_file (relative_path: str) -> (Exception | None):
    '''
    Delete a file in the given path
    '''
    print("from delete_file:", relative_path)
    try:
        os.remove(relative_path)
        return None
    except FileNotFoundError:
        print(f"Something went wrong: file {relative_path} not found.")
        return FileNotFoundError
    except (OSError, IOError) as e:
        print(f"Error: {e}")
        return e

def create_directory (relative_path: str) -> (Exception | None):
    '''
    Create a directory in the given path
    '''
    try:
        os.mkdir(relative_path)
        return None
    except (OSError, IOError) as e:
        print(f"Error: {e}")
        return e

def delete_directory (relative_path: str) -> (Exception | None):
    '''
    Delete a directory in the given path
    '''
    try:
        os.rmdir(relative_path)
        return None
    except FileNotFoundError:
        print(f"Something went wrong: the directory {relative_path} not found.")
        return FileNotFoundError
    except OSError:
        print(f"Something went wrong: the directory {relative_path} is not empty.")
        return OSError

def get_diff_path(path: str, client_path: str) -> str:
    '''
    Get the difference between the two paths
    '''
    return os.path.relpath(path, client_path)
def normalize_path(path: str) -> str:
    '''
    Normalize the path
    '''
    return os.path.normpath(path)


@rpyc.service
class DropbBoxV1Service(rpyc.Service):
    '''
    DropBox service
    '''
    def __init__(self) -> None:
        self.server_relative_path: str = os.getcwd()
        self.client_path: str = ""
        current_id_available: int = 1 # id for the current client connected

    def on_connect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is established
        with a client
        '''
        # code that runs when a connection is created
        # (to init the service, if needed)
        print("Hello client!", conn)

    def on_disconnect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is closed
        with a client
        '''
        print("Goodbye client!", conn)
    def set_client_state_path(self, request: Request) -> (bool | Exception):
        '''
        Set the client state path
        '''
        try:
            if request.src_path in [self.client_path, ""]:
                return False
            # Getting the difference between the two paths
            diff_path: str = get_diff_path(request.src_path, self.client_path)
            # Update server_relative_path and normalize it
            new_relative_path: str = os.path.join(self.server_relative_path, diff_path)
            # Remove the '..' from the path, if any
            self.server_relative_path: str = normalize_path(new_relative_path)
            self.client_path: str = request.src_path

            # Check if the updated path exists
            print(f"Checking existence of path: {self.server_relative_path}")
            if request.action not in ['file_created', 'modified', 'touch', 'cp', 'created', 'mv']:
                if not os.path.exists(self.server_relative_path):
                    print(self.server_relative_path)
                    print(f"Something went wrong: the parent directory\
                        {os.path.dirname(self.server_relative_path)}\
                    not found.")
                    return False
            return True
        except (OSError, IOError) as e:
            print("ERRORRRR")
            print(f"Error: {e}")
            return e

    @rpyc.exposed
    def set_client_path(self, cwd: str) -> str:
        '''
        Set the client path when the connection is established
        '''
        self.client_path = cwd
        print(f"Client path set to: {self.client_path}")
        return self.client_path

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def upload_chunk(self, request: Request, chunk: int) -> Response:
        '''
        upload a chunk of a file to the server
        '''
        print(f"Uploading chunk of size {len(chunk)} bytes...")
        #Caso chunk vacio-- file by chunk empty
        if request.action in ['file_created', 'modified', 'touch', 'cp', 'created']:
            try:
                # delete_file(self.server_relative_path)
                with open(self.server_relative_path, "wb") as arc:
                    arc.write(chunk)
                return Response(
                    message=request.file_name \
                    + " succesfully modified file!",
                    status_code=0
                )
            except (OSError, IOError) as e:
                print(f"Error: {e}")
                return Response(
                    error=e,
                    message=f'Error in action: {request.action}, error: {e}',
                    status_code=13
                )

        elif request.action == "mv":
            dst_path: str = request.destination_path
            print(dst_path)
            print(self.server_relative_path)
            try:
                print(f"destination_path: {dst_path}")
                src_path: str = self.server_relative_path
                # Get difference from path to delete, then change to the path to overwrite
                diff_path: str = get_diff_path(dst_path, self.client_path)
                new_relative_path: str = os.path.join(self.server_relative_path, diff_path)
                # normalize
                self.server_relative_path: str = normalize_path(new_relative_path)
                # Handle the case when the file does not exist (create empty file)
                if not os.path.exists(self.server_relative_path):
                    with open(self.server_relative_path, "wb") as empty_file:
                        empty_file.write(b'')
                shutil.move(src_path, self.server_relative_path)
                return Response(
                    message=request.file_name +\
                    " succesfully moved file!",
                    status_code=0
                )
            except (OSError, IOError) as e:
                print(f"Error: {e}")
                return Response(error=e, message="Error: ", status_code=13)
        else:
            return Response(error="ActionError", message="Error: ", status_code=3)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def file_creation(self, request: Request) -> Response: #touch en principio hecho
        '''
        Create a file on the server
        '''
        try:
            open(self.server_relative_path, 'x', encoding='utf-8')
            print(request)
            return Response(message=request.file_name + " succesfully touched!")
        except FileExistsError:
            print(f"Something went wrong: the file {request.file_name}\
                already exists in the given path."
            )
            return Response(error="FileExistsError", message="Error: ", status_code=6)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message=f'Error en action: {e}', status_code=13)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def file_deletion(self, request: Request) -> Response: #rm
        '''
        Delete a file on the server
        '''
        try:
            os.remove(self.server_relative_path)
            print(request)
            return Response(message=request.file_name + " succesfully removed!", status_code=0)
        except FileNotFoundError:
            print(f"Something went wrong: file {request.file_name} not found.")
            return Response(error="FileNotFoundError",
                            message="Something went wrong: file " +\
                                {request.file_name} + " not found.",
                            status_code=5
                        )
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message="Error: ", status_code=13)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def dir_creation(self, request: Request) -> Response: #mkdir
        '''
        Create a directory on the server
        '''
        try:
            os.mkdir(self.server_relative_path)
            return Response(message = request.file_name + " succesfully cretated directory!")

        except FileExistsError:
            print(f"Something went wrong: the directory {request.file_name}\
                already exists in the given path."
            )
            return Response(error = "FileExistsError", message = "Error: ", status_code = 6)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message="Error: ", status_code=13)

    @rpyc.exposed
    @apply_set_client_dir_state_wrapper
    def dir_deletion(self, request: Request) -> Response: #rmdir
        '''
        Delete a directory on the server
        '''
        try:
            os.rmdir(self.server_relative_path)
            return Response(message = request.file_name + " succesfully deleted directory!")

        except FileNotFoundError:
            print(f"Something went wrong: the directory {request.file_name} not found.")
            return Response(error = "FileNotFoundError", message = "Error: ", status_code = 5)
        except (OSError, IOError) as e:
            print(f"Something went wrong: the directory {request.file_name} is not empty.")
            return Response(error=e, message="Error: ", status_code=13)

if __name__ == "__main__":
    try:
        DIR_NAME: str = "dropbox_genial_loli_app"
        # Check if the directory exists
        if not os.path.exists(DIR_NAME):
            # If it doesn't exist, create it
            os.mkdir(DIR_NAME)
            print(f"Directory '{DIR_NAME}' created.")
        # Change to the directory
        os.chdir(DIR_NAME)
        print(f"Changed to directory: {os.getcwd()}")
        from rpyc.utils.server import ThreadedServer
        t = ThreadedServer(DropbBoxV1Service, port=50080, auto_register=True)
        print(t)
        t.start()
    except (OSError, IOError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
    finally:
        print("Exiting...")
        sys.exit(0)
