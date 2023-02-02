import socket
import numpy as np
import cv2

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        sock = socket.socket()
        sock.connect((host, port))

        print(f'connected to {host}:{port}')
        
        sock.close()
    
    def send(self, msg) -> None:
        sock = socket.socket()
        sock.connect((self.host, self.port))
        sock.sendall(msg)
        sock.close()
        
    
    def recv(self, length=1024) -> bytes:
        sock = socket.socket()
        sock.connect((self.host, self.port))      
        data = sock.recv(length)
        sock.close()
        
        return data
    
    def recv_str(self) -> str:
        return self.recv().decode('utf-8', 'strict')
    
    def send_img(self, img, quality=90) -> None:
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), quality)
        res, data = cv2.imencode('.jpg', img, encode_param)
        data = data.tobytes()
        size = len(data)
        self.send(size.to_bytes(8, 'big'))
        #print(f'sent size = {size}')
        self.send(data)
        #print('sent compressed img')
        #print(f'img_size={len(img_bytes)}')
    

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    #client = Client('192.168.95.46', 9090)
    client = Client('192.168.95.141', 9090)

    while True:
        res, frame = cap.read()
        frame = cv2.flip(frame, 1)
        
        #if cv2.waitKey(1) == ord('q'):
        #    break
        
        client.send_img(frame)
        
        command = client.recv_str()
        print(command)
        

    cv2.destroyAllWindows()
