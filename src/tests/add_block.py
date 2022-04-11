from src.blockchain.block import Transaction
from src.blockchain.blockchain import Blockchain

transactions = [Transaction("Justus", "Jonas", 10.0),
                Transaction("Bernd", "Harald", 5.0)]
blockchain = Blockchain()
blockchain.add_block(transactions)
