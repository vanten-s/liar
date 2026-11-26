from scapy.all import Ether, get_if_hwaddr
from scapy.layers.tuntap import TunTapInterface
import socket
import fcntl
import struct
import time

SOCKGETIFFLAG = 0x8913 # SIOCGIFFLAGS 
SOCKSETIFFLAG = 0x8914 # SIOCSIFFLAGS
IFF_UP = 0x1

def bring_interface_up(name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifr = struct.pack("16sH", name.encode(), 0)

    result = fcntl.ioctl(sock.fileno(), SOCKGETIFFLAG, ifr)
    flags = struct.unpack("16sH", result[:18])[1]
    flags |= IFF_UP

    ifr = struct.pack("16sH", name.encode(), flags)
    fcntl.ioctl(sock.fileno(), SOCKSETIFFLAG, ifr)
    
    sock.close()

class NetworkHandler:
    mac_address = "00:00:00:00:00:00"
    def __init__(self, name="RFtap0"):
        self.name = name

        self.tap: TunTapInterface = TunTapInterface(name, mode_tun=False)

        time.sleep(1) # hack interface tar tid att registrera TODO: hitta lösning
        bring_interface_up(self.name)
        self.mac_address = get_if_hwaddr(self.name)

    def poll(self):
        pkt = self.tap.recv()

        if pkt is None or not pkt.haslayer(Ether):
            return
        
        if pkt[Ether].src.lower() == self.mac_address.lower():
            pass

        pkt.show()

        return bytes(pkt)
        
    def get_mac_address(self):
        return self.mac_address


    def close(self):
        if self.tap:
            self.tap.close()
            self.tap = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
