'''
File that contains the election service
'''
from server.interfaces.election_interface import IElection
from server.imports.import_server_base import rpyc

class Election(IElection):
    '''
    Election service of a new leader
    '''
    @rpyc.exposed
    def send_election_message(
        self,
        message_election: str,
        nodes: list[tuple[str, int]],
        curr_node: int
    ) -> tuple[list[str], int]:
        '''
        Send an election message to greater identified nodes
        '''
        # For every node greater than curr_node, send the election message
        accum_nodes: list[tuple[str, int]] = []
        for ip, node in nodes:
            if node > curr_node:
                # Send the election message
                accum_nodes.append((node, ip))
        responses: list[str] = []
        next_max_node: int = -1
        for ip, node in accum_nodes:
            # Send the election message
            try:
                conn: rpyc.Connection = rpyc.connect(ip, 18861)
                response_slave: str = conn.root.receive_election_message(message_election)
                responses.append(response_slave)
                if response_slave == "ok":
                    next_max_node = node
            except ConnectionRefusedError:
                print(f"Connection refused to {ip}")
                responses.append("")
            except Exception as e:
                print(f"Error: {e}")
                responses.append("")
        return responses, next_max_node
    @rpyc.exposed
    def elect_leader(self) -> None:
        '''
        Elect a new leader based on the highest id
        '''
        print(self.receive_election_message("leader"))
    @rpyc.exposed
    def update_leader(self):
        '''
        Update the leader
        '''
        pass
    @rpyc.exposed
    def receive_election_message(
        self,
        message_election: str
    ) -> str:
        '''
        Receive an election message
        '''
        if message_election == "election":
            return "ok"
        elif message_election == "leader":
            return "ok"
        return "error"
