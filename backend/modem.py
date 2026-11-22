import numpy as np
import scipy.signal
from scipy.signal.windows import gaussian
import matplotlib.pyplot as plt

SAMPLE_RATE = 48000 # Samples per second
BAUD_RATE = 300 # Symbols per second
SAMPLES_PER_SYMBOL = SAMPLE_RATE / BAUD_RATE # Samples per Symbol

FREQUENCIES = (1200, 1500, 1800, 2100)

def modulate(data_bytes: bytes) -> np.ndarray:
    data = np.array(list(data_bytes), dtype=np.uint8) 

    length = data.shape[0] * 4
    n_samples = np.ceil(SAMPLE_RATE * length / BAUD_RATE)
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

        return np.sin(FREQUENCIES[bit0 + bit1] * 2 * np.pi * n / SAMPLE_RATE)
    
    samples = np.array([get_sample(sample_number) for sample_number in samples])
    return samples

def demodulate(audio: np.ndarray) -> bytes:
    window_size = 160
    SFT = scipy.signal.ShortTimeFFT(np.ones(window_size), hop=80, fs=SAMPLE_RATE)
    Sx = SFT.stft(audio) # frequency = n * sample_rate / window_size
    # n = frequency / (sample_rate / window_size) = window_size * frequency / sample_rate
    data = []
    current_bit = 0
    for i in range(0, Sx.shape[1]):
        if i % 2 == 0:
            continue

        symbol = np.argmax(abs(Sx[...,i])) - 4
        
        if current_bit % 8 == 0:
            data.append(0)

        data[current_bit // 8] |= (symbol << (current_bit % 8))

        current_bit += 2

    return bytes(data)

