import pyaudio
from io_handler.audiooutput import AudioOutput
import numpy as np
import itertools

class AudioPlayer(AudioOutput):
    CHUNK = 512

    def __init__(self):
        pass

    def __enter__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(48000, 1, pyaudio.paInt32, output=True)
        return self

    def write(self, signal: np.ndarray):
        data = bytes(itertools.chain.from_iterable([list(round((2**31) * (0.9 * a)).to_bytes(4, 'little', signed=True)) for a in signal]))

        data_length = len(data)
        current_index = 0

        while current_index + self.CHUNK < data_length:
            self.stream.write(data[current_index:current_index + self.CHUNK])
            current_index += self.CHUNK

        self.stream.write(data[current_index:])

    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        self.stream.close()
        self.p.terminate()

