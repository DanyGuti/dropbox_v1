'''
This file contains the interface for the Health service
'''
from abc import ABC, abstractmethod

class IHealthService(ABC):
    '''
    Interface for the Health service
    '''
    @abstractmethod
    def get_health_status(self) -> float:
        '''
        Get the health status of the server
        '''
    @abstractmethod
    def set_health_status(self, health_status: float) -> None:
        '''
        Set the health status of the server
        '''
    @abstractmethod
    def calculate_health_status(self) -> float:
        '''
        Calculate the health status of the server
        '''
