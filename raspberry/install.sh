wget https://github.com/fg2it/grafana-on-raspberry/releases/download/v5.1.3/grafana_5.1.3_armhf.deb
dpkg -i grafana_5.1.3_armhf.deb
sudo apt-get install python3-psycopg2
sudo apt-get install postgresql

#sudo nano /etc/grafana/grafana.ini Ativar acesso anonimo
sudo service grafana-server start
sudo -u postgres createdb nodemcu
# criar tabelas 

