from typing_extensions import Protocol


class CardVerifierInterface(Protocol):
    def verify(self, idm: str) -> bool:
        ...
