from typing import List

from .types import NormalizedMessage


class InMemoryMessageStore:
    def __init__(self) -> None:
        self._messages: List[NormalizedMessage] = []

    def save(self, msg: NormalizedMessage) -> None:
        self._messages.append(msg)

    def all(self) -> List[NormalizedMessage]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()


store = InMemoryMessageStore()

