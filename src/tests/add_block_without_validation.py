from src.blockchain.block import Transaction
from src.blockchain.blockchain import Blockchain

transactions = [Transaction("Jan", "Timme", 1000.0),   # invalid
                Transaction("Timme", "Max", 5.0)]
blockchain = Blockchain()
blockchain.add_block_without_validation(transactions)
