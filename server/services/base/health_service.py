'''
Health service module
'''
import server.interfaces.common.health_interface

class HealthService(
    server.interfaces.common.health_interface.IHealthService
    ):
    '''
    Health service class
    '''
    def __init__(self, health_status: float) -> None:
        self.health_status: float = health_status
    def get_health_status(self) -> float:
        '''
        Get the health status of the server
        '''
        return self.health_status
    def set_health_status(self, health_status: float) -> None:
        '''
        Set the health status of the server
        '''
        self.health_status = health_status
    def calculate_health_status(self) -> float:
        '''
        Calculate the health status of the server
        '''
        # TODO: Implement this method
        return 0.0
