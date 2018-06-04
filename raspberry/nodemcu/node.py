import socket
import struct
import time
from threading import Thread
from datetime import datetime

class Error(Exception):
    def __init__(self, value):
        self.value= value
    def __str__(self):
        return repr(self.value)

class Node:
    def __init__(self, db):
        self.verbose= 1
        self.server_adddress = ('192.168.0.111', 5780)
        self.connected= False
        #self.sock= None
        self.con = db
        try:
            self.t1= Thread(target=self.reconnect)
            self.t1.start()
            self.t2 = Thread(target=self.recv_data)
            self.t2.start()
        except:
            raise Error('Error on creating threads')

    def connect_node(self):
        if self.verbose: print('Attempt to connect {} port {}'.format(*self.server_adddress))
        try:
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.server_adddress)

            self.sock.send(b'ok')
            self.connected= True
            if self.verbose: print('Successfully connected')
        except socket.error as e:
            if self.verbose: print('Error on attempt to connect', e)
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

        if self.verbose > 1: print('Seding last mode and time')
        # wait for the nodemcu
        time.sleep(0.5)
        for i in range(0,4):
            self.send_data(modo)
            minute= datetime.now()
            timepack= [127, (minute.hour*60+minute.minute)*10+minute.second/6.0, 0]
            self.send_data(timepack)
            time.sleep(0.1)

    def reconnect(self):
        while not self.connected:
            self.connect_node()
            time.sleep(5)
        while 1:
            if self.verbose > 2: print("Verificando conexao")
            try:
                data = b'ok'
                self.sock.send(data)
                self.connected = True
            except:
                if self.verbose: print('Reconnecting...')
                self.connected = False
                self.sock.close()
                while not self.connected:
                    self.connect_node()
                    time.sleep(5)
            time.sleep(5)

    def recv_data(self):
        while not self.connected:
            pass
        while 1:
            try:
                data = self.sock.recv(8)
                if self.verbose > 1: print('Recv ', data, struct.unpack('ff', data))
            except:
                if self.verbose: print('Connection lost -- recv')
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
                if self.verbose > 1: print('Seding ', data, modo_)
                self.sock.send(data)
            except:
                if self.verbose: print('Connection lost -- send')
                self.connected = False
                self.sock.close()

    def get_data(self, table, cols, where):
        try:
            sql= 'select {} from {} where {}'.format(cols,table,where)
            cur= self.con.cursor()
            if self.verbose > 1: print(sql)
            cur.execute(sql)
            return cur.fetchall()
        except:
            if self.verbose: print("Error on geting data ")

    def save_data(self, table, keys, val):
        try:
            keys_= ''
            val_= ''
            for k,v in zip(keys,val):
                keys_+=k+(',' if k != keys[-1] else '')
                val_+=str(v)+(',' if k != keys[-1] else '')
#            sql = 'insert into {} ({}) values ({})'.format(table,keys_,val_)
            sql = 'insert into {} ({}) values ({})'.format(table,keys_,'%s,'*(len(val)-1)+'%s')
            if self.verbose > 1: print(sql,val)
            self.con.cursor().execute(sql,tuple(val))
            self.con.commit()
        except:
            if self.verbose: print('Error on saving on database in table {}'.format(table))
