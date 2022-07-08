import hashlib
import os
import logging
from blockchain.block import Block
from db.mapper import Mapper
from network.conversations.block_broadcasting import Block_broadcasting

log = logging.getLogger()


class Blockchain():
    def add_block(self, transactions, node=None):
        pred_hash = Mapper().read_latest_block_hash()

        block = Block(pred=pred_hash)
        for transaction in transactions:
            block.add_transaction(transaction)

        if not node:
            log.error("No node specified, cannot mine block")
            return

        node.set_currently_mined_block(block)
        block.set_nonce(block.find_nonce())

        block_hash = block.hash()
        log.debug(f"{block_hash=}")
        block.set_saved_hash(block_hash)
        cwd = os.getcwd()

        if cwd.endswith('tests'):
            cwd = os.path.dirname(os.getcwd())   # if in directory 'tests', go one directory up
        my_block_hashes = os.listdir(cwd + "/db/blocks/")

        if block.validate() is False:
            log.info("The block is not valid")
            return

        if block_hash in my_block_hashes:
            log.info("The local blockchain contains the block already")
            return

        block.write_to_file()
        Mapper().write_latest_block_hash(block_hash)
        log.info("block saved")

        if node:
            block_broadcasting = Block_broadcasting(node)
            block_broadcasting.broadcast_block(block)
            log.info("block broadcasted")

    def create_genesis_block(self):
        block = Block()
        block = block.serialize()
        block_hash = hashlib.sha256(block).hexdigest()

        Mapper().write_block(block_hash, block)
        Mapper().write_latest_block_hash(block_hash)
