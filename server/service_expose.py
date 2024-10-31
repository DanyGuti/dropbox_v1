'''
Start the connection exposed by the service
'''
import rpyc
from server.interfaces.service_expose import IServiceExposed
class ServiceExpose(IServiceExposed):
    '''
    Service exposed class
    '''
    def on_connect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is established
        '''
        print("Hello client!", conn)
    def on_disconnect(self, conn: rpyc.Connection) -> None:
        '''
        Method to be called when a connection is closed
        '''
        print("Goodbye client!", conn)
