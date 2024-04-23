import requests
from time import sleep
import random
from multiprocessing import Process
import boto3
import json
import sqlalchemy
from sqlalchemy import text
import datetime


random.seed(100)


class AWSDBConnector:

    def __init__(self):

        self.HOST = "pinterestdbreadonly.cq2e8zno855e.eu-west-1.rds.amazonaws.com"
        self.USER = 'project_user'
        self.PASSWORD = ':t%;yCY3Yjg'
        self.DATABASE = 'pinterest_data'
        self.PORT = 3306
        
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
            
            pin_invoke_url = 'https://39plmt8rih.execute-api.us-east-1.amazonaws.com/milestone5/topics/0affc6b7559b.pin'
            geo_invoke_url = "https://39plmt8rih.execute-api.us-east-1.amazonaws.com/milestone5/topics/0affc6b7559b.geo"
            user_invoke_url = "https://39plmt8rih.execute-api.us-east-1.amazonaws.com/milestone5/topics/0affc6b7559b.user"

            geo_result['timestamp'] = geo_result['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            user_result['date_joined'] = user_result['date_joined'].strftime("%Y-%m-%d %H:%M:%S")


            pin_payload = json.dumps({
                'records': [
                    {
                    'value': pin_result
                    }
                ]
            })


            geo_payload = json.dumps({
                'records': [
                    {
                    'value': geo_result
                    }
                ]
            })

            user_payload = json.dumps({
                'records': [
                    {
                    'value': user_result
                    }
                ]
            })

            headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}

            pin_response = requests.request("POST", pin_invoke_url, headers=headers, data=pin_payload)
            geo_response = requests.request("POST", geo_invoke_url, headers=headers, data=geo_payload)
            user_response = requests.request("POST", user_invoke_url, headers=headers, data=user_payload)

            print(pin_response.status_code)
            print(geo_response.status_code)
            print(user_response.status_code)




if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Working')
    


