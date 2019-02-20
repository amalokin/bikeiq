from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.hooks import PostgresHook
from airflow.contrib.operators.ssh_operator import SSHOperator

import boto3
import psycopg2
import pandas as pd
from config_psql import config



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



#####Function definition
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


def ETL_run(**kwargs):
    conn_id = kwargs.get('conn_id')
    pg_hook = PostgresHook(conn_id)

    # get s3 iterators
    def get_matching_s3_objects(bucket, prefix='', suffix=''):
        """
        Generate objects in an S3 bucket.

        :param bucket: Name of the S3 bucket.
        :param prefix: Only fetch objects whose key starts with
            this prefix (optional).
        :param suffix: Only fetch objects whose keys end with
            this suffix (optional).
        """
        s3 = boto3.client('s3')
        kwargs = {'Bucket': bucket}

        # If the prefix is a single string (not a tuple of strings), we can
        # do the filtering directly in the S3 API.
        if isinstance(prefix, str):
            kwargs['Prefix'] = prefix

        while True:

            # The S3 API response is a large blob of metadata.
            # 'Contents' contains information about the listed objects.
            resp = s3.list_objects_v2(**kwargs)

            try:
                contents = resp['Contents']
            except KeyError:
                return

            for obj in contents:
                key = obj['Key']
                if key.startswith(prefix) and key.endswith(suffix):
                    yield obj

            # The S3 API is paginated, returning up to 1000 keys at a time.
            # Pass the continuation token into the next response, until we
            # reach the final page (when this field is missing).
            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break

    def get_matching_s3_keys(bucket, prefix='', suffix=''):
        """
        Generate the keys in an S3 bucket.

        :param bucket: Name of the S3 bucket.
        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        """
        for obj in get_matching_s3_objects(bucket, prefix, suffix):
            yield obj['Key']

    s3_bucket = "s3://sharedbikedata/"

    # load cities
    city_lookup = {"SanFrancisco/": "San Francisco",
                   "NewYork/": "New York",
                   "Boston/": "Boston",
                   "Washington/": "Washington",
                   "Chicago/": "Chicago"}

    def load_city(prefix):
        commands = (
            """
            COPY trips (city,
                            duration_sec,
                            start_time,
                            end_time,
                            start_station_id,
                            start_station_name,
                            start_location_latitude,
                            start_location_longitude,
                            end_station_id,
                            end_station_name,
                            end_location_latitude,
                            end_location_longitude,
                            bike_id,
                            user_type,
                            member_birth_year,
                            member_gender) 
            FROM '/tmp/city_trip_data.csv' DELIMITER ',' CSV HEADER;
            """,
        )

        for key in get_matching_s3_keys(bucket='sharedbikedata', prefix=prefix, suffix=('.zip', '.csv')):
            print(key)
            s3_path = [s3_bucket, key]
            df = pd.read_csv("".join(s3_path))  # get dataset from s3 to pd.df
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')',
                                                                                                                   '')

            df.insert(loc=0, column='city', value=city_lookup[prefix])
            if "bike_share_for_all_trip" in df:
                df = df.drop(["bike_share_for_all_trip"], axis=1)

            if "NewYork" in key:
                df.birth_year = pd.to_numeric(df.birth_year, errors='coerce')
            if "Boston" in key:
                df.birth_year = pd.to_numeric(df.birth_year, errors='coerce')
                df.end_station_id = pd.to_numeric(df.end_station_id, errors='coerce')
                df.end_station_latitude = pd.to_numeric(df.end_station_latitude, errors='coerce')
                df.end_station_longitude = pd.to_numeric(df.end_station_longitude, errors='coerce')

            df.to_csv("/tmp/city_trip_data.csv", index=False)

            for command in commands:
                pg_hook.run(command)

            break


    load_city("SanFrancisco/")



def create_tres(**kwargs):
    conn_id = kwargs.get('conn_id')
    pg_hook = PostgresHook(conn_id)
    sql = """CREATE TABLE IF NOT EXISTS tres (id_id INT8 PRIMARY KEY) DISTRIBUTE BY HASH(id_id);"""
    pg_hook.run(sql)




####DAG definition
dag = DAG(
    'import_data',
    schedule_interval='@once',
    default_args=args)

create_import_table_op = PythonOperator(
    task_id='create_import_table',
    op_kwargs = {'conn_id':'postgis_master'},
    python_callable=create_import_table,
    dag=dag)

ETL_run_op = PythonOperator(
    task_id='ETL_run',
    op_kwargs = {'conn_id':'postgis_master'},
    python_callable=ETL_run,
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




create_import_table_op >> ETL_run_op >> create_tres_op
create_gisdata_op >> create_tres_op