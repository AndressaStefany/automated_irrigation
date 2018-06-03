from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs
import os
import struct
from array import array

class Handler(SimpleHTTPRequestHandler):
    node= None

    def do_GET(self):
        if ('/index.html' in self.path) or (self.path == '/' in self.path):
            data_banco = self.node.get_data('cadastro', '*', 'data_cadastro = (select max(data_cadastro) from cadastro)')[0]
            #datatime(year, month, day, hour, minute, second, microsecond)

            f = self.send_head()
            if f:
                aux= f.read()
                aux= array('B',struct.unpack('B'*len(aux),aux))
                #aux = str(f.read(), 'utf-8').strip('\'b')
                #print(aux)

                colunas = []
                linha =[]

                if data_banco[7] != None:
                    colunas.append('Modo')
                    if data_banco[7] == 1:
                        linha.append('Horário e intervalo de irrigação')
                    if data_banco[7] == 2:
                        linha.append('Umidade mínima e máxima')
                    if data_banco[7] == 3:
                        linha.append('Umidade mínima e intervalo de irrigação')
                    if data_banco[7] == 4:
                        linha.append('Temperatura mínima e máxima')
                    if data_banco[7] == 5:
                        linha.append('Temperatura máxima e intervalo de irrigação')
                    if data_banco[7] == 6:
                        linha.append('Umidade e Temperatura')
                if data_banco[1] != None:
                    colunas.append('Data de Cadastro')
                    string = data_banco[1].strftime('%d %b,%Y %H:%M')
                    linha.append(string)
                if data_banco[8] != None:
                    colunas.append('Horário de Irrigação')
                    hora = int(data_banco[8]/60)
                    minutos = data_banco[8]%60
                    linha.append(str(hora) + ":" + str(minutos))
                if data_banco[2] != None:
                    colunas.append('Intervalo de Irrigação')
                    linha.append(data_banco[2])
                if data_banco[3] != None:
                    colunas.append('Umidade Mínima')
                    linha.append(data_banco[3])
                if data_banco[4] != None:
                    colunas.append('Umidade Máxima')
                    linha.append(data_banco[4])
                if data_banco[5] != None:
                    colunas.append('Temperatura Mínima')
                    linha.append(data_banco[5])
                if data_banco[6] != None:
                    colunas.append('Temperatura Máxima')
                    linha.append(data_banco[6])

                html = '<table class=\"table\"><thead><tr>'
                for coluna in colunas:
                    html += '<th scope=\"col\">' + str(coluna) + '</th>'
                html += '</tr></thead><tbody><tr>'
                for l in linha:
                    html += '<td>'+str(l)+'</td>'
                html += '</tr></tbody></table>'

                html= html.encode('utf-8')
                to_format= array('B',struct.unpack('B'*len(html),html))

                idx = aux.index(123)
                while idx < len(aux):
                    if aux[idx+1]==123 and aux[idx+2]==125 and aux[idx+3]==125:
                        aux= aux[:idx]+to_format+aux[idx+4:]
                        break
                    idx += aux[idx+1:].index(123)
                #aux = aux.format(*to_format)
                self.wfile.write(aux)
        else:
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
        postvars = self.parse_POST()
        for k,r in zip(postvars.keys(),postvars.values()):
            if b'tempo' in k:
                aux = str(r[0]).strip('b\'').split(':')
                postvars[b'tempo'] = int(aux[0]) * 60 + int(aux[1])
            else:
                postvars[k] = int(r[0])


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
        self.node.send_data(modo)

        f = self.send_head()
        if f:
            aux = str(f.read(),'utf-8').strip('\'b')
            keys_table = []
            values_table = []
            values_save = []
            keys = []
            to_format = []

            if b'modo' in postvars.keys():
                keys_table.append('Modo')
                aux_v = postvars[b'modo']
                if aux_v == 1:
                    values_table.append('Horário e intervalo de irrigação')
                if aux_v == 2:
                    values_table.append('Umidade mínima e máxima')
                if aux_v == 3:
                    values_table.append('Umidade mínima e intervalo de irrigação')
                if aux_v == 4:
                    values_table.append('Temperatura mínima e máxima')
                if aux_v == 5:
                    values_table.append('Temperatura máxima e intervalo de irrigação')
                if aux_v == 6:
                    values_table.append('Umidade e Temperatura')
                keys.append('modo')
                values_save.append(aux_v)
            if b'tempo' in postvars.keys():
                keys_table.append('Horário de Irrigação')
                aux_v = postvars[b'tempo']
                hora = int(aux_v/60)
                minutos = aux_v%60
                values_table.append(str(hora) + ":" + str(minutos))
                keys.append('tempo')
                values_save.append(postvars[b'tempo'])

            if b'minutos' in postvars.keys():
                keys_table.append('Intervalo em minutos')
                values_table.append(postvars[b'minutos'])
                keys.append('minutos')
                values_save.append(postvars[b'minutos'])

            if b'umi_min' in postvars.keys():
                keys_table.append('Umidade mínima')
                values_table.append(postvars[b'umi_min'])
                keys.append('umi_min')
                values_save.append(postvars[b'umi_min'])

            if b'umi_max' in postvars.keys():
                keys_table.append('Umidade máxima')
                values_table.append(postvars[b'umi_max'])
                keys.append('umi_max')
                values_save.append(postvars[b'umi_max'])

            if b'temp_min' in postvars.keys():
                keys_table.append('Temperatura mínima')
                values_table.append(postvars[b'temp_min'])
                keys.append('temp_min')
                values_save.append(postvars[b'temp_min'])

            if b'temp_max' in postvars.keys():
                keys_table.append('Temperatura máxima')
                values_table.append(postvars[b'temp_max'])
                keys.append('temp_max')
                values_save.append(postvars[b'temp_max'])

            html = '<table class=\"table\"><thead><tr>'

            for key in keys_table:
                html += '<th scope=\"col\">'+key+'</th>'

            html += '</tr></thead><tbody><tr>'

            for value in values_table:
                html += '<td>'+str(value)+'</td>'

            html += '</tr></tbody></table>'
            to_format.append(html)

            aux=aux.format(*to_format)

            self.wfile.write(aux.encode('utf-8'))
            #self.copyfile(f, self.wfile)

            self.node.save_data('cadastro', keys, values_save)

            f.close()

class Server():
    def __init__(self, server_address, path, node):
        web_dir = os.path.join(os.path.dirname(__file__), '..',path)
        os.chdir(web_dir)
        Handler.node= node
        self.httpd = HTTPServer(server_address, Handler)

    def run(self):
        self.httpd.serve_forever()
