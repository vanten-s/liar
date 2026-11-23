from io_handler import AudioSaver, AudioOpener 
from modem import demodulate, modulate

CHUNK = 512

def mainloop():
    message = "test test 123"
    signal = modulate(message.encode('utf-8'))
  
    with AudioSaver() as stream:
        stream.write(signal)

    with AudioOpener() as stream:
        audio = stream.read()
        print(demodulate(audio).decode('utf-8', errors='ignore'))

if __name__ == "__main__":
    mainloop()

