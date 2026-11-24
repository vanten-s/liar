from .io_handler import AudioSaver, AudioOpener
from .modem import demodulate, modulate, is_sync_signal
from .modem import SAMPLES_PER_SYMBOL
from queue import Queue
import numpy as np
import threading
import pyaudio

CHUNK = 4 * SAMPLES_PER_SYMBOL
running = True
receiving = False

mod_queue: Queue[bytes] = Queue()
demod_queue: Queue[bytes] = Queue()

def raw2float(audio: bytes) -> np.ndarray:
    length = len(audio)
    if length % 4 != 0:
        raise ValueError("Audio must be 32-bit")

    samples = []
    for i in range(0, length // 4):
        samples.append(int.from_bytes(audio[4*i:4*(i+1)], 'little', signed=True) / 2**32)

    return np.array(samples)

def float2raw(audio: np.ndarray) -> bytes:
    raw = []
    for sample in audio:
        raw.extend(round(0.9 * 2**31 * sample).to_bytes(4, 'little', signed=True))

    return bytes(raw)

def mainloop(modulate: bool = True, demodulate: bool = True):
    global mod_queue, demod_queue
    p = pyaudio.PyAudio()

    out_stream = p.open(48000, 1, pyaudio.paInt32, output=True)
    in_stream = p.open(48000, 1, pyaudio.paInt32, input=True)

    if modulate:
        mod_thread = threading.Thread(target=modulation_loop, args=[out_stream])
        mod_thread.start()

    if demodulate:
        demod_thread = threading.Thread(target=demodulation_loop, args=[in_stream])
        demod_thread.start()

def modulation_loop(stream: pyaudio.Stream):
    global mod_queue
    while running:
        message = mod_queue.get()
        modulated = modulate(message)
        stream.write(float2raw(modulated))

def demodulation_loop(stream: pyaudio.Stream):
    previous_chunk = np.zeros(CHUNK//2)
    while running:
        chunk = raw2float(stream.read(CHUNK//2))

        shift, amplitude = is_sync_signal(np.concat((previous_chunk, chunk)))

        previous_chunk = chunk

        if amplitude > 6: 
            with AudioSaver("sync.wav") as s:
                s.write(chunk)

            test = stream.read(shift) # Read enough bytes to receive the last of the message
            with AudioSaver("empty.wav") as s:
                s.write(raw2float(test))

        else:
            continue

        chunk = raw2float(stream.read(CHUNK))

        with AudioSaver("testAudio.wav") as s:
            s.write(chunk)

        length = demodulate(chunk)[0]

        if length == 0: continue

        chunk = raw2float(stream.read(CHUNK * length))

        with AudioSaver("dataAudio.wav") as s:
            s.write(chunk)

        message = demodulate(chunk)
        demod_queue.put(message)
        print(message.decode('utf-8', errors='ignore'))

