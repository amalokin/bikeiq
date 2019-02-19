## Airflow setup

On a ec2 instance install _Airflow_:

Install pip3 and additional libraries:
```
sudo apt install python3-pip build-essential libssl-dev libffi-dev python3-dev
```

Install Airflow:
```
echo "#airflow vars" >> ~/.bashrc
echo "export SLUGIFY_USES_TEXT_UNIDECODE=yes" >> ~/.bashrc
source ~/.bashrc

pip3 install apache-airflow[postgres,s3] paramiko sshtunnel
airflow initdb
airflow webserver &
airflow scheduler &
```


Configure a connection with the _PostGIS_ or any other node in the web interface 
(access it as public_DNS:8080):

```
Conn_id=[name]
Conn_type=[type]
Host=[public_dns]
Schema=[database]
Login=[username]
Password=[password]
Port=[port]
```

Copy contents of the ```dags/``` folder into ```~/airflow/dags/``` on the airflow node.


<hr></hr>

To kill an airflow webserver if needed: 
```
lsof -i tcp:8080
kill <pid>
```

