from .message import Message
from src.blockchain.block import Block
import sys
sys.path.append("..")


class Block_message(Message):
    def __init__(self, block) -> None:
        super().__init__()
        self._name = "block"
        self._block = block

    def get_block(self):
        return self._block

    def set_block(self, block):
        self._block = block

    def to_dict(self):
        return {
            "name": self.get_name(),
            "block": self.get_block().to_dict_with_hash()
        }

    @staticmethod
    def from_dict(dict):
        block = Block.from_dict(dict["block"], dict["block"]["hash"])
        return Block_message(block)
