# Street Ferret
Last-mile intelligence.

Check the [slides](#https://docs.google.com/presentation/d/18LPw-SW8qJNuNjT2F3QfWp9YstwNbiO7OuN-6nQ0AMo/edit?usp=sharing) out.

<hr/>

## How to install and get it up and running

TBD

<hr/>

## Introduction

The project will leverage shared bicycling data (past trip and current station occupancy) and land use data (Census, ACS) to create a platform for the demand analysis, future expansion, and usage optimization for docked or dockless bicycles and scooters.

## Architecture

_Airflow_ for orchestration

_Python_ for getting trip data from the external sources to S3

_Kafka_ for getting station occupancy updates. (Might get by using _RabbitMQ_.)

_Spark_ for data processing 

_PostgreSQL_ for spatial query

_Cassandra_ for storing time series data

_Flask_ for creating a dashboard

## Dataset

[Alta Run Systems](#https://github.com/BetaNYC/Bike-Share-Data-Best-Practices/wiki/Bike-Share-Data-Systems) 

## Engineering challenges

Defining and optimizing schema.

Making joins less expensive.

Realizing efficient spatial queries.

Maintaining and updating original and transposed data for various data access.

Storing and retrieving real-time data at high (simulated) load while ensuring reliability via replicating.

Ensuring fast read and processing for the historical and real-time data by distributed storage and computing.

## Trade-offs

TBD
