from .audioinput import AudioInput
import numpy as np
import pyaudio

class AudioListener(AudioInput):
    def __init__(self):
        pass

    def __enter__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(48000, 1, pyaudio.paInt32, input=True)
        return self

    def read(self, num_samples: int) -> np.ndarray:
        bytes_read = self.stream.read(num_samples)
        
        samples = []
        
        for i in range(0, num_samples):
            samples.append(int.from_bytes(bytes_read[4*i:4*(i+1)], 'little', signed=True) / 2**32)

        return np.array(samples)

    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        self.stream.close()
        self.p.terminate()

