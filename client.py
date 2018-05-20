# socket_echo_client.py

import socket
import struct
import time
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

# hora e intervalo em minutos
Modo_1 = [1, 257, 33]
# Min e max da umidade
Modo_2 = [2, 20, 60]
# Min umidade e invervalo
Modo_3 = [3, 20, 55]
# Min e max da temperatura
Modo_4 = [4, 10, 35]
# Max da temperatura e intervalo
Modo_5 = [5, 35, 60]
# Mod2 and/or Mod4
# 0 - or; 1 - and
Modo_6 = [6, 1]

class HttpServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        print("Post")


print('starting server...')
# Server settings
# Choose port 8080, for port 80, which is normally used for a http server, you need root access
server_address = ('127.0.0.1', 8081)
httpd = HTTPServer(server_address, HttpServer)
print('running server...')
httpd.serve_forever()

exit(0)

class Node:
    def __init__(self):
        self.server_adddress = ('192.168.2.111', 5780)
        self.connected= False
        #self.sock= None
        self.connect_node()
        try:
            self.t= Thread(target=self.recv_data)
            self.t.start()
        except:
            print('Error on creating recv thread')

    def connect_node(self):
        print('Attempt to connect {} port {}'.format(*self.server_adddress))
        try:
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.server_adddress)
            self.sock.send(b'ok')
            self.connected= True
            print('Successfully connected')
        except socket.error as e:
            print('Error on attempt to connect', e)
            self.connected = False

    def recv_data(self):
        while 1:
            try:
                data = self.sock.recv(1)
                print(struct.unpack('B', data))
            except:
                print('Connection lost recv')
                self.connected= False
                self.sock.close()
                while not self.connected:
                    self.connect()
                    time.sleep(0.5)

    def send_data(self, Modo_1):
        if self.connected:
            try:
                data = struct.pack(">Bhh", Modo_1[0], Modo_1[1], Modo_1[2])
                self.sock.send(data)
            except:
                print('Connection lost send')
                self.connected = False
                self.sock.close()

node= Node()
while 1:
    node.send_data(Modo_1)
    time.sleep(1)