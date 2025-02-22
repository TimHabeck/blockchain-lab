#!/usr/bin/env python3

import os
import logging
import argparse
from Crypto.PublicKey import RSA
from network.node import P2PNode
from ecdsa import SigningKey, SECP256k1
from hashlib import sha256
from blockchain.block import Transaction
from blockchain.blockchain import Blockchain


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port',
        '-p',
        dest='port',
        type=int,
        help='Port on which to start the node (default: 80)',
        default=80
    )
    parser.add_argument(
        '--debug',
        dest='debug',
        help='Enable debug logging',
        action='store_true'
    )
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s %(levelname)-8s[%(filename)s %(funcName)s(): "
                        "%(lineno)s] %(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger()
    if args.debug:
        log.setLevel(logging.DEBUG)

    # start node
    node = P2PNode("127.0.0.1", args.port, args.port, max_connections=3)
    node.start_up()

    if not os.path.exists('db/keys'):
        os.mkdir("db/keys")

    if not os.path.exists('db/keys/private_key.pem') \
            or not os.path.exists('db/keys/public_key.pem'):
        # generate keys
        key = RSA.generate(2048)
        private_key = key.export_key()
        with open("db/keys/private_key.pem", "wb") as file:
            file.write(private_key)

        public_key = key.publickey().export_key()
        with open("db/keys/public_key.pem", "wb") as file:
            file.write(public_key)

        print(public_key.decode('ASCII'))

    possible_inputs = ['s', 'S', 't', 'T']
    user_input = ''
    while user_input not in possible_inputs:
        user_input = input("(s)\tstop the node\n(t)\tcreate transactions, "
                           "put them in a block and broadcast it to the network\n")

        if user_input == 's':
            node.stop()

        elif user_input == 't':
            transactions = []
            create_transactions = True
            while create_transactions:
                print("create a transaction:")
                source = input("type the sender: \n")
                target = input("type the receiver: \n")
                amount = input("type the amount: \n")

                transaction = Transaction(source, target, float(amount))
                tx_hash = transaction.hash()
                log.debug(f"Created transaction {transaction.to_dict()}")
                log.debug(f"Hash of transaction is {tx_hash}")

                # generate an ECDSA keypair for each transaction
                private_key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
                pubkey = private_key.get_verifying_key()
                # sign the transaction hash with the private key
                sig = private_key.sign(tx_hash.encode("utf-8"))

                # add the pubkey and the signature to the transaction
                transaction.set_pubkey(pubkey)
                transaction.set_signature(sig)
                log.debug("Created ECDSA keypair and signature")

                transactions.append(transaction)
                answer = input("do you want to create another transaction? (y/n)\n")
                if answer == 'y':
                    continue
                else:
                    create_transactions = False

            answer = input("type 'go' to create a block, append it to your blockchain "
                           "and broadcast it to the network \n")
            if answer == 'go':
                blockchain = Blockchain()
                blockchain.add_block(transactions, node)
            user_input = ''
