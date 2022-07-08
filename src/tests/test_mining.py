'''
Test functions to test different approaches/algorithms to find a nonce for a block
Used to determine which approach has the least overall hash iterations

run with 'python -m unittest' in the src/ directory
individual tests can be run with e.g.:
'python -m unittest tests.test_mining.TestMining.test_mine_with_bruteforce'
'''

import logging
from unittest import TestCase
from datetime import datetime
from ecdsa import SigningKey, SECP256k1
from hashlib import sha256

# local imports
from blockchain.block import Transaction
from blockchain.block import Block

logging.disable(logging.CRITICAL)   # disable all logging from main.py


class TestMining(TestCase):

    DIFFICULTY = 4
    NO_OF_BLOCKS = 50
    print(f'test for {NO_OF_BLOCKS} blocks with difficulty {DIFFICULTY}')

    def test_mine_with_bruteforce(self):
        ''' Find the nonce for each block using bruteforce '''

        all_iterations = []
        start = datetime.now()  # FIXME this is inaccurate, but is enough to get a rough estimation

        for i in range(self.NO_OF_BLOCKS):
            tx = Transaction('bob', 'alice', float(i), datetime(2022, 1, 1, 0, 0, 0))
            tx_hash = tx.hash()
            private_key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
            pubkey = private_key.get_verifying_key()
            sig = private_key.sign(tx_hash.encode("utf-8"))
            tx.set_pubkey(pubkey)
            tx.set_signature(sig)

            block = Block(transactions=[tx])    # put the tx in a block and mine it
            iterations = block.find_nonce(difficulty=self.DIFFICULTY, method='bruteforce')
            all_iterations.append(iterations)

        print("Average iterations for bruteforce:\t", sum(all_iterations) / len(all_iterations))
        print(f"took {datetime.now() - start}")

    def test_mine_with_nonce_skipping(self):
        ''' Find the nonce and the number of iterations for each block by skipping prev. nonces '''
        all_iterations = []
        start = datetime.now()

        for i in range(self.NO_OF_BLOCKS):
            tx = Transaction('bob', 'alice', float(i), datetime(2022, 1, 1, 0, 0, 0))
            tx_hash = tx.hash()
            private_key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
            pubkey = private_key.get_verifying_key()
            sig = private_key.sign(tx_hash.encode("utf-8"))
            tx.set_pubkey(pubkey)
            tx.set_signature(sig)

            block = Block(transactions=[tx])    # put the tx in a block and mine it
            block.find_nonce(difficulty=self.DIFFICULTY, method='nonce-skip')
            all_iterations.append(block.iterations)

        print("Average iterations for nonce-skip:\t", sum(all_iterations) / len(all_iterations))
        print(f"took {datetime.now() - start}")
