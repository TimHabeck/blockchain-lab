from abc import ABC


class Message(ABC):
    def __init__(self) -> None:
        self._name = None

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def to_dict(self):
        pass

    @staticmethod
    def from_dict():
        pass
