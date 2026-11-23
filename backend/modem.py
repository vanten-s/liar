import numpy as np
import scipy.signal

SAMPLE_RATE = 48000 # Samples per secondmode
BAUD_RATE = 300 # Symbols per second
SAMPLES_PER_SYMBOL = SAMPLE_RATE // BAUD_RATE # Samples per Symbol

FREQUENCIES = (1200, 1500, 1800, 2100)

# One "sync" symbols, then one symbol silence
def create_sync_signal() -> np.ndarray:
    samples: np.ndarray = np.zeros(2 * SAMPLES_PER_SYMBOL)
    for i in range(SAMPLES_PER_SYMBOL * 1, SAMPLES_PER_SYMBOL * 2):
        samples[i] = np.sin(900 * 2 * np.pi * i / SAMPLE_RATE)
        
    return samples

def modulate(data_bytes: bytes) -> np.ndarray:
    data = np.array(list(data_bytes), dtype=np.uint8) 

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

        return 0.5 * np.sin(FREQUENCIES[bit0 + bit1] * 2 * np.pi * n / SAMPLE_RATE)
    
    samples = np.array([get_sample(sample_number) for sample_number in samples])
    sync_signal = create_sync_signal()

    return np.concatenate((np.zeros(80), sync_signal, samples))

def demodulate(audio: np.ndarray) -> bytes:
    # To get our starting index, we need to find the sync signal
    # We do this by convolving a sync signal over our received signal and finding the maximum

    sync_signal = create_sync_signal()
    convolved = scipy.signal.convolve(audio, sync_signal, mode='valid')
    shift = np.argmax(abs(convolved)) - 161 + len(sync_signal) + 80

    window_size = 160
    SFT = scipy.signal.ShortTimeFFT(np.ones(window_size), hop=160, fs=SAMPLE_RATE)
    Sx = SFT.stft(audio[shift:]) # frequency = n * sample_rate / window_size
    # n = frequency / (sample_rate / window_size) = window_size * frequency / sample_rate
    data = []
    current_bit = 0
    for i in range(0, Sx.shape[1]):
        symbol = np.argmax(abs(Sx[...,i])) - 4
        
        if current_bit % 8 == 0:
            data.append(0)

        if symbol < 0 or symbol > 3:
            current_bit += 2
            continue

        data[current_bit // 8] |= (symbol << (current_bit % 8))
        current_bit += 2

    return bytes(data)





