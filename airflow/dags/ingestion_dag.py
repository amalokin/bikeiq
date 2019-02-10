from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks import PostgresHook
from datetime import datetime, timedelta

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

def create_tres(**kwargs):
    conn_id = kwargs.get('conn_id')
    pg_hook = PostgresHook(conn_id)
    sql = """CREATE TABLE IF NOT EXISTS tres (id_id INT8 PRIMARY KEY) DISTRIBUTE BY HASH(id_id);"""
    pg_hook.run(sql)

def create_dua(**kwargs):
    conn_id = kwargs.get('conn_id')
    pg_hook = PostgresHook(conn_id)
    sql = """CREATE TABLE IF NOT EXISTS dua (id_id INT8 PRIMARY KEY);"""
    pg_hook.run(sql)

dag = DAG(
    'ingestion_dag',
    schedule_interval='@once',
    default_args=args)

create_dua_op = PythonOperator(
    task_id='create_dua',
    op_kwargs = {'conn_id':'postgis_master'},
    python_callable=create_dua,
    dag=dag)

create_tres_op = PythonOperator(
    task_id='create_tres',
    op_kwargs = {'conn_id':'pgxl_coord1'},
    python_callable=create_tres,
    dag=dag)

create_dua_op >> create_tres_op