#!/usr/bin/env bash

#install aws cli
sudo apt install awscli

#update postgres repo
cd Downloads/
wget https://salsa.debian.org/postgresql/postgresql-common/raw/master/pgdg/apt.postgresql.org.sh
sudo sh apt.postgresql.org.sh

#install postgres and postgis
sudo apt-get install postgresql-10 postgis postgresql-10-postgis-2.4 postgresql-10-postgis-scripts

#change password to postgres user
sudo -u postgres psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'berkeley';"

#create gis db
sudo -u postgres createdb gis

#setup networking
# in /etc/postgresql/10/main/postgresql.conf change to listen_addresses = '*'
# in /etc/postgresql/10/main/pg_hba.conf change addresses for IPv4 connections to all
sudo service postgresql restart

#install following extensions into gis database
sudo -u postrges psql -c "CREATE EXTENSION postgis;" -d gis
sudo -u postrges psql -c "CREATE EXTENSION fuzzystrmatch;" -d gis
sudo -u postrges psql -c "CREATE EXTENSION address_standardizer;" -d gis
sudo -u postrges psql -c "CREATE EXTENSION postgis_tiger_geocoder;" -d gis

#intialize tiger loader parameters
sudo -u postrges psql -c "
INSERT INTO tiger.loader_platform(os, declare_sect, pgbin, wget, unzip_command, psql, path_sep,
		   loader, environ_set_command, county_process_command)
SELECT 'debbie', declare_sect, pgbin, wget, unzip_command, psql, path_sep,
	   loader, environ_set_command, county_process_command
  FROM tiger.loader_platform
  WHERE os = 'sh';" -d gis


#update tiger loader defaults
sudo -u postrges psql -c "
update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'yourpasswordhere','berkeley'))
where os='debbie';" -d gis

sudo -u postrges psql -c "
update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'geocoder','gis'))
where os='debbie';" -d gis

sudo -u postrges psql -c "
update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'10','11'))
where os='debbie';" -d gis

sudo -u postrges psql -c "
update tiger.loader_platform set declare_sect=
(select replace ((select declare_sect from tiger.loader_platform where os='debbie'),'shp2pgsql','/usr/bin/shp2pgsql'))
where os='debbie';" -d gis

#set up national data
psql -c "SELECT Loader_Generate_Nation_Script('debbie')" -d geocoder -tA > /gisdata/nation_script_load.sh
cd /gisdata/
sh nation_script_load.sh

sudo -u postrges psql -c "
UPDATE tiger.loader_lookuptables SET load = true
WHERE load = false AND lookup_name IN('tract', 'bg', 'tabblock');" -d gis

#specify tigerfiles for states to download
sudo -u postgres psql -c "SELECT Loader_Generate_Script(ARRAY['CA','DC','IL','MA','MD','MN',
  'NJ','NY','OH','OR','TN','VA'], 'debbie')" -d gis -tA > /gisdata/us12_load.sh

#run downloader: caution, due to the slow governmental servers it can take A LOT of time
sh us12_load.sh