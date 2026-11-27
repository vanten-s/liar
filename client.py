from network import FramedSocket
from frontend import NetworkHandler

HOST = "127.0.0.1"
PORT = 13371

with NetworkHandler as Net:
    with FramedSocket.connect(HOST, PORT) as client:
        while True:
            message = Net.poll()
            if message is None:
                continue
            client.send(message)
            new_message = client.recv()
            Net.pinject(new_message)
            