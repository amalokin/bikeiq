from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.hooks import PostgresHook
from airflow.contrib.operators.ssh_operator import SSHOperator




#arguments for the dag
args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2015, 1, 1),
    "email": ["youremail@mail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}



def create_import_table(**kwargs):
    conn_id = kwargs.get('conn_id')
    pg_hook = PostgresHook(conn_id)
    sql = """
        CREATE TABLE IF NOT EXISTS trips (
            trip_id SERIAL8 PRIMARY KEY,
            city VARCHAR(16),
            duration_sec INT4,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            start_station_id FLOAT4,
            start_station_name VARCHAR(256),
            start_location_latitude FLOAT8,
            start_location_longitude FLOAT8,
            end_station_id FLOAT4,
            end_station_name VARCHAR(256),
            end_location_latitude FLOAT8,
            end_location_longitude FLOAT8,
            bike_id INT4,
            user_type VARCHAR(16),
            member_birth_year FLOAT4,
            member_gender VARCHAR(16)
            );
        """
    pg_hook.run(sql)

def create_tres(**kwargs):
    conn_id = kwargs.get('conn_id')
    pg_hook = PostgresHook(conn_id)
    sql = """CREATE TABLE IF NOT EXISTS tres (id_id INT8 PRIMARY KEY) DISTRIBUTE BY HASH(id_id);"""
    pg_hook.run(sql)

dag = DAG(
    'import_data',
    schedule_interval='@once',
    default_args=args)

create_import_table_op = PythonOperator(
    task_id='create_import_table',
    op_kwargs = {'conn_id':'postgis_master'},
    python_callable=create_import_table,
    dag=dag)

create_tres_op = PythonOperator(
    task_id='create_tres',
    op_kwargs = {'conn_id':'pgxl_coord1'},
    python_callable=create_tres,
    dag=dag)

#get s3 read into the local node
create_gisdata_op = SSHOperator(
    task_id = "create_folder_gisdata",
    ssh_conn_id = 'ssh_postgis',
    command = """sudo mkdir /gisdata/
                 sudo chmod 777 /gisdata/
                 #aws s3 cp s3://sharedbikedata/Land_use/gisdata/ /gisdata2/ --recursive
              """,
    dag=dag)




create_import_table_op >> create_tres_op
create_gisdata_op >> create_tres_op