import requests

login= requests.post('http://127.0.0.1:3000/login',data={'user':'admin','password':'admin','email':''})
data = open('dash.json').read()
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
createdb= requests.post('http://127.0.0.1:3000/api/dashboards/db',cookies=login.cookies,data=data,headers=headers)
print(createdb.text)
data= open('datasource.json').read()
createds= requests.post('http://127.0.0.1:3000/api/datasources',cookies=login.cookies,data=data,headers=headers)
print(createds.text)

