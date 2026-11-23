from frontend import NetworkHandler

with NetworkHandler() as Net:
    mac_address = Net.get_mac_address()
    print(mac_address)
    while True:
        Net.poll()