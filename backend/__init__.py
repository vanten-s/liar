from .io_handler import AudioInput, AudioOutput, AudioOpener, AudioSaver
from .modem import demodulate, modulate, is_sync_signal, create_sync_signal
from .modem import SAMPLES_PER_SYMBOL
from queue import Queue
import numpy as np
import threading

CHUNK = len(create_sync_signal())
running = True
receiving = False

mod_queue: Queue[bytes] = Queue()
demod_queue: Queue[bytes] = Queue()

def mainloop(modulate: bool = True, demodulate: bool = True):
    global mod_queue, demod_queue

    out_stream = AudioSaver("signal.wav")
    in_stream = AudioOpener("signal.wav")

    if modulate:
        mod_thread = threading.Thread(target=modulation_loop, args=[out_stream])
        mod_thread.start()

    if demodulate:
        demod_thread = threading.Thread(target=demodulation_loop, args=[in_stream])
        demod_thread.start()

def modulation_loop(stream: AudioOutput):
    global mod_queue
    with stream:
        while running:
            message = mod_queue.get()
            modulated = modulate(message)
            stream.write(modulated)

def demodulation_loop(stream: AudioInput):
    with stream:
        previous_chunk = np.zeros(CHUNK//2)
        while running:
            chunk = stream.read(CHUNK//2)

            shift, amplitude, average = is_sync_signal(np.concat((previous_chunk, chunk)))

            previous_chunk = chunk

            if amplitude > 3: 
                _empty = stream.read(shift) # Read enough bytes to receive the last of the message

            else:
                continue

            chunk = stream.read(2 * 4 * SAMPLES_PER_SYMBOL)

            length = int.from_bytes(demodulate(chunk), 'little')

            if length == 0: 
                continue

            chunk = stream.read(CHUNK * length)

            message = demodulate(chunk)
            demod_queue.put(message)
            print(message)
            print("Listening...")

