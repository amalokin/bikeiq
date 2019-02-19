# BikeIQ
#### Last-mile intelligence.

<hr></hr>

The front-end is available [here](https://bit.ly/bikeiq)

The slides are available 
[here](https://bit.ly/slides_bikeiq).

The screencast of the front-end functionality will be available soon.



## How to install and get it up and running

See the _READMEs_ and _shell_ scripts in the respective folders.

_AWS_ setup is not covered.

Node configurations include:

* _Airflow_ setup
* _PostGIS_ setup
* _Postgres-XL_ setup
* _Apache2_ setup


## Introduction

Sharing systems are galvanizing a renewed interest in bicycles, scooters, and other first/last 
mile mobility services. At an annual growth rate of 7%, global market size is estimated to 
reach [$8 billion by 2023](https://www.mordorintelligence.com/industry-reports/bike-sharing-market). 
To facilitate strategic planning, I’ve developed a map-based 
exploratory tool for data scientists and business analysts to identify promising locations 
and new markets for the service expansion. This tool can use historical trip data, 
socio-economic attributes, micro-climate data, land use characteristics, and other 
spatial data, as it offers a platform of leveraging data-driven insights from fusing 
multisource datasets.

## Architecture

_s3_ hosts historical trip datasets (stored as zipped/raw CSV files) partitioned by city 
of origin (San Francisco, New York, Boston are implemented, Chicago, Washington, Portland, 
Columbus, Chattanooga will be implemented in the future) and by time period (year, quarter, or 
month).

Additionally to the historical trip data, _s3_ contains socio-economic (the American Community 
Survey) and land use (the EPA Smart Location) data at a fine-grain level of census block groups 
(census tracts are possible with minimal adjustments to the data filtering script). This data is 
being selectively filtered 
and preprocessed using _python_. The resulting hand-picked, domain-relevant attributes are 
loaded into
_PostgreSQL_ database, which is set up on an _ec2_ cluster. 
  
_Airflow_ node runs _python_ and _bash_ tasks to load each trip dataset into a _PostgreSQL_ database 
with _PostGIS_ extension to perform a spatial join (origin and destination points to polygons)
with socio-economic and land use attributes. The enriched trip data, then, will be piped into 
_Postgres-XL_ data warehouse.

_Leaflet_ is used for creating a map-based dashboard to visualize pre-computed and arbitrary
queries of interest that will help to identify locations for expansion within the entire U.S. 



## Datasets

Historical trip data: 
[Alta Run Systems](https://github.com/BetaNYC/Bike-Share-Data-Best-Practices/wiki/Bike-Share-Data-Systems) 
(~ 70Gb across the whole system)

Socio-economic data:
[American Community Survey 2017, 5 year estimates](https://www2.census.gov/programs-surveys/acs/summary_file/2017/data/5_year_entire_sf/) 
(~ 30Gb)

Spatial reference data:
[TIGER  Geodatabase](https://www.census.gov/geo/maps-data/data/tiger-geodatabases.html)
(~ 300Gb)



## Engineering challenges

* Efficient use of spatial joins on geo-reference data 
* Defining the requirements for a data warehouse and choosing a solution accordingly

## Trade-offs

TBD
