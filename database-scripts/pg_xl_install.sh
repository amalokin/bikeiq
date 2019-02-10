#!/usr/bin/env bash

#install pre-req libraries for Postgres-XL
sudo apt-get install libreadline6 libreadline6-dev zlib1g-dev flex bison

sudo adduser postgres

git clone git://git.postgresql.org/git/postgres-xl.git

echo "export PATH=/usr/local/pgsql/bin:$PATH" >> ~/.bashrc
source ~/.bashrc

#passwordless ssh
ssh-keygen -t rsa -N "" -f /home/postgres/.ssh/id_rsa
scp Downloads/YOUR_PEM.pem ubuntu@MASTER_DNS:~/.ssh/my.key
chmod 600 .ssh/my.key
#on each worker postgres@:
mkdir .ssh
chmod 700 .ssh
touch .ssh/authorized_keys
chmod 600 .ssh/authorized_keys
#add pub key manually
vim .ssh/authorized_keys
cat ~/.ssh/id_rsa.pub | ssh -i ~/.ssh/my.key postgres@10.0.0.X "cat >> ~/.ssh/authorized_keys"



#On all servers
#
#(GTM, Coord, Datanode1, Datanode2)
#
#Edit /etc/environment (I got tired fighting with .bashrc) and add to the path
#
#/usr/local/pgsql/bin:

#edit local pg_hba.conf to allow all connections
#then on each node:
select pg_reload_conf();

#coordinator node entering
psql postgres -p 30001
CREATE NODE node3 WITH (TYPE = datanode, HOST = '10.0.0.8', PORT = 40001);
CREATE NODE node4 WITH (TYPE = datanode, HOST = '10.0.0.6', PORT = 40002);
CREATE NODE node5 WITH (TYPE = datanode, HOST = '10.0.0.12', PORT = 40003);
select pgxc_pool_reload();
