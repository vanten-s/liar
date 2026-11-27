from network import FramedSocket
import backend
HOST = "127.0.0.1"
PORT = 13371

with FramedSocket.listen(HOST, PORT) as server:
    print("Listening...")

    backend.mainloop()
    
    client, address = server.accept()
    with client:
        while True:
            data = client.recv()
            backend.mod_queue.put(data)
            client.send(backend.demod_queue.get())