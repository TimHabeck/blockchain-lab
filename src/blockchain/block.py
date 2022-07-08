import hashlib
import json
import logging
import os
import time
import numpy as np
import multiprocessing as mp
from abc import ABC, abstractmethod
from datetime import datetime
from ecdsa import VerifyingKey, SECP256k1
from sklearn.cluster import KMeans
from .merkle_tree import MerkleTree
from db.mapper import Mapper

log = logging.getLogger()


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
            block = Block().from_dict(block_dict, block_hash)
            try:
                for transaction in block.transactions:
                    if transaction.source == self.source:
                        balance -= transaction.amount
                    if transaction.target == self.source:
                        balance += transaction.amount
            except AttributeError:
                log.error(f"no transactions for block {block_hash}")
        return balance

    def validate(self):
        # verify the transaction data structure
        # we just assume if the keys are present, the values are also valid
        expected_keys = set(["amount", "source", "target", "timestamp"])
        if set(self.to_dict()) != expected_keys:
            log.error("Transaction key fields invalid")
            return False

        balance = self.get_balance()
        if balance < self.amount:
            log.error(f"Not valid: {self.source} can't send {self.amount} "
                      f"with balance of {balance}")
            return False

        # verify the transaction signature
        tx_hash = self.hash()
        if not self.pubkey.verify(self.sig, tx_hash.encode("utf-8")):
            log.error("Cannot verify transaction signature")
            return False

        log.info("Transaction is valid")
        return True


class Block(Serializable):
    def __init__(self, pred=None, transactions=None, saved_hash=None, nonce=None):
        if not transactions:
            transactions = list()
        self.predecessor = pred
        self.transactions = transactions
        self.nonce = nonce
        self.saved_hash = saved_hash
        self.is_mining = True
        self.nonce_list = []

    def set_nonce(self, nonce):
        self.nonce = nonce

    def get_nonce(self):
        return self.nonce

    def set_saved_hash(self, saved_hash):
        self.saved_hash = saved_hash

    @staticmethod
    def from_dict(block_dict, block_hash):
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
            log.error("No Nonce available yet. Mine it first!")

    def add_transaction(self, t):
        self.transactions.append(t)

    def validate(self):
        transactions = list()
        for transaction in self.transactions:  # Validating each transaction
            if transaction.validate() is False:
                return False
            transactions.append(json.dumps(transaction.to_dict()))

        if self.saved_hash != self.hash():
            log.error("Not valid: recalculating the hash results in a different hash")
            return False

        if not self.validate_nonce(transactions, self.nonce):
            log.error(f"Not valid: Nonce {self.nonce} does not fullfill the difficulty")
            return False

        log.info("Block is valid")
        return True

    def write_to_file(self):
        block_hash = self.hash()
        block = self.serialize()
        Mapper().write_block(block_hash, block)

    def stop_mining(self) -> None:
        self.is_mining = False

    def get_mining_status(self) -> bool:
        return self.is_mining

    def get_iterations(self) -> int:
        return self.iterations

    def determine_start_nonce(self) -> int:
        data = Mapper().read_nonce_list()
        if data:
            data = data.split('\n')         # str.split() returns a list of strings
            data.pop(-1)                    # remove the last element, since it is an empty string
            self.nonce_list = sorted(list(map(int, data)))  # convert all str to int and sort

        # only cluster every 5 blocks and when we have 15 initial values
        if len(self.nonce_list) >= 15 and len(self.nonce_list) % 5 == 0:
            data = np.array(self.nonce_list)
            kmeans = KMeans(n_clusters=3).fit(data.reshape(-1, 1))
            kmeans.predict(data.reshape(-1, 1))
            # return the mean value between the first centroid and the smallest nonce in the list
            return int((int(min(kmeans.cluster_centers_)[0]) + min(self.nonce_list)) / 2)
        # else return the last determined start nonce
        return int(Mapper().read_latest_start_nonce())

    def find_nonce(self, difficulty=4, method='bruteforce'):
        transactions = list()
        for t in self.transactions:
            transactions.append(json.dumps(t.to_dict()))

        if method == 'bruteforce':
            nonce = 0
            while self.is_mining:
                if self.validate_nonce(transactions, nonce, difficulty):
                    log.info(f"successfull at {nonce}")
                    self.nonce = nonce
                    self.stop_mining()
                    return nonce
                else:
                    log.debug(f"not successfull at {nonce}")
                nonce += 1

        elif method == 'nonce-skip':
            nonce = self.determine_start_nonce()
            Mapper().write_latest_start_nonce(str(nonce).encode())

            # remove all elements from the nonce_list that are smaller than the starting nonce
            self.nonce_list = list(filter(lambda x: x >= nonce, self.nonce_list))
            index = 0
            iterations = 0
            while self.is_mining:
                # check if the nonce has already been used
                if self.nonce_list and nonce == self.nonce_list[index]:
                    log.info(f"skipped {nonce}")
                    nonce += 1
                    # check if we reached the end of the list
                    if not (index + 1 == len(self.nonce_list)):
                        index += 1
                    continue
                elif self.validate_nonce(transactions, nonce, difficulty):
                    log.info(f"successfull at {nonce}")
                    self.nonce = nonce
                    self.iterations = iterations + 1
                    self.stop_mining()
                    Mapper().append_to_nonce_list(nonce)
                    return nonce
                else:
                    log.debug(f"not successfull at {nonce}")
                nonce += 1
                iterations += 1
                # stop when we reach the limit of a 32-bit integer
                if nonce > 2**32:
                    self.is_mining = False

        elif method == 'multithreading':
            max = 2**32  # use the max value of a 32-bit integer as the limit
            cpus = mp.cpu_count()
            individual_load = int((max/cpus) - (max/cpus) % 1)

            processes = []
            manager = mp.Manager()
            shared_dict = manager.dict()
            shared_dict["nonce"] = None
            shared_dict["finished"] = []
            run = manager.Event()
            run.set()  # We should keep running.

            for i in range(cpus):
                process = mp.Process(target=self.mine_multithreaded,
                                     args=(shared_dict, i, cpus, individual_load+1))
                processes.append(process)

            log.debug(f"Mining with processes {processes}")
            start_time = time.time()
            for proc in processes:
                if shared_dict["nonce"] is None:
                    proc.start()
                else:
                    break
                time.sleep(0.1)

            while True:
                if not self.is_mining:
                    log.warning("mining will be stopped for external reasons")
                    for proc in processes:
                        if proc.is_alive():
                            proc.terminate()
                    break
                elif shared_dict["nonce"] is not None:
                    log.info(f"Found nonce {shared_dict['nonce']}")
                    for proc in processes:
                        if proc.is_alive():
                            proc.terminate()
                    break
                elif len(shared_dict["finished"]) == cpus:
                    log.error("Could not determine nonce with multithreading")
                    break
                else:
                    time.sleep(0.1)
            log.debug(f"Took about {round(time.time() - start_time, 2)} seconds")
            self.stop_mining()
            return shared_dict["nonce"]

    def mine_multithreaded(self, shared_dict, start=0, steps=1, times=1000):
        transactions = list()
        for t in self.transactions:
            transactions.append(json.dumps(t.to_dict()))
        nonce = start

        while self.is_mining:
            # Try with this nonce
            if self.validate_nonce(transactions, nonce):
                log.info(f"successfull at {nonce}")
                shared_dict["nonce"] = nonce
                return nonce
            else:
                log.debug(f"not successfull at {nonce}")
            nonce += steps

    def validate_nonce(self, transactions, nonce, difficulty=4):
        transactions.append(str(nonce))
        mtree = MerkleTree(transactions)
        t_hash = mtree.getRootHash()
        transactions.pop()
        # check the result
        important_digits = t_hash[0:difficulty]
        not_null_digits = important_digits.replace("0", "")

        if len(not_null_digits) == 0:
            return True
        return False
