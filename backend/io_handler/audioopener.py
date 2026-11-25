from .audioinput import AudioInput
import wave
import numpy as np

class AudioOpener(AudioInput):
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        self.wf = wave.open(self.filename, mode="rb")
        return self

    def read(self, num_samples: int) -> np.ndarray:
        frames = self.wf.readframes(num_samples)
        width = self.wf.getsampwidth()
        samples = []
        for i in range(0, len(frames), width):
            samples.append(int.from_bytes(frames[i:i+width], 'little', signed=True) / (2**(width*8)))

        return np.array(samples)
    
    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        self.wf.close()

