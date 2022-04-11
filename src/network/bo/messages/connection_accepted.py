from .message import Message


class Connection_accepted(Message):
    def __init__(self) -> None:
        super().__init__()
        self._name = "connection-accepted"

    def to_dict(self):
        return {
            "name": self.get_name()
        }

    @staticmethod
    def from_dict():
        return Connection_accepted()
