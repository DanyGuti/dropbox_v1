'''
Module containing main function for the client
'''
from client.imports.import_base import os
from client.client_impl import Client
from client.client_watcher_watchdog import ClientWatcher

current_directory = os.getcwd()
target_directory = os.path.join(current_directory, "dropbox_genial_loli_app")
                                
CWD: str = os.path.dirname(os.path.abspath(__file__))
print(current_directory)

def main() -> None:
    '''
    Main function
    '''
    client: Client = Client("Guty")
    client.start_connection(CWD)
    try:
        if client.conn:
            try:
                DIR_NAME: str = "dropbox_genial_loli_app"
                # Check if the directory exists
                if not os.path.exists(DIR_NAME):
                    # If it doesn't exist, create it
                    os.mkdir(DIR_NAME)
                    print(f"Directory '{DIR_NAME}' created.")
            except OSError as e:
                client.handle_error(e)
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