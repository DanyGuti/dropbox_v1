'''
Module containing helper functions
'''
import os

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

SERVERS_IP: str = "158.227.125.64" ##IP ADDRESS OF THE MASTER SERVER ON THE SYSTEM
SLAVE_SERVER_PORT: int = 50083
