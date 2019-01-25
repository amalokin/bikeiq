# Street Ferret
Last-mile intelligence.

Check the [slides](https://docs.google.com/presentation/d/18LPw-SW8qJNuNjT2F3QfWp9YstwNbiO7OuN-6nQ0AMo/edit?usp=sharing) out.

<hr/>

## How to install and get it up and running

TBD _sh_ script contents:
* _Postgres_ setup,
* _Postgis_ setup.

<hr/>

## Introduction

Sharing systems are galvanizing a renewed interest in bicycles, scooters, and other first/last 
mile mobility services. At an annual growth rate of 7%, global market size is estimated to 
reach $8 billion by 2023. To facilitate strategic planning, I’ve developed a map-based 
exploratory tool for data scientists and business analysts to identify promising locations 
and new markets for the service expansion. This tool uses historical trip data, socio-economic 
attributes, and land use characteristics, as it offers a platform of leveraging data-driven 
insights from fusing multisource datasets.

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
  
_Airflow_ will run _python_ tasks to load each trip dataset into a _PostgreSQL_ database 
to perform a spatial join (origin and destination points to polygons) with socio-economic 
and land use attributes in parallel. The enriched trip data, then, will be piped into 
_Cassandra_ or other NO SQL, column-wise database. _Spark_ will be used to process variables 
efficiently, 
e.g., to estimate basic statistics like correlation, OLS regression, etc.

_Flask_ will be used for creating a map-based dashboard to visualize pre-computed and arbitrary
queries of interest that will help to identify locations for expansion within the entire U.S. 

If time permits, the scope of the project may include ingesting station occupancy status 
(provided in each city with 10 seconds resolution). _Kafka_ will be used to provide this
functionality.


## Datasets

Historical trip data: 
[Alta Run Systems](https://github.com/BetaNYC/Bike-Share-Data-Best-Practices/wiki/Bike-Share-Data-Systems) 
(~ 70Gb across the whole systems)

Socio-economic data:
[American Community Survey 2017, 5 year estimates](https://www2.census.gov/programs-surveys/acs/summary_file/2017/data/5_year_entire_sf/) 
(~ 30Gb)

Land use data:
[EPA Smart Location Database](https://edg.epa.gov/data/PUBLIC/OP/SLD)
(~ 1Gb)

Spatial reference data:
[TIGER  Geodatabase](https://www.census.gov/geo/maps-data/data/tiger-geodatabases.html)
(~ 20Gb)




## Engineering challenges

* IO optimized search and retrieval of the required socio-economic data
* Efficient handling of the spatial matching pipelines
* Flexibility of the postprocessing
* Architecture built to satisfy preliminary and comprehensive data analysis

## Trade-offs

TBD
