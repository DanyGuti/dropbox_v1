import os
import inotify.adapters

CWD = os.getcwd()

# Modularize by cwd
def isDockerEnv() -> bool:
    if CWD == '/usr/src/app/tmp':
        return True
    return False

# Main function for client hearing
def _main():
    i = inotify.adapters.Inotify()
    i.add_watch('/usr/src/app/tmp' if isDockerEnv() else CWD, mask=inotify.constants.IN_DELETE | inotify.constants.IN_CREATE | inotify.constants.IN_MODIFY)
    
    with open('/tmp/test_file', 'w'):
        pass

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        
        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
              path, filename, type_names))

if __name__ == '__main__':
    _main()