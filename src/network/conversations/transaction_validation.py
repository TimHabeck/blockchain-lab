import logging
from network.bo.messages.prepare_to_validate import Prepare_to_validate
from network.bo.messages.vote import Vote
from network.bo.messages.global_decision import Global_decision

log = logging.getLogger()


class Transaction_Validation():
    def __init__(self, node, transaction) -> None:
        self.node = node
        self.transaction = transaction
        self.votes = {}

    # coordinator
    def send_prepare_to_validate(self):
        for peer in self.node.all_nodes:
            self.votes[peer.port] = "not_voted"

        msg = Prepare_to_validate(self.transaction)
        self.node.send_to_nodes(msg.to_dict())

    # participants
    def prepare_to_validate_received(self, sender_node_conn):
        valid = True

        # simulate that node 81 can't validate the transaction
        if self.node.port == 81:
            valid = False

        if valid:
            msg_out = Vote(True)
            log.debug("vote transaction valid")
        else:
            msg_out = Vote(False)
            log.debug("vote transaction not valid")

        self.node.send_to_node(sender_node_conn, msg_out.to_dict())

    # coordinator
    def vote_received(self, sender_node_conn, message):
        msg_in = Vote.from_dict(message)

        self.votes[sender_node_conn.port] = msg_in.get_valid()

        # if all peers have voted
        all_peers_voted = "not_voted" not in self.votes.values()
        # if len(self.votes) == len(self.node.all_nodes):
        if all_peers_voted:
            if all(self.votes.values()):
                # add transaction to mempool
                msg_out = Global_decision(True)
                log.debug("transaction validated and added to mempool")
            else:
                msg_out = Global_decision(False)
                log.error("transaction not valid")

            self.node.send_to_nodes(msg_out.to_dict())
            self.votes.clear()
            self.node.conversations.pop("transaction_validation")

    # participants
    def global_decision_received(self, message):
        msg = Global_decision.from_dict(message)

        if msg.get_valid():
            # add transaction to mempool
            log.debug("transaction validated and added to mempool")
        else:
            log.error("transaction not valid")

        self.node.conversations.pop("transaction_validation")
