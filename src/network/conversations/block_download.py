import logging
import os
import sys
sys.path.append("..")
from ..bo.messages.get_blocks import Get_blocks
from ..bo.messages.blocks import Blocks
from src.db.mapper import Mapper
from src.blockchain.block import Block


class Block_download():
    def __init__(self, node) -> None:
        self.node = node
        # hash of the genesis block
        self.genesis_block_hash = "ca831b26dda2d7f27cf1eead9528ef3f1b793c6a68e9e652e8fb3e6164425e38"

    # node that requests blocks
    def get_blocks(self, node_connection):
        latest_block_hash = Mapper().read_latest_block_hash()
        msg = Get_blocks(latest_block_hash)
        self.node.send_to_node(node_connection, msg.to_dict())

    def serve_block_request(self, node_connection, message):
        """ Handle a received Get_blocks request from a peer node """
        msg_in = Get_blocks.from_dict(message)
        latest_block_hash_from_peer = msg_in.get_latest_block_hash()
        own_latest_block_hash = Mapper().read_latest_block_hash()
        my_block_hashes = os.listdir(os.getcwd() + "/db/blocks/")
        if latest_block_hash_from_peer == own_latest_block_hash:
            # up to date with peer
            logging.debug("Already synced with peer")
            blocks = []
            info = "already-synced"
            msg = Blocks(blocks, info)
            self.node.send_to_node(node_connection, msg.to_dict())
        elif latest_block_hash_from_peer != own_latest_block_hash:
            if latest_block_hash_from_peer not in my_block_hashes:
                # local blockchain doesn't contain latest_block_hash_from_peer -> possible fork
                logging.warning("the local blockchain doesn't contain the latest_block_hash "
                                "from peer")
                blocks = self.build_whole_blockchain()
                info = "fork-detected"
                msg = Blocks(blocks, info)
                self.node.send_to_node(node_connection, msg.to_dict())
            elif latest_block_hash_from_peer in my_block_hashes:
                logging.debug("send blocks to peer")
                blocks = self.build_blockchain_from_hash(latest_block_hash_from_peer, [])
                msg = Blocks(blocks)
                self.node.send_to_node(node_connection, msg.to_dict())

    # node that requested blocks
    def receive_blocks(self, message):
        """ Receive blocks from a peer node after sending a Get_blocks request """
        msg_in = Blocks.from_dict(message)
        my_block_hashes = os.listdir(os.getcwd() + "/db/blocks/")
        local_latest_block_hash = Mapper().read_latest_block_hash()
        successor_of_local_latest_block_count = 0
        if msg_in.get_info() == "already-synced":
            logging.debug("Already synced with peer")
            return False
        if msg_in.get_info() == "fork-detected":
            logging.warning("Possible fork detected")
            # if the chain from the peer is longer than the local chain, rebuild the whole thing
            if len(msg_in.get_blocks()) > len(my_block_hashes):
                logging.debug("Less local blocks, adopting longest chain")
                db_dir = os.getcwd() + "/db/blocks/"
                # delete the local blockchain
                for block_hash in os.listdir(db_dir):
                    # keep the genesis block
                    if block_hash == self.genesis_block_hash:
                        continue
                    os.remove(os.path.join(db_dir, block_hash))
                my_block_hashes = ''
                local_latest_block_hash = ''
            else:
                return False

        for block in msg_in.get_blocks():
            if block.validate() is False:
                logging.error("A block is not valid")
                return False
            if block.saved_hash in my_block_hashes:
                logging.debug("The local blockchain contains one of the blocks already")
                return False
            if block.predecessor == local_latest_block_hash:
                successor_of_local_latest_block_count += 1

        if successor_of_local_latest_block_count != 1 \
                and msg_in.get_info() != "fork-detected":
            logging.error("Not exactly one successor of the local latest block")
            return False

        for block in msg_in.get_blocks():
            block.write_to_file()
            Mapper().write_latest_block_hash(block.saved_hash)
        logging.info("block(s) saved")
        return True

    # helper method
    def get_successor_block(self, predecessor_hash):
        for block_hash in os.listdir(os.getcwd() + "/db/blocks/"):
            block_dict = Mapper().read_block(block_hash)
            block: Block = Block().from_dict(block_dict, block_hash)
            if block.predecessor == predecessor_hash:
                return block

    # recursive helper method
    def build_blockchain_from_hash(self, predecessor_hash, blocks_to_send):
        successor_block = self.get_successor_block(predecessor_hash)
        blocks_to_send.append(successor_block)

        local_latest_block_hash = Mapper().read_latest_block_hash()
        if successor_block.saved_hash == local_latest_block_hash:
            return blocks_to_send

        blocks_to_send = self.build_blockchain_from_hash(successor_block.saved_hash, blocks_to_send)
        return blocks_to_send

    def build_whole_blockchain(self):
        ''' Rebuild the whole blockchain in case a peer node discovered a fork '''
        blocks_to_send = []
        for block_hash in os.listdir(os.getcwd() + "/db/blocks/"):
            # ignore the genesis block
            if block_hash == self.genesis_block_hash:
                continue
            block_dict = Mapper().read_block(block_hash)
            block: Block = Block().from_dict(block_dict, block_hash)
            blocks_to_send.append(block)
        return blocks_to_send
