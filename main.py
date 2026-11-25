from frontend import NetworkHandler
import backend

def mainloop(Net: NetworkHandler):
    backend.mainloop()
    while True:
        message = Net.poll()
        if message is None:
            continue

        backend.mod_queue.put(message)

with NetworkHandler() as Net:
    mainloop(Net)

