from ..bo.messages.get_blocks import Get_blocks
from ..bo.messages.blocks import Blocks
import os
import sys
sys.path.append("..")
from src.db.mapper import Mapper
from src.blockchain.block import Block


class Block_download():
    def __init__(self, node) -> None:
        self.node = node

    # node that requests blocks
    def get_blocks(self, node_connection):
        latest_block_hash = Mapper().read_latest_block_hash()
        msg = Get_blocks(latest_block_hash)
        self.node.send_to_node(node_connection, msg.to_dict())

    # node that receives request for blocks
    def get_blocks_received(self, node_connection, message):
        msg_in = Get_blocks.from_dict(message)
        latest_block_hash_from_peer = msg_in.get_latest_block_hash()
        own_latest_block_hash = Mapper().read_latest_block_hash()
        my_block_hashes = os.listdir(os.getcwd() + "/db/blocks/")
        if latest_block_hash_from_peer != own_latest_block_hash and latest_block_hash_from_peer in my_block_hashes:
            blocks = self.build_blockchain_from_hash(latest_block_hash_from_peer, [])
        else:
            # up to date with peer or local blockchain doesn't contain latest_block_hash_from_peer
            blocks = []
        msg = Blocks(blocks)
        self.node.send_to_node(node_connection, msg.to_dict())

    # node that requested blocks
    def blocks_received(self, message):
        msg_in = Blocks.from_dict(message)
        my_block_hashes = os.listdir(os.getcwd() + "/db/blocks/")
        local_latest_block_hash = Mapper().read_latest_block_hash()
        successor_of_local_latest_block_count = 0
        if len(msg_in.get_blocks()) == 0:
            print("Already synced with peer")
            return
        for block in msg_in.get_blocks():
            if block.validate() is False:
                print("A block is not valid")
                return
            if block.saved_hash in my_block_hashes:
                print("The local blockchain contains one of the blocks already")
                return
            if block.predecessor == local_latest_block_hash:
                successor_of_local_latest_block_count += 1
        if successor_of_local_latest_block_count != 1:
            print("Not exactly one successor of the local latest block")
            return

        for block in msg_in.get_blocks():
            block.write_to_file()
            Mapper().write_latest_block_hash(block.saved_hash)

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

        blocks = self.build_blockchain_from_hash(successor_block.saved_hash, blocks_to_send)
        return blocks
