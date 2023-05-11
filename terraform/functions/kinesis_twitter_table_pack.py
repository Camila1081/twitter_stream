from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3
import requests
from requests_aws4auth import AWS4Auth
import json

region = 'us-west-2'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
host = 'search-test-z***ce.us-east-1.es.amazonaws.com'
index = 'boards'
type = '_doc'
url = 'https://' + host + '/' + index + '/' + type + '/'
headers = { "Content-Type": "application/json" }

def lambda_handler(event, context):
    print(event)
    client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    count = 0
    if(event.get("Records", None) != None):
        
        for record in event['Records']:
            if record['eventName'] == 'REMOVE':
                id = record['dynamodb']['Keys']['boardId']['S']
                document = record['dynamodb']['NewImage']
                print("Removing this document: ", document)
        
                response = client.delete(
                    index = index,
                    id = id,
                )
                count += 1
                print(response)
            else:
                id = record['dynamodb']['Keys']['boardId']['S']
                document = record['dynamodb']['NewImage']
                print("Indexing this document: ", document)
        
                response = client.index(
                    index = index,
                    body = document,
                    id = id,
                    refresh = True
                )
                count += 1
                print(response)
            
    else:
        response = client.search(
            body={
              'size': 1,
              'query': {
                'multi_match': {
                  'query': event['queryStringParameters']['search']
                }
              }
            }    
        )
        print(response)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
   
   #return str(count) + ' records processed.'