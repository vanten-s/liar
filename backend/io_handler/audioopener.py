from io_handler.audioinput import AudioInput
import wave
import numpy as np

class AudioOpener(AudioInput):
    def __init__(self):
        pass

    def __enter__(self):
        self.wf = wave.open("audio.wav", mode="rb")
        return self

    def read(self) -> np.ndarray:
        frames = self.wf.readframes(self.wf.getnframes())
        width = self.wf.getsampwidth()
        samples = []
        for i in range(0, len(frames), width):
            samples.append(int.from_bytes(frames[i:i+width], 'little', signed=True) / (2**(width*8)))

        return np.array(samples)
    
    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        self.wf.close()

