from .message import Message
from network.bo.peer import Peer


class Addr(Message):
    def __init__(self, peers) -> None:
        super().__init__()
        self._name = "addr"
        self._peers = peers

    def get_peers(self):
        return self._peers

    def set_peers(self, peers):
        self._peers = peers

    def to_dict(self):
        peers = []
        for peer in self.get_peers():
            if isinstance(peer, Peer):
                peers.append(peer.to_dict())

        return {
            "name": self.get_name(),
            "peers": peers,
        }

    @staticmethod
    def from_dict(dict):
        addr = Addr(dict["peers"])
        peers = []
        for peer in addr.get_peers():
            peers.append(Peer.from_dict(peer))
        addr.set_peers(peers)
        return addr
