from src.blockchain.block import Block
from src.db.mapper import Mapper
from src.network.conversations.block_broadcasting import Block_broadcasting
import hashlib
import os
import logging


class Blockchain():
    def add_block(self, transactions, node=None):
        pred_hash = Mapper().read_latest_block_hash()

        block = Block(pred=pred_hash)
        for transaction in transactions:
            block.add_transaction(transaction)
        
        block.nonce = block.find_nonce()

        block_hash = block.hash()
        logging.debug(f"{block_hash=}")
        block.saved_hash = block_hash
        cwd = os.getcwd()
        if cwd.endswith('tests'):
            cwd = os.path.dirname(os.getcwd())   # if in directory 'tests', go one directory up
        my_block_hashes = os.listdir(cwd + "/db/blocks/")
        if block.validate() is False:

            print("The block is not valid")
            return
        if block_hash in my_block_hashes:
            print("The local blockchain contains the block already")
            return
        block.write_to_file()
        Mapper().write_latest_block_hash(block_hash)
        print("block saved")

        if node:
            block_broadcasting = Block_broadcasting(node)
            block_broadcasting.broadcast_block(block)
            print("block broadcasted")

    def add_block_without_validation(self, transactions):
        pred_hash = Mapper().read_latest_block_hash()

        block = Block(pred=pred_hash)
        for transaction in transactions:
            block.add_transaction(transaction)
        block_hash = block.hash()
        block.saved_hash = block_hash

        block.write_to_file()
        Mapper().write_latest_block_hash(block_hash)
        print("block saved")

    def create_genesis_block(self):
        block = Block()
        block = block.serialize()
        hash = hashlib.sha256(block).hexdigest()

        Mapper().write_block(hash, block)

        Mapper().write_latest_block_hash(hash)
