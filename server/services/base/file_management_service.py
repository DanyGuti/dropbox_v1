'''
This file contains the DropBoxService class,
which is responsible for handling the file operations
'''
from server.imports.import_server_base import os, shutil,\
    Response, get_diff_path, normalize_path
from server.interfaces.local_fms_interface import IFileManagementService

class FileManagementService(
    IFileManagementService
):
    '''
    DropBox service
    '''
    def write_chunk_no_mv(
        self,
        file_name: str,
        server_relative_path: str,
        chunk: bytes,
        action :str
    ) -> Response:
        '''
        upload a chunk of a file to the server
        '''
        try:
            # delete_file(self.server_relative_path)
            with open(server_relative_path, "wb") as arc:
                arc.write(chunk)
            return Response(
                message=file_name \
                + " succesfully modified file!",
                status_code=0
            )
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(
                error=e,
                message=f'Error in action: {action}, error: {e}',
                status_code=13
            )
    def write_chunk_mv(
        self,
        client_path: str,
        dst_path: str,
        file_name: str,
        server_relative_path: str,
    ) -> Response:
        '''
        upload a chunk of a file to the server mv action
        '''
        try:
            print(f"destination_path: {dst_path}")
            src_path: str = server_relative_path
            # Get difference from path to delete, then change to the path to overwrite
            diff_path: str = get_diff_path(dst_path, client_path)
            new_relative_path: str = os.path.join(server_relative_path, diff_path)
            # normalize
            server_relative_path: str = normalize_path(new_relative_path)
            # Handle the case when the file does not exist (create empty file)
            print(f"Moving file from {src_path} to {server_relative_path}")
            print(diff_path)
            if not os.path.exists(server_relative_path):
                with open(server_relative_path, "wb") as empty_file:
                    empty_file.write(b'')
            shutil.move(src_path, server_relative_path)
            return Response(
                message=file_name +\
                " succesfully moved file!",
                status_code=0
            )
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message="Error: ", status_code=13)
    def file_creation(
        self,
        file_name: str,
        server_relative_path: str,
    )-> Response:
        '''
        create a file
        '''
        try:
            open(server_relative_path, 'x', encoding='utf-8')
            return Response(message=file_name + " succesfully touched!")
        except FileExistsError:
            print(f"Something went wrong: the file {file_name}\
                already exists in the given path."
            )
            return Response(error="FileExistsError", message="Error: ", status_code=6)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message=f'Error en action: {e}', status_code=13)
    def file_deletion(
        self,
        server_relative_path: str,
        file_name: str,
    ) -> Response:
        '''
        Delete a file on the server
        '''
        try:
            os.remove(server_relative_path)
            return Response(message=file_name + " succesfully removed!", status_code=0)
        except FileNotFoundError:
            print(f"Something went wrong: file {file_name} not found.")
            return Response(error="FileNotFoundError",
                            message="Something went wrong: file " +\
                                {file_name} + " not found.",
                            status_code=5
                        )
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message="Error: ", status_code=13)
    def dir_creation(
        self,
        dir_name: str,
        server_relative_path: str,
    ) -> Response:
        '''
        Create a directory on the server
        '''
        try:
            os.mkdir(server_relative_path)
            return Response(message=dir_name + " succesfully cretated directory!")

        except FileExistsError:
            print(f"Something went wrong: the directory {dir_name}\
                already exists in the given path."
            )
            return Response(error = "FileExistsError", message = "Error: ", status_code = 6)
        except (OSError, IOError) as e:
            print(f"Error: {e}")
            return Response(error=e, message="Error: ", status_code=13)
    def dir_deletion(
        self,
        server_relative_path: str,
        dir_name: str,
    ) -> Response:
        '''
        Delete a directory on the server
        '''
        try:
            os.rmdir(server_relative_path)
            return Response(message = dir_name + " succesfully deleted directory!")

        except FileNotFoundError:
            print(f"Something went wrong: the directory {dir_name} not found.")
            return Response(error = "FileNotFoundError", message = "Error: ", status_code = 5)
        except (OSError, IOError) as e:
            print(f"Something went wrong: the directory {dir_name} is not empty.")
            return Response(error=e, message="Error: ", status_code=13)
