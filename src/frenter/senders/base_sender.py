from typing import Dict
from abc import abstractmethod


class BaseSender:

    @staticmethod
    def _dict_to_str(content: Dict) -> str:
        return "".join([f"{key}: {value}\n" for key, value in content.items()])

    def send(self, content: Dict):
        return self._send(self._dict_to_str(content))

    @abstractmethod
    def _send(self, message: str):
        raise NotImplementedError()
