class Peer():
    def __init__(self, host, port) -> None:
        super().__init__()
        self._host = host
        self._port = port

    def get_host(self):
        return self._host

    def set_host(self, host):
        self._host = host

    def get_port(self):
        return self._port

    def set_port(self, port):
        self._port = port

    def to_dict(self):
        return {
            "host": self.get_host(),
            "port": self.get_port(),
        }

    @staticmethod
    def from_dict(dict):
        return Peer(dict["host"], dict["port"])
