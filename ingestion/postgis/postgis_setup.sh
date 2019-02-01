#!/usr/bin/env bash

#update postgres repo
cd Downloads/
wget https://salsa.debian.org/postgresql/postgresql-common/raw/master/pgdg/apt.postgresql.org.sh
sudo sh apt.postgresql.org.sh

#install postgres and postgis
sudo apt-get install postgresql-10 postgis postgresql-10-postgis-2.4 postgresql-10-postgis-scripts

#change password to postgres user
sudo -u postgres psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'berkeley';"

#create gis db
sudo -u postgres createdb gis

#setup networking
# in /etc/postgresql/10/main/postgresql.conf change to listen_addresses = '*'
# in /etc/postgresql/10/main/pg_hba.conf change addresses for IPv4 connections to all
sudo service postgresql restart