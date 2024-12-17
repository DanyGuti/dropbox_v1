# dropbox_v1
---
## Distributed systems project
### What is the project about?
It is able to run one master node, which acts as a coordinator node, but also two or more slaves should be launched.

The project is based on the usage of RPCs for communication between servers, as well as for client communication. RPyC library is used, and also Watchdog Observer library.

System was based on various design patterns (factory, usage of decorators, observer and state), following best besides the usage of best practices in Python.

### What is the project able to do?
A client can make commands via terminal/konsole or console (which will be specified in advance), then the server is able to mirror the commands done locally in server side in a transparent way, following distributed systems principles.
* touch <file_name>
* cp <file_name> <dest_path>
* mv <file_name1> <file_name2>
* nano <file_name> (overwriting or a new file)
* rm <file_name>
* mkdir <dir_name>
* rmdir <dir_name>
* repeating the commands from parent directories
---
### How to run the project?
You must follow the next process to run the project:

### Server side
If not already installed you MUST install rpyc:
> `pip install rpyc`

Start servers (can be in different machines or just one in various terminals), also one computer must serve as the service registry.
1. For the service registry run in terminal/console or konsole at root directory: `rpyc_registry --port 50081 -l true`
2. In another computer or in the same (must be in another terminal/console or konsole window), run the following at root directory: `python3 -m app.main_master`
3. In another computer or in the same (must be in another terminal/console or konsole window), run the following at root directory: `python3 -m app.main_slave`

### Client side
1. At root directory, in terminal/console or konsole, run: `python3 -m client.main`

> Enjoy