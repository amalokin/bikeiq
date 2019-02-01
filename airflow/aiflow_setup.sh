#!/usr/bin/env bash

###get pip3
sudo apt install python3-pip


###install airflow
#modify .bashrc
echo "#airflow vars" >> ~/.bashrc
echo "export SLUGIFY_USES_TEXT_UNIDECODE=yes" >> ~/.bashrc
source ~/.bashrc
#intall airflow with hooks
pip3 install apache-airflow[postgres,s3]
airflow initdb
airflow webserver

#kill airflow
#lsof -i tcp:8080
#kill <pid>

###configure a connection with the postgis node in the web interface:
#Conn_id=postgis_master
#Conn_type=Postgres
#Host=[public_dns]
#Schema=gis
#Login=postgres
#Password=berkeley
#Port=5432