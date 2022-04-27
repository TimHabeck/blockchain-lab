import hashlib
import json
import logging
import os
from ecdsa import VerifyingKey, SECP256k1
from abc import ABC, abstractmethod
from datetime import datetime
from src.blockchain.merkle_tree import MerkleTree
from src.db.mapper import Mapper


class Serializable(ABC):
    def serialize(self):
        return json.dumps(self.to_dict(),
                          sort_keys=True).encode("utf-8")

    @abstractmethod
    def to_dict(self):
        pass


class Transaction(Serializable):
    def __init__(self, source=None, target=None, amount=0, timestamp=datetime.now(),
                 pubkey=None, sig=None):
        self.source = source
        self.target = target
        self.amount = amount
        self.timestamp = timestamp
        if pubkey and sig:
            self.pubkey = VerifyingKey.from_string(bytes.fromhex(pubkey), SECP256k1, hashlib.sha256,
                                                   valid_encodings=['raw'])
            self.sig = bytes.fromhex(sig)

    def set_pubkey(self, pubkey):
        self.pubkey = pubkey

    def set_signature(self, sig):
        self.sig = sig

    @staticmethod
    def from_dict(transaction_dict):
        if type(transaction_dict["timestamp"]) == str:
            timestamp = datetime.strptime(
                transaction_dict["timestamp"], '%m/%d/%Y, %H:%M:%S'
            )
        else:
            timestamp = transaction_dict["timestamp"]

        return Transaction(transaction_dict["source"], transaction_dict["target"],
                           transaction_dict["amount"], timestamp, transaction_dict["pubkey"],
                           transaction_dict["sig"])

    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "amount": self.amount,
            "timestamp": self.timestamp.strftime("%m/%d/%Y, %H:%M:%S")
        }

    def to_full_dict(self):
        ''' Create a dict that also contains the pubkey and the signature for the transaction '''
        return {
            "source": self.source,
            "target": self.target,
            "amount": self.amount,
            "timestamp": self.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
            # get the text string representation of the ECDSA key binary blobs with hex()
            "pubkey": self.pubkey.to_string().hex(),
            "sig": self.sig.hex()
        }

    def hash(self):
        return hashlib.sha256(self.serialize()).hexdigest()

    def get_balance(self):
        balance = 100   # +100 balance for testing
        cwd = os.getcwd()
        if cwd.endswith('tests'):
            # if in directory 'tests', go one directory up
            cwd = os.path.dirname(os.getcwd())
        local_block_hashes = os.listdir(cwd + "/db/blocks/")
        for block_hash in local_block_hashes:
            block_dict = Mapper().read_block(block_hash)
            block: Block = Block().from_dict(block_dict, block_hash)
            try:
                for transaction in block.transactions:
                    if transaction.source == self.source:
                        balance -= transaction.amount
                    if transaction.target == self.source:
                        balance += transaction.amount
            except AttributeError:
                logging.error("no transaction")
        return balance

    def validate(self):
        # verify the transaction data structure
        # we just assume if the keys are present, the values are also valid
        expected_keys = set(["amount", "source", "target", "timestamp"])
        if set(self.to_dict()) != expected_keys:
            logging.error("Transaction key fields invalid")
            return False

        balance = self.get_balance()
        if balance < self.amount:
            logging.error(f"Not valid: {self.source} can't send {self.amount} "
                          f"with balance of {balance}")
            return False

        # verify the transaction signature
        tx_hash = self.hash()
        if not self.pubkey.verify(self.sig, tx_hash.encode("utf-8")):
            logging.error("Cannot verify transaction signature")
            return False

        logging.debug("Transaction is valid")
        return True


class Block(Serializable):
    def __init__(self, pred=None, transactions=None, saved_hash=None, nonce=None):
        if transactions is None:
            transactions = list()
        self.predecessor = pred
        self.transactions = transactions
        self.nonce = nonce
        self.saved_hash = saved_hash

    @staticmethod
    def from_dict(block_dict, block_hash):
        logging.debug(f"{block_dict=}")
        block = Block(block_dict["predecessor"],
                      block_dict["transactions"], block_hash, int(block_dict["nonce"]))
        transaction_objects = []
        for transaction_dict in block.transactions:
            transaction_objects.append(Transaction.from_dict(transaction_dict))
        block.transactions = transaction_objects
        return block

    def to_dict(self):
        transactions = list()
        for t in self.transactions:
            transactions.append(t.to_full_dict())

        return {
            "predecessor": self.predecessor,
            "transactions": transactions,
            "nonce": self.nonce
        }

    def to_dict_with_hash(self):
        transactions = list()
        for t in self.transactions:
            transactions.append(t.to_full_dict())

        return {
            "hash": self.hash(),
            "predecessor": self.predecessor,
            "transactions": transactions,
            "nonce": self.nonce
        }

    def hash(self):
        if self.nonce is not None:
            transactions = list()
            for t in self.transactions:
                transactions.append(json.dumps(t.to_dict()))
            transactions.append(str(self.nonce))
            if len(transactions) != 0:
                mtree = MerkleTree(transactions)
                t_hash = mtree.getRootHash()
            else:
                t_hash = transactions

            block_dict = {
                "predecessor": self.predecessor,
                "transactions": t_hash,
                "nonce": self.nonce
            }
            serialized_block = json.dumps(
                block_dict, sort_keys=True).encode("utf-8")
            return hashlib.sha256(serialized_block).hexdigest()
        else:
            logging.error("No Nonce available jet. Mine it first!")

    def add_transaction(self, t):
        self.transactions.append(t)

    def validate(self):
        for transaction in self.transactions:
            if transaction.validate() is False:
                return False

        if self.saved_hash != self.hash():
            logging.error("Not valid: recalculating the hash results in a different hash")
            return False
        else:
            return True

    def write_to_file(self):
        hash = self.hash()
        block = self.serialize()
        Mapper().write_block(hash, block)

    def find_nonce(self, difficulty=4):
        transactions = list()
        for t in self.transactions:
            transactions.append(json.dumps(t.to_dict()))
        nonce = 0
        while True:
            # Try with this nonce
            transactions.append(str(nonce))
            mtree = MerkleTree(transactions)
            t_hash = mtree.getRootHash()

            # check the result
            important_digits = t_hash[0:difficulty]
            not_null_digits = important_digits.replace("0", "")
            if len(not_null_digits) == 0:
                logging.info(f"Successfull at {nonce}")
                return nonce
            else:
                logging.debug(f"not successfull at {nonce}")
                transactions.pop()
                nonce += 1
