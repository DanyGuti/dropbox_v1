import rpyc

class Client():
    conn: rpyc.Connection = None
    def __init__(self, requestResponse: dict = None) -> None:
        self.requestResponse = requestResponse if requestResponse else {}
    def startConnection(self) -> None:
        try:
            self.conn = rpyc.connect("localhost", 18861)
            print(f"Connected to server: {self.conn}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
    def sendReq(self) -> dict:
        if self.conn is None:
            print("No active connection to the server!")
            return
        # Send request to the server (example method call)
        try:
            print(self.requestResponse)
            response = self.conn.root.get_answer()  # Call an exposed method from the server
            print(f"Response from server: {response}")
        except Exception as e:
            print(f"Failed to send request: {e}")
        ## rpyc.escribirDocumento():
    def receiveResp() -> dict:
        pass
    def handleError() -> dict:
        pass