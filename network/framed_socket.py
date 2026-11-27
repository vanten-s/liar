import socket
import struct

# protocol [u32][u8[#]]
# [len][data]

# TODO: don't trust user submitted length "recvall"

class FramedSocket:
    def __init__(self, sock: socket.socket):
        self._sock = sock

    @classmethod
    def listen(cls, host: str, port: int, backlog: int = 5):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(backlog)
        return cls(sock)

    @classmethod
    def connect(cls, host: str, port: int):
        sock = socket.create_connection((host, port))
        return cls(sock)

    def accept(self):
        client_sock, address = self._sock.accept()
        return FramedSocket(client_sock), address

    def _recvall(self, num_bytes: int) -> bytes:
        data = bytearray()
        while len(data) < num_bytes:
            chunk = self._sock.recv(num_bytes - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return bytes(data)

    def recv(self) -> bytes | None:
        raw_header = self._recvall(4)
        if not raw_header:
            return None
        msg_len = struct.unpack("!I", raw_header)[0]
        return self._recvall(msg_len)

    def send(self, data: bytes) -> None:
        msg_header = struct.pack("!I", len(data))
        self._sock.sendall(msg_header + data)

    def close(self) -> None:
        self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()