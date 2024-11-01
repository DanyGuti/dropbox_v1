'''
Module containing main function for the client
'''
from client.imports.import_base import os
from client.client_impl import Client
from client.client_watcher_watchdog import ClientWatcher

current_dir: str = os.path.dirname(os.path.abspath(__file__))
# Get the directory of the current file
CWD: str = os.path.normpath(os.path.join(current_dir, ".."))

def main() -> None:
    '''
    Main function
    '''
    client: Client = Client()
    client.start_connection(CWD)
    try:
        if client.conn:
            client_watcher: ClientWatcher = ClientWatcher(client_instance=client)
            client_watcher.start_watching()
    except KeyboardInterrupt:
        client.close_connection()
    except EOFError:
        client.close_connection()
    except (ConnectionError, OSError) as e:
        client.handle_error(e)
    finally:
        client.close_connection()

if __name__ == "__main__":
    main()
