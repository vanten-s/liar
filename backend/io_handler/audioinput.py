from abc import abstractmethod
from typing import Self

class AudioInput:
    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        pass

    @abstractmethod
    def read(self) -> bytes:
        pass

