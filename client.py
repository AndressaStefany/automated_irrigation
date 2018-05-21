import socket
import struct
import time
from threading import Thread
import psycopg2
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import os

class Node:
    def __init__(self):
        self.server_adddress = ('192.168.0.111', 5780)
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
                data = self.sock.recv(8)
            except:
                print('Connection lost recv')
                self.connected= False
                self.sock.close()
                while not self.connected:
                    self.connect_node()
                    time.sleep(0.5)
            try:
                sql = 'insert into sensors (temperature, humidity) values ({},{})'.format(struct.unpack('ff', data)[0],
                                                                                       struct.unpack('ff', data)[1])
                cur.execute(sql)
                con.commit()
            except:
                print('Error on saving on database')

    def send_data(self, modo):
        if self.connected:
            try:
                data = struct.pack("<B"+"H"*(len(modo)-1), *modo)
                self.sock.send(data)
            except:
                print('Connection lost send')
                self.connected = False
                self.sock.close()

class HttpServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        SimpleHTTPRequestHandler.do_GET(self)

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(self.rfile.read(length),keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        # Mod2 and/or Mod4
        # 0 - or; 1 - and
        Modo_6 = [6, 1]

        print("Post")
        postvars = self.parse_POST()
        for k,r in zip(postvars.keys(),postvars.values()):
            if b'tempo' in k:
                aux = str(r[0]).strip('b\'').split(':')
                postvars[b'tempo'] = int(aux[0]) * 60 + int(aux[1])
            else:
                postvars[k] = int(r[0])

        print(postvars)

        modo= []
        if postvars[b'modo'] == 1:
            modo= [postvars[b'modo'], postvars[b'tempo'], postvars[b'minutos']]
        if postvars[b'modo'] == 2:
            modo= [postvars[b'modo'], postvars[b'umi_min'], postvars[b'umi_max']]
        if postvars[b'modo'] == 3:
            modo= [postvars[b'modo'], postvars[b'umi_min'], postvars[b'minutos']]
        if postvars[b'modo'] == 4:
            modo= [postvars[b'modo'], postvars[b'temp_min'], postvars[b'temp_max']]
        if postvars[b'modo'] == 5:
            modo= [postvars[b'modo'], postvars[b'temp_max'], postvars[b'minutos']]
        if postvars[b'modo'] == 6:
            modo= [postvars[b'modo'], postvars[b'temp_min'], postvars[b'temp_max'], postvars[b'umi_min'], postvars[b'umi_max']]
        node.send_data(modo)

        SimpleHTTPRequestHandler.do_GET(self)

        # content_length = int(self.headers['Content-Length'])
        # body = self.rfile.read(content_length)
        # print(body)
        # self.send_response(200)
        # self.end_headers()
        # response = BytesIO()
        # response.write(b'This is POST request. ')
        # response.write(b'Received: ')
        # response.write(body)
        # self.wfile.write(response.getvalue())


print('starting PostgreSQL connection')
con = psycopg2.connect(host='localhost', database='nodemcu', user='postgres', password='admin')
cur = con.cursor()

print('starting node')
node = Node()

print('starting server...')
web_dir = os.path.join(os.path.dirname(__file__), 'interfaceWEB')
os.chdir(web_dir)
server_address = ('', 8081)
httpd = HTTPServer(server_address, HttpServer)
print('running server...')
httpd.serve_forever()