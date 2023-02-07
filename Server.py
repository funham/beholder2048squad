import socket
import cv2
import numpy as np
from enum import Enum
from functools import partialmethod


class ConnType(Enum):
    N = 0   # do Nothing
    O = 1   # just Open
    C = 2   # just Close
    OC = 3  # Open & Close


class Server:
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket()
        self.sock.bind(('', port))
        self.sock.listen()
        self.conn, addr = self.sock.accept()

        print(f'connected to {addr}')

        self.conn.close()

    def recv_int(self, dtype, connType: ConnType = ConnType.OC) -> int:
        data = self.recv_raw(_sizeof(dtype), connType)
        return int.from_bytes(data, byteorder='big')

    def recv_img(self, closeOnExit: bool):
        size = self.recv_int(np.uint64, ConnType.O)
        data = self.recv_arr((size, ), dtype=np.uint8, connType=ConnType.N)
        if closeOnExit:
            self._closeConn(ConnType.C)

        return cv2.imdecode(data, 1)
    

    def recv_arr(self, shape: tuple, dtype=np.int64, connType: ConnType = ConnType.OC) -> np.ndarray:
        size = np.prod(shape)
        data = self.recv_raw(size * _sizeof(dtype),
                             connType=connType, safe=True)
        arr = np.frombuffer(data, dtype=dtype)

        return arr.reshape(shape)

    def recv_raw(self, size: int, connType: ConnType = ConnType.OC, *, safe: bool = False) -> bytes:
        self.conn = self._getConn(connType)
        data = self.conn.recv(size, socket.MSG_WAITALL if safe else 0)
        self._closeConn(connType)

        return data

    def send_raw(self, data: bytes, connType: ConnType = ConnType.OC) -> None:
        self.conn = self._getConn(connType)
        self.conn.sendall(data)
        self._closeConn(connType)

    def send_str(self, string: str, connType: ConnType = ConnType.OC) -> None:
        self.send_raw(string.encode(encoding='utf-8'), connType)

    def _getConn(self, connType: ConnType) -> socket.socket:
        if connType in (ConnType.O, ConnType.OC):
            self.sock.listen()
            conn, addr = self.sock.accept()
            return conn

        return self.conn

    def _closeConn(self, connType: ConnType) -> None:
        if connType in (ConnType.C, ConnType.OC):
            self.conn.close()

    chat_img = partialmethod(recv_img, closeOnExit=False)
    chat_cmd = partialmethod(send_str, connType=ConnType.C)

def _sizeof(dtype):
    return np.array([], dtype=dtype).itemsize


if __name__ == '__main__':

    serv = Server(9090)

    while True:
        frame = serv.recv_img(closeOnExit=False)

        cv2.imshow('recieved', frame)

        command = 's 90'
        serv.send_str(command, ConnType.C)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
