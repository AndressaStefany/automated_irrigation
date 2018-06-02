import socket
import struct
import time
from threading import Thread
from datetime import datetime

class Node:
    def __init__(self, db):
        self.server_adddress = ('192.168.0.111', 5780)
        self.connected= False
        #self.sock= None
        self.con = db
        self.connect_node()
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

        self.send_last_mode()

    def send_last_mode(self):
        last_r = self.get_data('cadastro', '*', 'data_cadastro = (select max(data_cadastro) from cadastro)')[0]
        pars = {'id': 0, 'data_cadastro': 1, 'minutos': 2, 'umi_min': 3, 'umi_max': 4, 'temp_min': 5, 'temp_max': 6,
                'modo': 7, 'tempo': 8}
        modo = []
        if last_r[pars['modo']] == 1:
            modo = [last_r[pars['modo']], last_r[pars['tempo']], last_r[pars['minutos']]]
        if last_r[pars['modo']] == 2:
            modo = [last_r[pars['modo']], last_r[pars['umi_min']], last_r[pars['umi_max']]]
        if last_r[pars['modo']] == 3:
            modo = [last_r[pars['modo']], last_r[pars['umi_min']], last_r[pars['minutos']]]
        if last_r[pars['modo']] == 4:
            modo = [last_r[pars['modo']], last_r[pars['temp_min']], last_r[pars['temp_max']]]
        if last_r[pars['modo']] == 5:
            modo = [last_r[pars['modo']], last_r[pars['temp_max']], last_r[pars['minutos']]]
        if last_r[pars['modo']] == 6:
            modo = [last_r[pars['modo']], last_r[pars['temp_min']], last_r[pars['temp_max']], last_r[pars['umi_min']],
                    last_r[pars['umi_max']]]


        # wait for the nodemcu
        time.sleep(1)
        for i in range(0,10):
            self.send_data(modo)
            minute= datetime.now()
            self.send_data([127, minute.hour*60+minute.minute, 0])
            time.sleep(0.1)

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
            self.save_data('sensors', ['temperature','humidity'], struct.unpack('ff', data))

    def send_data(self, modo):
        if self.connected:
            try:
                modo_= [int(x) for x in modo]
                data = struct.pack("<B"+"H"*(len(modo)-1), *modo_)
                self.sock.send(data)
            except:
                print('Connection lost -- send')
                self.connected = False
                self.sock.close()

    def get_data(self, table, cols, where):
        try:
            sql= 'select {} from {} where {}'.format(cols,table,where)
            cur= self.con.cursor()
            cur.execute(sql)
            return cur.fetchall()
        except:
            print("Error on geting data ")

    def save_data(self, table, keys, val):
        try:
            keys_= ''
            val_= ''
            for k,v in zip(keys,val):
                keys_+=k+(',' if k != keys[-1] else '')
                val_+=str(v)+(',' if k != keys[-1] else '')
            sql = 'insert into {} ({}) values ({})'.format(table,keys_,val_)
            self.con.cursor().execute(sql)
            self.con.commit()
        except:
            print('Error on saving on database in table {}'.format(table))