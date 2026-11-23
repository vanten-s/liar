from frontend import NetworkHandler
from backend.io_handler import AudioSaver, AudioOpener 
from backend.modem import demodulate, modulate

def mainloop(Net):
    while True:
        message = Net.poll()
        if message is None:
            continue
        signal = modulate(message)

        with AudioSaver() as stream:
            stream.write(signal)

        with AudioOpener() as stream:
            audio = stream.read()
            print(demodulate(audio))

with NetworkHandler() as Net:
    mainloop(Net)