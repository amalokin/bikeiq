import psycopg2
from config_psql import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
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
        """,
    )
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()