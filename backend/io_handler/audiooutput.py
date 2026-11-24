from abc import abstractmethod
from typing import Self
import numpy as np

class AudioOutput:
    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        pass

    @abstractmethod
    def write(self, signal: np.ndarray):
        pass


