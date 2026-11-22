from abc import abstractmethod

class AudioInput:
    @abstractmethod
    def __enter__(self) -> AudioInput:
        pass

    @abstractmethod
    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        pass

    @abstractmethod
    def read(self) -> bytes:
        pass

