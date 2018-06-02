import socket
import struct
import time
from threading import Thread

class Node:
    def __init__(self, db):
        self.server_adddress = ('192.168.0.111', 5780)
        self.connected= False
        #self.sock= None
        self.connect_node()
        self.con= db
        try:
            self.t1= Thread(target=self.recv_data)
            self.t1.start()
            self.t2 = Thread(target=self.reconnect)
            self.t2.start()
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

    def reconnect(self):
        while 1:
            #print("Verificando conexao")
            try:
                data = b'ok'
                self.sock.send(data)
                self.connected = True
            except:
                print('Reconnecting...')
                self.connected = False
                self.sock.close()
                self.connect_node()
            time.sleep(5)

    def recv_data(self):
        while 1:
            try:
                data = self.sock.recv(8)
            except:
                print('Connection lost -- recv')
                self.connected= False
                self.sock.close()
                time.sleep(5)
                continue
            try:
                sql = 'insert into sensors (temperature, humidity) values ({},{})'.format(struct.unpack('ff', data)[0],
                                                                                       struct.unpack('ff', data)[1])
                self.con.cursor().execute(sql)
                self.con.commit()
            except:
                print('Error on saving on database {}'.format(data))

    def send_data(self, modo):
        if self.connected:
            try:
                data = struct.pack("<B"+"H"*(len(modo)-1), *modo)
                self.sock.send(data)
            except:
                print('Connection lost -- send')
                self.connected = False
                self.sock.close()