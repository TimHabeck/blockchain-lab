import logging
from network.bo.peer import Peer
from network.bo.messages.addr import Addr
from network.bo.messages.connection_accepted import Connection_accepted

log = logging.getLogger()


class Initial_Peer_Discovery():
    def __init__(self, node) -> None:
        self.node = node

    # node that refuses connection
    def send_addr(self, node_connection):
        peers = []
        for conn in self.node.nodes_inbound:
            if conn.port != node_connection.port:
                peer = Peer(conn.host, conn.port)
                peers.append(peer)

        msg = Addr(peers)
        self.node.send_to_node(node_connection, msg.to_dict())
        node_connection.stop()   # stop connection

    # node that searches peer
    def addr_received(self, sender_node_conn, message):
        msg_in = Addr.from_dict(message)

        self.node.disconnect_with_node(sender_node_conn)
        self.node.potential_peers.remove(sender_node_conn.port)

        peer: Peer
        for peer in msg_in.get_peers():
            self.node.potential_peers.append(peer.get_port())

        self.node.connect_with_node('127.0.0.1', self.node.potential_peers[0])
        log.info(f"Potential peers: {self.node.potential_peers}")

    # node that accepts connection
    def send_connection_accepted(self, node_connection):
        msg = Connection_accepted()
        self.node.send_to_node(node_connection, msg.to_dict())
