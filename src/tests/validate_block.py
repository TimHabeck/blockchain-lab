from src.blockchain.block import Transaction, Block
from src.blockchain.blockchain import Blockchain
import time

blockchain = Blockchain()
transactions = [Transaction("Leon", "Timme", 10.0),
                Transaction("Leon", "Jan", 50.0)]
blockchain.add_block(transactions)
time.sleep(1)

transactions2 = [Transaction("Timme", "Leon", 30.0),
                 Transaction("Jan", "Leon", 80.0)]
blockchain2 = Blockchain()
blockchain2.add_block(transactions2)
time.sleep(1)

transactions3 = [Transaction("Jan", "Timme", 10.0),
                 Transaction("Timme", "Jan", 50.0)]
blockchain3 = Blockchain()
blockchain3.add_block(transactions3)

# Jan: 110
# Timme: 40
# Leon: 150
time.sleep(1)
transactions4 = [Transaction("Timme", "Leon", 50.0)]
block = Block("123", transactions4)
block.saved_hash = block.hash()
print("assert: False ")
print(block.validate())

time.sleep(1)
transactions5 = [Transaction("Timme", "Leon", 40.0)]
block = Block("123", transactions5)
block.saved_hash = block.hash()
print("assert: True ")
print(block.validate())

time.sleep(1)
transactions6 = [Transaction("Jan", "Leon", 110.1)]
block = Block("123", transactions6)
block.saved_hash = block.hash()
print("assert: False ")
print(block.validate())

time.sleep(1)
transactions7 = [Transaction("Jan", "Leon", 109.9)]
block = Block("123", transactions7)
block.saved_hash = block.hash()
print("assert: True ")
print(block.validate())

time.sleep(1)
transactions8 = [Transaction("Leon", "Jan", 115659.9)]
block = Block("123", transactions8)
block.saved_hash = block.hash()
print("assert: False ")
print(block.validate())

time.sleep(1)
transactions9 = [Transaction("Leon", "Jan", 0.79)]
block = Block("123", transactions9)
block.saved_hash = block.hash()
print("assert: True ")
print(block.validate())
