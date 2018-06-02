from nodemcu import node
from simplehttpserver import server
import psycopg2

print('starting PostgreSQL connection')
try:
    con = psycopg2.connect(host='localhost', database='nodemcu', user='postgres', password='admin')
    cur = con.cursor()
except psycopg2.Error as e:
    print("Cannot connect to database", e)

print('starting nodemcu')
try:
    node = node.Node(con)
except:
    print("Error on create node instance")

print('starting server...')
try:
    server_address = ('', 8081)
    serv= server.Server(server_address,'interfaceWEB', node)
except:
    print("Error on create http server")

serv.run()
print('running server...')