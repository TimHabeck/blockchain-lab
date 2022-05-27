from .message import Message
from blockchain.block import Block


class Blocks(Message):
    def __init__(self, blocks, info=None) -> None:
        super().__init__()
        self._name = "blocks"
        self._blocks = blocks
        self._info = info

    def get_blocks(self):
        return self._blocks

    def set_blocks(self, blocks):
        self._blocks = blocks

    def get_info(self):
        return self._info

    def set_info(self, info):
        self._info = info

    def to_dict(self):
        blocks = []
        for block in self.get_blocks():
            if isinstance(block, Block):
                blocks.append(block.to_dict_with_hash())

        return {
            "name": self.get_name(),
            "blocks": blocks,
            "info": self.get_info()
        }

    @staticmethod
    def from_dict(dict):
        block_message = Blocks(dict["blocks"], dict["info"])
        blocks = []
        for block in block_message.get_blocks():
            blocks.append(Block.from_dict(block, block["hash"]))
        block_message.set_blocks(blocks)
        return block_message
