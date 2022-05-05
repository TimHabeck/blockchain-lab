import json
import logging
import os


class Mapper():
    blockchain_dir = os.path.dirname(
        os.path.realpath(__file__)) + "/blocks"
    latest_block_hash_file = os.path.dirname(
        os.path.realpath(__file__)) + "/latest_block_hash"

    @staticmethod
    def write_block(hash, block):
        try:
            with open(Mapper.blockchain_dir + "/" + str(hash), "wb") as file:
                file.write(block)
        except EOFError:
            logging.error("Unable to write block")

    @staticmethod
    def read_block(block_hash):
        try:
            with open(Mapper.blockchain_dir + "/" + block_hash, "rb") as file:
                block_bytes = file.read()
                return json.loads(block_bytes)
        except EOFError:
            logging.error("Unable to read block")

    @staticmethod
    def read_latest_block_hash():
        try:
            with open(Mapper.latest_block_hash_file) as file:
                return file.read()
        except EOFError:
            logging.error("Unable to read latest-block-hash")

    @staticmethod
    def write_latest_block_hash(hash):
        try:
            with open(Mapper.latest_block_hash_file, "w") as file:
                file.write(str(hash))
        except EOFError:
            logging.error("Unable to write latest-block-hash")
