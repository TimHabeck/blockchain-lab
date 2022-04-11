from .message import Message


class Prepare_to_validate(Message):
    def __init__(self, transaction) -> None:
        super().__init__()
        self._name = "prepare-to-validate"
        self._transaction = transaction

    def get_transaction(self):
        return self._transaction

    def set_transaction(self, transaction):
        self._transaction = transaction

    def to_dict(self):
        return {
            "name": self.get_name(),
            "transaction": self.get_transaction(),
        }

    @staticmethod
    def from_dict(dict):
        return Prepare_to_validate(dict["transaction"])
