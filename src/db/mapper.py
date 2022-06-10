import json
import logging
import os


class Mapper():
    blockchain_dir = os.path.dirname(
        os.path.realpath(__file__)) + "/blocks"
    latest_block_hash_file = os.path.dirname(
        os.path.realpath(__file__)) + "/latest_block_hash"
    db_dir = os.path.dirname(os.path.realpath(__file__))

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
                data = file.read()
            return data.replace("\n", "")  # Remove any EOL characters
        except EOFError:
            logging.error("Unable to read latest-block-hash")

    @staticmethod
    def write_latest_block_hash(hash):
        try:
            with open(Mapper.latest_block_hash_file, "w") as file:
                file.write(str(hash))
        except EOFError:
            logging.error("Unable to write latest-block-hash")

    @staticmethod
    def read_nonce_list():
        try:
            with open(Mapper.db_dir + "/nonce_list") as file:
                data = file.read()
            return data
        except FileNotFoundError:
            # create the file
            with open(Mapper.db_dir + "/nonce_list", "a") as file:
                pass
            return None

    @staticmethod
    def append_to_nonce_list(nonce):
        try:
            with open(Mapper.db_dir + "/nonce_list", "a") as file:
                file.write(str(nonce) + "\n")
        except EOFError:
            logging.error("Unable to write nonce list")

    @staticmethod
    def read_latest_start_nonce():
        try:
            with open(Mapper.db_dir + "/start_nonce") as file:
                data = file.read()
            if data:
                return data.replace("\n", "")   # remove any EOF characters just in case
        except FileNotFoundError:
            # create the file
            with open(Mapper.db_dir + "/start_nonce", "a") as file:
                pass
        return 0

    @staticmethod
    def write_latest_start_nonce(nonce):
        try:
            with open(Mapper.db_dir + "/start_nonce", "wb") as file:
                file.write(nonce)
        except EOFError:
            logging.error("Unable to write start nonce")
