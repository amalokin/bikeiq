--men take shorter trips that women:
select avg(duration_sec)/60 as duration_min, member_gender from trip_data group by member_gender order by duration_min;


--setting up tiger, #4 https://postgis.net/docs/manual-2.5/postgis_installation.html#install_tiger_geocoder
update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'yourpasswordhere','berkeley'))
where os='debbie';

update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'geocoder','gis'))
where os='debbie';

update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'9.4','9.5'))
where os='debbie';

update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'${PGBIN}/shp2pgsql','/usr/bin/shp2pgsql'))
where os='debbie';


--downloading tigerfiles for all states
sudo -u postgres psql -c "SELECT Loader_Generate_Script(ARRAY['AK','AL','AR','AZ','CA','CO','CT','DE','DC','FL','GA','HI','IA,''ID','IL',
'IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE',
'NH','NJ','NM','NV','NY','OH','OK','OR','PA','PR','RI','SC','SD','TN','TX',
'UT','VA','VT','WA','WI','WV','WY'], 'debbie')" -d gis -tA > /gisdata/us52_load.sh

--downloading tigerfiles for states where biking stations are present
sudo -u postgres psql -c "SELECT Loader_Generate_Script(ARRAY['CA','DC','IL','MA','MD','MN',
  'NJ','NY','OH','OR','TN','VA'], 'debbie')" -d gis -tA > /gisdata/us12_load.sh


--updating table, creating point geometry
ALTER TABLE trips ADD COLUMN start_station_point geometry(Point, 4269);
ALTER TABLE trips ADD COLUMN end_station_point geometry(Point, 4269);
UPDATE trips SET start_station_point=st_SetSrid(st_MakePoint(start_location_longitude, start_location_latitude), 4269);
UPDATE trips SET end_station_point=st_SetSrid(st_MakePoint(end_location_longitude, end_location_latitude), 4269);


--matching fips with trip data
ALTER TABLE trips ADD COLUMN start_fips VARCHAR(12);
ALTER TABLE trips ADD COLUMN end_fips VARCHAR(12);

UPDATE trips SET start_fips=fips.bg_id
FROM
(SELECT trips.trip_id, bg.bg_id
FROM trips, bg
WHERE ST_Contains(bg.the_geom,trips.start_station_point)
) AS fips
WHERE trips.trip_id = fips.trip_id;

UPDATE trips SET end_fips=fips.bg_id
FROM
(SELECT trips.trip_id, bg.bg_id
FROM trips, bg
WHERE ST_Contains(bg.the_geom,trips.end_station_point)
) AS fips
WHERE trips.trip_id = fips.trip_id;




--create schema for acs (should be automated in the relevant script,
--change default output for missing values from '.' to '',
--create bg_id variable,
--sort it)
CREATE TABLE IF NOT EXISTS acs (
        fips VARCHAR(19) PRIMARY KEY,
        bach_edu FLOAT8,
        tot_trips FLOAT8,
        trips_u10 FLOAT8,
        trips_1014 FLOAT8,
        trips_1519 FLOAT8,
        med_age FLOAT8,
        med_age_m FLOAT8,
        med_age_f FLOAT8,
        pop_tot FLOAT8,
        race_white FLOAT8,
        race_black FLOAT8,
        asian FLOAT8,
        smartphone FLOAT8,
        car FLOAT8,
        transit FLOAT8,
        bike FLOAT8,
        walk FLOAT8,
        male_tot FLOAT8,
        fmale_tot FLOAT8,
        units_tot FLOAT8,
        owned FLOAT8,
        rented FLOAT8,
        med_hh_inc FLOAT8,
        med_rent FLOAT8
        );

COPY acs FROM '/home/ubuntu/street_ferret/data/acs.csv' DELIMITER ',' CSV HEADER;

ALTER TABLE acs ADD COLUMN bg_id VARCHAR(12);
UPDATE acs SET bg_id=substring(fips, 8);






--match ACS data with polygons
DROP TABLE IF EXISTS acs_mapped;
CREATE TABLE acs_mapped AS
SELECT DISTINCT ON(acs.bg_id)
  acs.*, bg.statefp, bg.countyfp, bg.aland, bg.the_geom
FROM acs
INNER JOIN bg
ON acs.bg_id = bg.bg_id;


--export mapped ACS CA data
COPY(
SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(features.feature)
)
FROM (
  SELECT jsonb_build_object(
    'type',       'Feature',
    'id',         bg_id,
    'geometry',   ST_AsGeoJSON(the_geom)::jsonb,
    'properties', to_jsonb(inputs) - 'bg_id' - 'the_geom'
  ) AS feature
  FROM (
    SELECT *
    FROM acs_mapped
    WHERE statefp = '06' AND (countyfp = '075' OR
                              countyfp = '081' OR
                              countyfp = '001' OR
                              countyfp = '085')
    ) AS inputs) AS features
) TO '/home/ubuntu/street_ferret/app/html/data/bg_polyCA.json';

COPY(
SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(features.feature)
)
FROM (
  SELECT jsonb_build_object(
    'type',       'Feature',
    'id',         bg_id,
    'geometry',   ST_AsGeoJSON(the_geom)::jsonb,
    'properties', to_jsonb(inputs) - 'bg_id' - 'the_geom'
  ) AS feature
  FROM (
    SELECT *
    FROM acs_mapped
    WHERE statefp = '06' AND (countyfp = '075')
    ) AS inputs) AS features
) TO '/home/ubuntu/street_ferret/app/html/data/bg_polySF.json';






----station-wide total trip count
--start station trip count
DROP TABLE IF EXISTS start_station_count;
CREATE TABLE start_station_count AS
SELECT  DISTINCT ON (aggr.start_station_id)
        aggr.start_station_id AS station_id,
        aggr.cnt,
        trips.start_station_point AS station_point,
        trips.start_station_name AS station_name
        FROM
        (SELECT count(trip_id) as cnt, start_station_id
        FROM trips
        GROUP BY start_station_id
        ) AS aggr
        INNER JOIN trips
        ON aggr.start_station_id = trips.start_station_id;

--end station trip count
DROP TABLE IF EXISTS end_station_count;
CREATE TABLE end_station_count AS
SELECT  DISTINCT ON (aggr.end_station_id)
        aggr.end_station_id AS station_id,
        aggr.cnt,
        trips.end_station_point AS station_point,
        trips.end_station_name AS station_name
        FROM
        (SELECT count(trip_id) as cnt, end_station_id
        FROM trips
        GROUP BY end_station_id
        ) AS aggr
        INNER JOIN trips
        ON aggr.end_station_id = trips.end_station_id;

--all station trip count
DROP TABLE IF EXISTS all_station_count;
CREATE TABLE all_station_count AS
SELECT  start_station_count.station_id,
        (start_station_count.cnt + end_station_count.cnt) AS cnt,
        start_station_count.station_name,
        start_station_count.station_point
FROM start_station_count, end_station_count
WHERE start_station_count.station_id = end_station_count.station_id;

--export start station trips
COPY(
  SELECT jsonb_build_object(
      'type',     'FeatureCollection',
      'features', jsonb_agg(features.feature)
  )
  FROM (
    SELECT jsonb_build_object(
      'type',       'Feature',
      'id',         station_id,
      'geometry',   ST_AsGeoJSON(station_point)::jsonb,
      'properties', to_jsonb(inputs) - 'station_id' - 'station_point'
    ) AS feature
    FROM start_station_count AS inputs
  ) AS features
) TO '/home/ubuntu/street_ferret/app/html/data/start_trip_count.json';

--export end station trips
COPY(
  SELECT jsonb_build_object(
      'type',     'FeatureCollection',
      'features', jsonb_agg(features.feature)
  )
  FROM (
    SELECT jsonb_build_object(
      'type',       'Feature',
      'id',         station_id,
      'geometry',   ST_AsGeoJSON(station_point)::jsonb,
      'properties', to_jsonb(inputs) - 'station_id' - 'station_point'
    ) AS feature
    FROM end_station_count AS inputs
  ) AS features
) TO '/home/ubuntu/street_ferret/app/html/data/end_trip_count.json';

--export all station trips
COPY(
  SELECT jsonb_build_object(
      'type',     'FeatureCollection',
      'features', jsonb_agg(features.feature)
  )
  FROM (
    SELECT jsonb_build_object(
      'type',       'Feature',
      'id',         station_id,
      'geometry',   ST_AsGeoJSON(station_point)::jsonb,
      'properties', to_jsonb(inputs) - 'station_id' - 'station_point'
    ) AS feature
    FROM all_station_count AS inputs
  ) AS features
) TO '/home/ubuntu/street_ferret/app/html/data/all_trip_count.json';
