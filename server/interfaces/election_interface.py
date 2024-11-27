'''
This file contains the interface for the Election service.
'''
from server.imports.import_server_base import ABC\
    , abstractmethod, Response

class IElection(ABC):
    '''
    Interface for the Election service
    '''
    @abstractmethod
    def send_election_message(
        self,
        message_election: str,
        nodes: list[tuple[str, int]],
        curr_node: int
    ) -> tuple[list[str], int]:
        '''
        Send election to the rest of the machines (higher id)
        '''
    @abstractmethod
    def elect_leader(self) -> Response:
        '''
        Elect a leader
        '''
    @abstractmethod
    def update_leader(self) -> Response:
        '''
        Update the leader
        '''
    @abstractmethod
    def receive_election_message(self, message_election: str) -> str:
        '''
        Receive an election message
        '''
