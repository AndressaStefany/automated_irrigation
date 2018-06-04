from nodemcu import node
from simplehttpserver import server
import psycopg2

import os

desired_output_file = open('log', 'a')
os.dup2(desired_output_file.fileno(), 1)
os.dup2(desired_output_file.fileno(), 2)

try:
    print('Starting PostgreSQL connection')
    con = psycopg2.connect(host='localhost', database='nodemcu', user='postgres', password='admin')

    print('Starting nodemcu')
    node = node.Node(con)

    print('Starting server...')
    server_address = ('', 8081)
    serv = server.Server(server_address, 'interfaceWEB', node)

    print('Running server...')
    serv.run()
except psycopg2.Error as e:
    print('Cannot connect to database', e)
except node.Error as e:
    print('Error on create node instance', e)
except:
    print("Error on create http server")
