from .message import Message


class Get_blocks(Message):
    def __init__(self, latest_block_hash) -> None:
        super().__init__()
        self._name = "get-blocks"
        self._latest_block_hash = latest_block_hash

    def get_latest_block_hash(self):
        return self._latest_block_hash

    def set_latest_block_hash(self, latest_block_hash):
        self._latest_block_hash = latest_block_hash

    def to_dict(self):
        return {
            "name": self.get_name(),
            "latest_block_hash": self.get_latest_block_hash()
        }

    @staticmethod
    def from_dict(dict):
        return Get_blocks(dict["latest_block_hash"])
