import psycopg2
from config_psql import config


def read_data():
    """ read tables in the PostgreSQL database"""
    commands = (
        """
        COPY trip_data (duration_sec,
                        start_time,
                        end_time,
                        start_station_id,
                        start_station_name,
                        start_location_latitude,
                        start_location_longitude,
                        end_station_id,
                        end_station_name,
                        end_location_latitutde,
                        end_location_longitude,
                        bike_id,
                        user_type,
                        member_birth_year,
                        member_gender) 
        FROM '/home/ubuntu/street_ferret/data/2017-fordgobike-tripdata.csv' DELIMITER ',' CSV HEADER;
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
    read_data()