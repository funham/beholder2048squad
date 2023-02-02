import socket
import cv2
import numpy as np


class Server:
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket()
        self.sock.bind(('', port))
        self.sock.listen()
        conn, addr = self.sock.accept()

        print(f'connected to {addr}')

        conn.close()

    def recv_int(self, dtype) -> int:
        data = self.recv_raw(_sizeof(dtype))
        return int.from_bytes(data, byteorder='big')

    def recv_img(self) -> cv2.Mat:
        size = self.recv_int(np.uint64)
        data = self.recv_arr((size, ), dtype=np.uint8)

        return cv2.imdecode(data, 1)

    def recv_arr(self, shape: tuple, dtype=np.int64) -> np.ndarray:
        size = np.prod(shape)
        data = self.recv_raw(size * _sizeof(dtype), safe=True)
        arr = np.frombuffer(data, dtype=dtype)

        return arr.reshape(shape)

    def recv_raw(self, size: int, *, safe: bool = False) -> bytes:
        self.sock.listen()
        conn, addr = self.sock.accept()
        data = conn.recv(size, socket.MSG_WAITALL if safe else 0)
        conn.close()

        return data

    def send_raw(self, data: bytes) -> None:
        self.sock.listen()
        conn, addr = self.sock.accept()
        conn.sendall(data)
        conn.close()

    def send_str(self, string: str) -> None:
        self.send_raw(string.encode(encoding='utf-8'))


def _sizeof(dtype):
    return np.array([], dtype=dtype).itemsize


if __name__ == '__main__':

    serv = Server(9090)

    while True:
        frame = serv.recv_img()

        cv2.imshow('frame', frame)

        command = 's 90'
        serv.send_str(command)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
