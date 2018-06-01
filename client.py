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

        f = self.send_head()
        if f:
            aux = str(f.read(),'utf-8').strip('\'b')
            values = []
            to_format = []
            print(postvars.keys())
            if b'modo' in postvars.keys():
                aux_k = 'Modo'
                values.append(aux_k)
            if b'umi_min' in postvars.keys():
                aux_k = 'Umidade mínima'
                values.append(aux_k)
            if b'umi_max' in postvars.keys():
                aux_k = 'Umidade máxima'
                values.append(aux_k)
            if b'temp_min' in postvars.keys():
                aux_k = 'Temperatura mínima'
                values.append(aux_k)
            if b'temp_max' in postvars.keys():
                aux_k = 'Temperatura máxima'
                values.append(aux_k)
            if b'tempo' in postvars.keys():
                aux_k = 'Horário'
                values.append(aux_k)
            if b'minutos' in postvars.keys():
                aux_k = 'Intervalo em minutos'
                values.append(aux_k)

            html = '<table class=\"table\"><thead><tr>'

            for value in values:
                html += '<th scope=\"col\">'+str(value)+'</th>'

            html += '</tr></thead><tbody><tr>'
            values = []

            if b'modo' in postvars.keys():
                aux_v = postvars[b'modo']
                values.append(aux_v)
            if  b'umi_min' in postvars.keys():
                aux_v = postvars[b'umi_min']
                values.append(aux_v)
            if b'umi_max' in postvars.keys():
                aux_v = postvars[b'umi_max']
                values.append(aux_v)
            if b'temp_min' in postvars.keys():
                aux_v = postvars[b'temp_min']
                values.append(aux_v)
            if b'temp_max' in postvars.keys():
                aux_v = postvars[b'temp_max']
                values.append(aux_v)
            if b'tempo' in postvars.keys():
                aux_v = postvars[b'tempo']
                values.append(aux_v)
            if b'minutos' in postvars.keys():
                aux_v = postvars[b'minutos']
                values.append(aux_v)

            for value in values:
                html += '<td>'+str(value)+'</td>'

            html += '</tr></tbody></table>'
            to_format.append(html)

            aux=aux.format(*to_format)

            self.wfile.write(aux.encode('utf-8'))
            #self.copyfile(f, self.wfile)
            f.close()


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
