import boto3
import json
import time
from datetime import datetime



# Initialize DynamoDB and Kinesis resources and set up constants
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table_name = 'kinesis_twitter_table'
stream_name = 'kinesis_twitter_stream'

def process_record(record, kinesis):
    print(f"\nrecord {record}")
    
    kinesis_data = json.loads(record['Data'])
    print(f"\nkinesis_data {json.loads(record['Data'])}")
    #print(f"\ntweet_data {json.loads(kinesis_data['Data'])}")
    try:
        # Load Kinesis data from the record and parse the tweet data
        kinesis_data = json.loads(record['Data'])
        #tweet_data = json.loads(kinesis_data['Data'])
        tweet_data = kinesis_data
        print(f'\nTweet_data é {tweet_data}')

        # Check if the tweet has an 'id_str' field
        if 'id' not in tweet_data:
            print('Skipping record - no id_str field')
            return

        # Extract relevant fields from the tweet
        #tweet_id = tweet_data['id_str']
        tweet_id = tweet_data['id']
        created_at= tweet_data['created_at']
        print(f"Created at : {created_at}")
        #timestamp = datetime.strptime(tweet_data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        
        timestamp=record['ApproximateArrivalTimestamp']
        text = tweet_data['text']
        #user = tweet_data['user']
        print(f'\ntimestamp é {timestamp}')
        #comprehend:
        comprehend = boto3.client(service_name='comprehend', region_name='eu-west-1')
        sentiment_all = comprehend.detect_sentiment(Text=text, LanguageCode='pt')
        sentiment = sentiment_all['Sentiment']
        print(f"Sentimento é :{sentiment}")
        positive = sentiment_all['SentimentScore']['Positive']
        negative = sentiment_all['SentimentScore']['Negative']
        total = positive - negative
        print(total)

        # Put data into DynamoDB
        table = dynamodb.Table(table_name)
        item = {
            'id': tweet_id,
            'timestamp': str(timestamp.isoformat()),
            'text': text,
            'sentiment': str(round(total,2)),
            'created_at': str(created_at),
            #,'user': {'id': user['id_str'],'screen_name': user['screen_name'],'name': user['name']}
        }
        table.put_item(Item=item)

    except Exception as e:
        print(f'Error processing record: {e}')


def process_shard(shard_id):
    kinesis = boto3.client('kinesis', region_name='us-west-2')
    shard_iterator = kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=shard_id,
        ShardIteratorType='TRIM_HORIZON'
    )['ShardIterator']
    while True:
        # Fetch records from the shard
        response = kinesis.get_records(ShardIterator=shard_iterator, Limit=100)

        if not response['Records']:
            break

        # Process each record in the response
        for record in response['Records']:
            print(f'Process record :{record}')
            process_record(record, kinesis)

        # Update shard iterator and sleep for 1 second
        shard_iterator = response['NextShardIterator']
        time.sleep(2)


def main():
    kinesis = boto3.client('kinesis', region_name='us-west-2')

    while True:
        # List shards in the Kinesis stream
        response = kinesis.list_shards(StreamName=stream_name)
        shards = response['Shards']

        # Process each shard
        for shard in shards:
            print(f'Processing shard: {shard["ShardId"]}')
            process_shard(shard['ShardId'])

        # Reset shards and sleep for 15 seconds
        shards = None
        time.sleep(15)

if __name__ == '__main__':
    main()
