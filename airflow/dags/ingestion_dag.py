# # airflow stuff
# # from airflow import DAG
# # from airflow.operators.python_operator import PythonOperator
# # from airflow.operators.postgres_operator import PostgresOperator
# # from datetime import datetime, timedelta
# from airflow import DAG
# from airflow.hooks.postgres_hook import PostgresHook
# from airflow.operators.python_operator import PythonOperator
# from datetime import datetime, timedelta
# from psycopg2.extras import execute_values
#
# # for postgres access
# import psycopg2 as pg
#
# default_args = {
#     "owner": "airflow",
#     "depends_on_past": False,
#     "start_date": datetime(2019, 1, 31),
#     "email": ["youremail@mail.com"],
#     "email_on_failure": False,
#     "email_on_retry": False,
#     "retries": 0,
#     "retry_delay": timedelta(minutes=5),
#     # 'queue': 'bash_queue',
#     # 'pool': 'backfill',
#     # 'priority_weight': 10,
#     # 'end_date': datetime(2016, 1, 1),
# }
#
# # use a daily interval for the schedule
# dag = DAG("ingestion_dag", default_args=default_args, schedule_interval='@daily', catchup=False)
#
#
# # replace with your connection data
# # t1 = PostgresOperator(
# #     task_id='create_table',
# #     postgres_conn_id="postgis_master",
# #     sql="CREATE TABLE temp1 (id_ig INT8 PRIMARY KEY);",
# #     database="gis",
# #     dag=dag)
#
#
# def etl(ds, **kwargs):
# # #     execution_date = kwargs['execution_date'].strftime('%Y-%m-%d')
# # #     query = """
# # # SELECT *
# # # FROM users
# # # WHERE created_at::date = date '{}'
# # #     """.format(execution_date)
# #
# #     src_conn = PostgresHook(postgres_conn_id='postgis_master',
# #                             schema='gis').get_conn()
# #     # dest_conn = PostgresHook(postgres_conn_id='dest',
# #     #                          schema='dest_schema').get_conn()
# #
# #     # notice this time we are naming the cursor for the origin table
# #     # that's going to force the library to create a server cursor
# #     src_cursor = src_conn.cursor("serverCursor")
# #     src_cursor.execute("""CREATE TABLE temp11 (id_id INT8 PRIMARY KEY);""")
# #     # dest_cursor = dest_conn.cursor()
# #
# #     # now we need to iterate over the cursor to get the records in batches
# #     # while True:
# #     #     records = src_cursor.fetchmany(size=2000)
# #     #     if not records:
# #     #         break
# #     #     execute_values(dest_cursor,
# #     #                    "INSERT INTO users VALUES %s",
# #     #                    records)
# #     #     dest_conn.commit()
# #
# #     src_cursor.close()
# #     # dest_cursor.close()
# #     src_conn.close()
# #     # dest_conn.close()
#
#
#     pg_hook = PostgresHook("postgis_master")
#     result = pg_hook.run("""CREATE TABLE temp11 (id_id INT8 PRIMARY KEY);""")
#
#
# t1 = PythonOperator(
#     task_id='etl',
#     provide_context=True,
#     python_callable=etl,
#     dag=dag)

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks import PostgresHook
from datetime import datetime, timedelta

args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2015, 1, 31),
    "email": ["youremail@mail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

def process_product_dim_py(**kwargs):
    conn_id = kwargs.get('conn_id')
    pg_hook = PostgresHook(conn_id)
    sql = """CREATE TABLE IF NOT EXISTS dua (id_id INT8 PRIMARY KEY);"""

    records = pg_hook.run(sql)

    return records

dag = DAG(
    'ingestion_dag',
    schedule_interval='@once',
    default_args=args)

process_product_dim = PythonOperator(
    task_id='process_product_dim',
    op_kwargs = {'conn_id':'postgis_master'},
    python_callable=process_product_dim_py,
    dag=dag)