import json
import boto3
from datetime import date
from datetime import datetime
import os


def file_content(s3,s3_client,bucket_name,itemname):
    print('file_content')
    #s3_client = boto3.client("s3")
    
    # Use a função list_objects_v2 para listar todos os objetos em um bucket S3
    response = s3_client.list_objects(Bucket=bucket_name)
    
    print(f'Itens of bucket {bucket_name}')
    itens=response['Contents']
    print(itens)
    
    flag_exist=False
    for item in itens:
        print(f'Loop in bucket, item is {item}')
        #print(f'Loop in bucket, item-key is {item['Key']}')
        if item["Key"]==itemname:
            flag_exist=True
            
    print(f'File {itemname} exist? {flag_exist}')
    flag_glue=False
    if flag_exist:
        print('vai entrar no read')
        existing_data= read_file(s3,bucket_name,itemname)
        print (f'content of file {itemname} is {existing_data}')
        return existing_data.decode('utf-8'),flag_glue
    else:
        print(f'{itemname} é novo no bucket, chamar o glue')
        flag_glue=True
        return "",flag_glue
        
    
        
def read_file(s3,bucketname,itemname):
    print('entrou no read')
    obj = s3.Object(bucketname, itemname)
    body = obj.get()['Body'].read()
    print(f'body é {body}')
    return body
    

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    s3 = boto3.resource("s3")
    s3_client = boto3.client('s3')
    glue = boto3.client('glue')
    
    
    bucket_name = os.environ['BUCKET_NAME']
    
    today = date.today()
    today = today.strftime("%b-%d-%Y")
    now = datetime.now()
    now = now.strftime("%d-%m-%Y:%H")
    s3_file=f'{now}.json'
    print(f'file name {s3_file}')

    flag=False

    print('records')
    content=""
    for record in event['Records']:
        print(record)
        print(record['eventName'])
        print("DynamoDB Record: " + json.dumps(record['dynamodb'], indent=2))
        
        content= content + json.dumps(record['dynamodb'], indent=2)

       
    print(f'existing data {content}')   
    existing_data, flag_glue = file_content(s3,s3_client,bucket_name, s3_file)
    #print(f'existing data {existing_data}') 
    
    #Concatenating strings
    content = existing_data + content
    
    #Writing file in bucket
    print('Writing file in bucket')
    s3.Bucket(bucket_name).put_object(Key=s3_file, Body=content)
    
    print(f'flag glue is {flag_glue}')
    if flag_glue:
        print('Calling glue')
        response = glue.start_job_run(JobName = 'twitter_job')


    return 'Successfully processed {} records.'.format(len(event['Records']))
