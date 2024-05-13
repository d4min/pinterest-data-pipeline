import requests
from time import sleep
import random
from multiprocessing import Process
import boto3
import json
import sqlalchemy
from sqlalchemy import text
import datetime
import yaml
import base64

random.seed(100)


class AWSDBConnector:

    def __init__(self):

        with open('db_creds.yaml', 'r')  as db_creds:

            db_dict = yaml.safe_load(db_creds)

        self.HOST = db_dict['RDS_HOST']
        self.USER = db_dict['RDS_USER']
        self.PASSWORD = db_dict['RDS_PASSWORD']
        self.DATABASE = db_dict['RDS_DATABASE']
        self.PORT = db_dict['RDS_PORT']
        
    def create_db_connector(self):
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?charset=utf8mb4")
        return engine


new_connector = AWSDBConnector()


def run_infinite_post_data_loop():
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:

            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)

            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            
            for row in geo_selected_row:
                geo_result = dict(row._mapping)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            
            for row in user_selected_row:
                user_result = dict(row._mapping)
            
            pin_invoke_url = 'https://39plmt8rih.execute-api.us-east-1.amazonaws.com/milestone5/streams/streaming-0affc6b7559b-pin/record'
            geo_invoke_url = 'https://39plmt8rih.execute-api.us-east-1.amazonaws.com/milestone5/streams/streaming-0affc6b7559b-geo/record'
            user_invoke_url = 'https://39plmt8rih.execute-api.us-east-1.amazonaws.com/milestone5/streams/streaming-0affc6b7559b-user/record'

            geo_result['timestamp'] = geo_result['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            user_result['date_joined'] = user_result['date_joined'].strftime("%Y-%m-%d %H:%M:%S")


            #To send JSON messages you need to follow this structure
            pin_payload = json.dumps({
                "StreamName": "streaming-0affc6b7559b-pin",
                "Data": {
                        #Data should be send as pairs of column_name:value, with different columns separated by commas      
                        "category": pin_result["category"], "description": pin_result["description"], "downloaded": pin_result["downloaded"], "follower_count": pin_result["follower_count"], "image_src": pin_result["image_src"], "index": pin_result["index"], "is_image_or_video": pin_result['is_image_or_video'], 'poster_name': pin_result['poster_name'], 'save_location': pin_result['save_location'], 'tag_list': pin_result['tag_list'], 'title': pin_result['title'], 'unique_id': pin_result['unique_id']
                        },
                        "PartitionKey": "desired-name"
                        })

            geo_payload = json.dumps({
                "StreamName": "streaming-0affc6b7559b-pin",
                "Data": {
                        #Data should be send as pairs of column_name:value, with different columns separated by commas      
                        "country": geo_result["country"], "ind": geo_result["ind"], "latitude": geo_result["latitude"], "longitude": geo_result["longitude"], "timestamp": geo_result["timestamp"]
                        },
                        "PartitionKey": "desired-name"
                        })
            
            user_payload = json.dumps({
                "StreamName": "streaming-0affc6b7559b-pin",
                "Data": {
                        #Data should be send as pairs of column_name:value, with different columns separated by commas      
                        "age": user_result["age"], "ind": user_result["ind"], "date_joined": user_result["date_joined"], "first_name": user_result["first_name"], "last_name": user_result["last_name"]
                        },
                        "PartitionKey": "desired-name"
                        })


            headers = {'Content-Type': 'application/json'}

            pin_response = requests.request("PUT", pin_invoke_url, headers=headers, data=pin_payload)
            geo_response = requests.request("PUT", geo_invoke_url, headers=headers, data=geo_payload)
            user_response = requests.request("PUT", user_invoke_url, headers=headers, data=user_payload)

            print(pin_response.status_code)
            print(geo_response.status_code)
            print(user_response.status_code)




if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Working')