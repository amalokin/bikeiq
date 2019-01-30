import boto3
import psycopg2
import pandas as pd
from config_psql import config


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
#s3 = boto3.client('s3')


city_lookup = {"SanFrancisco/": "San Francisco",
               "NewYork/": "New York",
               "Boston/": "Boston",
               "Washington/": "Washington",
               "Chicago/": "Chicago"}


params = config()
conn = psycopg2.connect(**params)
cur = conn.cursor()


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
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
        #print(df.columns)

        df.insert(loc=0, column='city', value=city_lookup[prefix])
        if "bike_share_for_all_trip" in df:
            df = df.drop(["bike_share_for_all_trip"], axis=1)

        if "NewYork" in key:
            # df = df.rename(columns={'tripduration': 'duration_sec',
            #                     'starttime': 'start_time',
            #                    'stoptime': 'end_time',
            #                    'start station id': 'start_station_id',
            #                    'start station name': 'start_station_name',
            #                    'start station latitude': 'start_location_latitude',
            #                    'start station longitude': 'start_location_longitude',
            #                    'end station id': 'end_station_id',
            #                    'end station name': 'end_station_name',
            #                    'end station latitude': 'end_location_latitude',
            #                    'end station longitude': 'end_location_longitude',
            #                    'bikeid': 'bike_id',
            #                    'usertype': 'user_type',
            #                    'birth_year': 'member_birth_year',
            #                    'gender': 'member_gender'})
            df.birth_year = pd.to_numeric(df.birth_year, errors='coerce')
        if "Boston" in key:
            df.birth_year = pd.to_numeric(df.birth_year, errors='coerce')
            df.end_station_id = pd.to_numeric(df.end_station_id, errors='coerce')
            df.end_station_latitude = pd.to_numeric(df.end_station_latitude, errors='coerce')
            df.end_station_longitude = pd.to_numeric(df.end_station_longitude, errors='coerce')



        df.to_csv("/tmp/city_trip_data.csv", index=False)

        for command in commands:
            cur.execute(command)

    conn.commit()
    conn.close()

load_city("SanFrancisco/")
#load_city("NewYork/")
#load_city("Boston/")

