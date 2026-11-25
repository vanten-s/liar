import datetime
import numpy as np
import scipy.signal

from .io_handler.audiosaver import AudioSaver

SAMPLE_RATE = 48000 # Samples per secondmode
BAUD_RATE = 300 # Symbols per second
FREQUENCY_SHIFT =  4
SAMPLES_PER_SYMBOL = SAMPLE_RATE // BAUD_RATE # Samples per Symbol

def frequency(symbol: int) -> float:
    if symbol > 3 or symbol < 0:
        raise ValueError("Woops, symbol is out of range")

    return (symbol + FREQUENCY_SHIFT) * BAUD_RATE

# One "sync" symbols, then three symbol silence
def create_sync_signal() -> np.ndarray:
    samples: np.ndarray = np.zeros(8 * SAMPLES_PER_SYMBOL)
    # "Sync" symbol is a frequency chirp from 0 -> 3 * BAUD_RATE
    for i in range(0, SAMPLES_PER_SYMBOL * 4):
        progress = 3 * i / (SAMPLES_PER_SYMBOL * 4) # Goes from 0 -> 3
        samples[i] = np.sin(progress * BAUD_RATE * 2 * np.pi * i / SAMPLE_RATE)

    return samples

def modulate(data_bytes: bytes) -> np.ndarray:
    data = np.array(list(data_bytes), dtype=np.uint8) 
    length_enoded = np.array(list(len(data_bytes).to_bytes(2, 'little')), dtype=np.uint8)
    data = np.concat((length_enoded, data))

    length: int = data.shape[0] * 4

    n_samples = np.ceil(length * SAMPLES_PER_SYMBOL)
    samples: np.ndarray = np.arange(n_samples)

    def get_sample(n):
        if data.dtype != np.uint8:
            print("WRONG DATA TYPE")
            raise TypeError("Wrong Data Type")

        current_symbol = int(n // SAMPLES_PER_SYMBOL)
        current_index = int(current_symbol // 4)
        current_bit = 2 * (current_symbol % 4)

        bit0 = 0 if data[current_index] & (1 << current_bit) == 0 else 1
        bit1 = 0 if data[current_index] & (1 << (current_bit + 1)) == 0 else 2

        return np.sin(frequency(bit0 + bit1) * 2 * np.pi * n / SAMPLE_RATE)
    
    samples = np.array([get_sample(sample_number) for sample_number in samples])
    sync_signal = create_sync_signal() # Syncing signal to make sure receiver can decode signal
    padding = np.zeros(20 * 4 * SAMPLES_PER_SYMBOL) # To make sure ALSA doesn't underrun

    return np.concatenate((padding, sync_signal, samples))

def demodulate(audio: np.ndarray) -> bytes:
    # To get our starting index, we need to find the sync signal
    # We do this by convolving a sync signal over our received signal and finding the maximum
    window_size = SAMPLES_PER_SYMBOL
    SFT = scipy.signal.ShortTimeFFT(np.ones(window_size), hop=SAMPLES_PER_SYMBOL, fs=SAMPLE_RATE)
    Sx = SFT.stft(audio[(SAMPLES_PER_SYMBOL//2):]) 
    # frequency = n * sample_rate / window_size
    # n = frequency / (sample_rate / window_size) = window_size * frequency / sample_rate
    data = []
    current_bit = 0
    for i in range(0, Sx.shape[1]):
        symbol = np.argmax(abs(Sx[...,i])) - FREQUENCY_SHIFT
        
        if current_bit % 8 == 0:
            data.append(0)

        if symbol < 0 or symbol > 3:
            current_bit += 2
            continue

        data[current_bit // 8] |= (symbol << (current_bit % 8))
        current_bit += 2

    return bytes(data)

def is_sync_signal(audio: np.ndarray) -> tuple[int, float, float]:
    sync_signal = np.flip(create_sync_signal())
    
    amplitude = np.sqrt(np.sum(audio * audio))

    convolved = scipy.signal.convolve(audio, sync_signal)
    max_index = np.argmax(np.sqrt(abs(convolved)))

    if amplitude > 0:
        max_value = convolved[max_index]

    else:
        max_value = 0

    shift = max_index - len(sync_signal)

    if shift < 0:
        shift = 0

    return (int(shift), max_value, amplitude)

