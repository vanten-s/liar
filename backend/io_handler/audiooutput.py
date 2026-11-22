from abc import abstractmethod
import numpy as np

class AudioOutput:
    @abstractmethod
    def __enter__(self) -> AudioOutput:
        pass

    @abstractmethod
    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        pass

    @abstractmethod
    def write(self, signal: np.ndarray):
        pass


