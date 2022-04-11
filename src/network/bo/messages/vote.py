from .message import Message


class Vote(Message):
    def __init__(self, valid) -> None:
        super().__init__()
        self._name = "vote"
        self._valid = valid

    def get_valid(self):
        return self._valid

    def set_valid(self, valid):
        self._valid = valid

    def to_dict(self):
        return {
            "name": self.get_name(),
            "valid": self.get_valid(),
        }

    @staticmethod
    def from_dict(dict):
        return Vote(dict["valid"])
