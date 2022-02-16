from datetime import datetime
import hashlib
import json
from abc import ABC, abstractmethod
import os
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
    def __init__(self, source=None, target=None, amount=0, timestamp=datetime.now()):
        self.source = source
        self.target = target
        self.amount = amount
        self.timestamp = timestamp

    @staticmethod
    def from_dict(transaction_dict):
        if type(transaction_dict["timestamp"]) == str:
            timestamp = datetime.strptime(transaction_dict["timestamp"], '%m/%d/%Y, %H:%M:%S')
        else:
            timestamp = transaction_dict["timestamp"]

        return Transaction(transaction_dict["source"], transaction_dict["target"],
                           transaction_dict["amount"], timestamp)

    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "amount": self.amount,
            "timestamp": self.timestamp.strftime("%m/%d/%Y, %H:%M:%S")
        }
        
    def hash(self):
        return hashlib.sha256(self.serialize()).hexdigest()

    def get_balance(self):
        balance = 100   # +100 balance for testing
        cwd = os.getcwd()
        if cwd.endswith('tests'):
            cwd = os.path.dirname(os.getcwd())   # if in directory 'tests', go one directory up
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
                print("no transaction")
        return balance

    def validate(self):
        balance = self.get_balance()
        if balance < self.amount:
            print("Not valid: " + str(self.source) + " can't send " +
                  str(self.amount) + " with a balance of " + str(balance))
            return False
        else:
            return True


class Block(Serializable):
    def __init__(self, pred=None, transactions=None, saved_hash=None):
        if transactions is None:
            transactions = list()
        self.predecessor = pred
        self.transactions = transactions
        self.saved_hash = saved_hash

    @staticmethod
    def from_dict(block_dict, block_hash):
        block = Block(block_dict["predecessor"], block_dict["transactions"], block_hash)
        transaction_objects = []
        for transaction_dict in block.transactions:
            transaction_objects.append(Transaction.from_dict(transaction_dict))
        block.transactions = transaction_objects
        return block

    def to_dict(self):
        transactions = list()
        for t in self.transactions:
            transactions.append(t.to_dict())

        return {
            "predecessor": self.predecessor,
            "transactions": transactions
        }

    def to_dict_with_hash(self):
        transactions = list()
        for t in self.transactions:
            transactions.append(t.to_dict())

        return {
            "hash": self.hash(),
            "predecessor": self.predecessor,
            "transactions": transactions
        }

    def hash(self):
        transactions = list()
        for t in self.transactions:
            transactions.append(json.dumps(t.to_dict()))
        if len(transactions) != 0:
            mtree = MerkleTree(transactions)
            t_hash = mtree.getRootHash()
        else:
            t_hash = transactions

        block_dict = {
            "predecessor": self.predecessor,
            "transactions": t_hash
        }
        serialized_block = json.dumps(block_dict, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized_block).hexdigest()

    def add_transaction(self, t):
        self.transactions.append(t)

    def validate(self):
        for transaction in self.transactions:
            if transaction.validate() is False:
                return False

        if self.saved_hash != self.hash():
            print("Not valid: recalculating the hash results in a different hash")
            return False
        else:
            return True

    def write_to_file(self):
        hash = self.hash()
        block = self.serialize()

        Mapper().write_block(hash, block)
