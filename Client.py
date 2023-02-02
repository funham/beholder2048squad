import socket
import numpy as np
import cv2

from Server import ConnType


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.connect((host, port))

        print(f'connected to {host}:{port}')

        self.sock.close()

    def send_raw(self, msg, connType: ConnType = ConnType.OC) -> None:
        self.sock = self._getConn(connType)
        self.sock.sendall(msg)
        self._closeConn(connType)

    def recv_raw(self, length=1024, connType: ConnType = ConnType.OC) -> bytes:
        self.sock = self._getConn(connType)
        data = self.sock.recv(length)
        self._closeConn(connType)

        return data

    def recv_str(self, connType: ConnType = ConnType.OC) -> str:
        return self.recv_raw(length=1024, connType=connType).decode('utf-8', 'strict')

    def send_img(self, img, quality=90, closeOnExit: bool = True) -> None:
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), quality)
        res, data = cv2.imencode('.jpg', img, encode_param)
        data = data.tobytes()
        size = len(data)
        self.send_raw(size.to_bytes(8, 'big'), ConnType.O)
        self.send_raw(data, ConnType.N)

    def _getConn(self, connType: ConnType) -> socket.socket:
        if connType in (ConnType.O, ConnType.OC):
            sock = socket.socket()
            sock.connect((self.host, self.port))
            return sock

        return self.sock

    def _closeConn(self, connType: ConnType) -> None:
        if connType in (ConnType.C, ConnType.OC):
            self.sock.close()


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    client = Client('192.168.95.46', 9090)
    # client = Client('192.168.95.141', 9090)

    while True:
        res, frame = cap.read()
        frame = cv2.flip(frame, 1)

        cv2.imshow('sent', frame)

        if cv2.waitKey(1) == ord('q'):
            break

        client.send_img(frame, quality=90, closeOnExit=False)

        command = client.recv_str(ConnType.C)
        print(command)

    cv2.destroyAllWindows()
