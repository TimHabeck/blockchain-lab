import os
import logging
from network.conversations.block_download import Block_download
from network.bo.messages.block_message import Block_message
from db.mapper import Mapper
from blockchain.block import Block


class Block_broadcasting():
    def __init__(self, node) -> None:
        self.node = node

    # node that broadcasts the block
    def broadcast_block(self, block: Block):
        msg = Block_message(block)
        self.node.send_to_nodes(msg.to_dict())

    # node that receives the block
    def block_received(self, sender_node_conn, message) -> bool:
        msg_in = Block_message.from_dict(message)
        block = msg_in.get_block()

        my_block_hashes = os.listdir(os.getcwd() + "/db/blocks/")
        local_latest_block_hash = Mapper().read_latest_block_hash()

        if block.validate() is False:
            logging.error("The block is not valid")
            return False
        if block.saved_hash in my_block_hashes:
            logging.error("The local blockchain contains the block already")
            return False
        if block.predecessor == local_latest_block_hash:
            block.write_to_file()
            Mapper().write_latest_block_hash(block.saved_hash)
            logging.info("block saved")
        else:
            logging.warning("the predecessor of the received block doesn't match the "
                            "local latest block")
            logging.info("initiate block download")
            block_download = Block_download(self.node)
            block_download.get_blocks(sender_node_conn)

        # relay block
        for conn in self.node.all_nodes:
            if conn.id != sender_node_conn.id:
                logging.debug(f"relay block {block.saved_hash} from Node {self.node.id} to Node "
                              f"{conn.id}")
                self.node.send_to_node(conn, message)
        return True
