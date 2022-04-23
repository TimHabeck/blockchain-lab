from ..bo.messages.get_blocks import Get_blocks
from ..bo.messages.blocks import Blocks
from src.db.mapper import Mapper
from src.blockchain.block import Block
import os
import sys
sys.path.append("..")


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
        if latest_block_hash_from_peer == own_latest_block_hash:
            # up to date with peer
            print("Already synced with peer")
            blocks = []
            info = "already-synced"
            msg = Blocks(blocks, info)
            self.node.send_to_node(node_connection, msg.to_dict())
        elif latest_block_hash_from_peer != own_latest_block_hash:
            if latest_block_hash_from_peer not in my_block_hashes:
                # local blockchain doesn't contain latest_block_hash_from_peer
                # -> possible fork
                print("the local blockchain doesn't contain the latest_block_hash from peer")
                blocks = self.build_whole_blockchain()
                info = "fork-detected"
                msg = Blocks(blocks, info)
                self.node.send_to_node(node_connection, msg.to_dict())
            elif latest_block_hash_from_peer in my_block_hashes:
                print("send blocks to peer")
                blocks = self.build_blockchain_from_hash(latest_block_hash_from_peer, [])
                msg = Blocks(blocks)
                self.node.send_to_node(node_connection, msg.to_dict())

    # node that requested blocks
    def blocks_received(self, message):
        msg_in = Blocks.from_dict(message)
        my_block_hashes = os.listdir(os.getcwd() + "/db/blocks/")
        local_latest_block_hash = Mapper().read_latest_block_hash()
        successor_of_local_latest_block_count = 0
        if msg_in.get_info() == "already-synced":
            print("Already synced with peer")
            return
        if msg_in.get_info() == "fork-detected":
            print("the predecessor of the received block doesn't match "
                  "the local latest block")
            # if the chain from the peer is longer than the local chain,
            # rebuild the whole thing
            if len(msg_in.get_blocks()) > len(my_block_hashes):
                print("Less local blocks, adopting longest chain")
                db_dir = os.getcwd() + "/db/blocks/"
                for block in os.listdir(db_dir):
                    os.remove(os.path.join(db_dir, block))
                my_block_hashes = ''
                local_latest_block_hash = ''
            else:
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

        if successor_of_local_latest_block_count != 1 \
                and msg_in.get_info() != "fork-detected":
            print("Not exactly one successor of the local latest block")
            return

        for block in msg_in.get_blocks():
            block.write_to_file()
            Mapper().write_latest_block_hash(block.saved_hash)
        print("block(s) saved")

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
        blocks_to_send = []
        for block_hash in os.listdir(os.getcwd() + "/db/blocks/"):
            block_dict = Mapper().read_block(block_hash)
            block: Block = Block().from_dict(block_dict, block_hash)
            blocks_to_send.append(block)
        return blocks_to_send
