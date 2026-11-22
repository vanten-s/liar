from io_handler.audiooutput import AudioOutput
import numpy as np
import wave
import itertools

class AudioSaver(AudioOutput):
    def __init__(self):
        pass

    def __enter__(self):
        self.wf = wave.open("audio.wav", mode="wb")
        self.wf.setnchannels(1)
        self.wf.setframerate(48000)
        self.wf.setsampwidth(4)
        return self

    def write(self, signal: np.ndarray):
        data = bytes(itertools.chain.from_iterable([list(round((2**31) * (0.9 * a)).to_bytes(4, 'little', signed=True)) for a in signal]))
        self.wf.writeframes(data)
    
    def __exit__(self, _exc_type, _exc_value, _exc_traceback):
        self.wf.close()

