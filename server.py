# socket_echo_client.py

import socket
import struct
import time
from threading import Thread

class MyThread(Thread):

        def __init__(self, sock):
                Thread.__init__(self)
                self.sock = sock

        def run(self):
                try:
                        while 1:
                                data = self.sock.recv(1)
                                self.sock.send(b'oo')
                                print(struct.unpack('B', data))
                                #time.sleep(0.5)
                except:
                        self.sock.close()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('192.168.0.111', 5780)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
sock.send(b'oo')

while 1:
        t = MyThread(sock=sock)
        t.start()
        while t.isAlive():
                sock.send(b'k0')
                time.sleep(1)
                sock.send(b'k1')
                time.sleep(1)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('192.168.0.111', 5780)
        print('connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)
        sock.send(b'ok')
        time.sleep(1)
