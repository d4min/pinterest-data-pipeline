# Pinterest Data Pipeline using AWS, Databricks, Spark, Airflow, Kinesis, Kafka and API Gateway

Pinterest crunches billions of data points every day to decide how to provide more value to their users. 

In this project, I will create a similar system using the AWS Cloud.

## Setting up the Pinterest infrastructure

To begin, I will need infrastructure similar to what a Pinterest data engineer would be working with. For this I used the user_posting_emulation.py script. This script contains login details for a RDS database with three tables that resemble the data received by the Pinterest API when a POST request is made by a user uploading data. This will provide us with the data to work with throughout the project. 

The three tables in the RDS include: 

    - pinterest_data: contains data about posts being uploaded to Pinterest.
    - geolocation_data: contains data about the geolocation of each Pinterest post found in pinterest_data
    - user_data: contains data about the user that has uploaded each post found in pinterest_data




