'''
File that contains the election service
'''
from rpyc.utils.classic import obtain
from server.interfaces.election_interface import IElection
from server.imports.import_server_base import rpyc

class Election(IElection):
    '''
    Election service of a new leader
    '''
    nodes: list[tuple[str, int]] = []
    @rpyc.exposed
    def send_election_message(
        self,
        message_election: str,
        curr_node: int,
    ) -> tuple[list[str], int]:
        '''
        Send an election message to greater identified nodes
        '''
        # For every node greater than curr_node, send the election message
        accum_nodes: list[tuple[str, int]] = []
        for ip, node in self.nodes:
            if node > curr_node:
                # Send the election message
                accum_nodes.append((node, ip))
        responses: list[str] = []
        next_max_node: int = -1
        for ip, node in accum_nodes:
            # Send the election message
            try:
                conn: rpyc.Connection = rpyc.connect(
                    ip,
                    50081,
                    config={"allow_all_attrs": True, "allow_pickle": True}
                )
                response_slave: str = conn.root.election_service.receive_election_message(message_election)
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
    def elect_leader(self, nodes: list[tuple[str, int]]) -> None:
        '''
        Elect a new leader based on the highest id
        '''
        for ip, _ in nodes:
            # Send the election message
            try:
                conn: rpyc.Connection = rpyc.connect(
                    ip,
                    50081,
                    config={"allow_all_attrs": True, "allow_pickle": True}
                )
                response_slave: str = conn.root.election_service.receive_election_message("leader")
                if obtain(response_slave) == "ok":
                    # Update the leader
                    conn.root.election_service.update_leader(conn.root)
                    print(f"Leader elected, in node with ip: {ip}")
            except ConnectionRefusedError:
                print(f"Connection refused to {ip}, in elect_leader")
            except Exception as e:
                print(f"Error: {e} in elect_leader")
    @rpyc.exposed
    def update_leader(self, service) -> None:
        '''
        Update the leader
        '''
        service.set_leader_ip(obtain(service.get_ip_service()))
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
        if message_election == "leader":
            return "ok"
        return "error"
    @rpyc.exposed
    def set_slaves_broadcasted(self, slaves: list[tuple[str, int]]) -> None:
        '''
        Receive the slaves broadcasted from the Coordinator
        '''
        print(obtain(slaves))
        self.nodes: list[tuple[str, int]] = obtain(slaves)
    def get_slaves_broadcasted(self) -> list[tuple[str, int]]:
        '''
        Get the slaves broadcasted from the Coordinator
        '''
        return self.nodes
