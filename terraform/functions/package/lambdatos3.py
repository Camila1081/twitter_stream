import json
import boto3
from datetime import date
from datetime import datetime
import os


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    s3 = boto3.resource("s3")
    bucket_name = os.environ['BUCKET_NAME']
    today = date.today()
    today = today.strftime("%b-%d-%Y")
    now = datetime.now()
    now = now.strftime("%d-%m-%Y-%H%M%S")
    s3_file=f'{today}/{now}.json'
    
    for record in event['Records']:
        print(record)
        print(record['eventName'])
        print("DynamoDB Record: " + json.dumps(record['dynamodb'], indent=2))
        
        #encoded_string = string.encode("utf-8")
        s3.Bucket(bucket_name).put_object(Key=s3_file, Body=json.dumps(record['dynamodb'], indent=2))
    
    return 'Successfully processed {} records.'.format(len(event['Records']))
