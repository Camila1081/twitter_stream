import json
import os
import boto3
import requests

dynamodb = boto3.client('dynamodb')
table_name = 'kinesis_twitter_table'
url = f"https://{os.environ['ENDPOINT']}/{os.environ['INDEX']}/_doc"
headers = {'Content-Type': 'application/json'}

def handler(event, context):
    for record in event['Records']:
        partition_key = record['dynamodb']['Keys']['partitionKey']['S']
        range_key = record['dynamodb']['Keys']['rangeKey']['S']
        item_url = f"{url}/{partition_key}_{range_key}"

        if record['eventName'] == 'REMOVE':
            response = requests.delete(item_url)
        else:
            new_image = record['dynamodb']['NewImage']
            document = boto3.dynamodb.types.TypeDeserializer().deserialize(new_image)
            document = remove_technical_fields(document)
            response = requests.put(item_url, json.dumps(document), headers=headers)
        
        print(response.text)
        
def remove_technical_fields(body):
    del body['SequenceNumber']
    del body['SizeBytes']
    del body['StreamViewType']
    del body['aws:rep:deleting']
    del body['aws:rep:updatetime']
    del body['aws:rep:updateregion']
    return body