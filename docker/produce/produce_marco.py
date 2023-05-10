import tweepy
from tweepy import StreamingClient, StreamRule
import os
from dotenv import load_dotenv
import boto3
from datetime import date
import json
load_dotenv()
 
#bearer_token = os.getenv('bearer-token')
bearer_token ='AAAAAAAAAAAAAAAAAAAAADMlbgEAAAAA83ftMr%2FuwnmZQ924OyzKzYfdBD4%3DiVmjk38LwLC8ntk6DxD68kfZUvMBL4EP6QgTYy5iRhINORUZnI'
# Initialize the Kinesis client and set the stream name
kinesis_client = boto3.client('kinesis', region_name='us-west-2')
kinesis_stream_name = 'kinesis_twitter_stream'
 
class TweetPrinterV2(tweepy.StreamingClient):
    
    def on_tweet(self, tweet):
        print(f"{tweet.id} {tweet.created_at} ({tweet.author_id}): {tweet.text}")
        print("-"*50)
    
def to_kinesis(tweet):
    
    try:
        # Create a record for the Kinesis stream
        kinesis_record = {
            'Data': str(tweet.text),
            'Created_at':str(tweet.created_at),
            'PartitionKey': date.today()
        }
        print(f'tipo kinesis_record é : {type(kinesis_record)}')
        msg=json.dumps(kinesis_record)
        print(f'tipo msg é : {type(msg)}')
        
        # Put the record into the Kinesis stream
        response = kinesis_client.put_record(StreamName=kinesis_stream_name, Data=msg,
                                             PartitionKey='partitionkey')
        # Print the record being sent to Kinesis
        print(f"Sending record to Kinesis: {msg}")
        # Increment tweet counter
    except Exception as e:
        print(f"Failed to send tweet with id {tweet.id} to Kinesis. Error: {e}")

"""
rule = StreamRule(value="(Itau ou Itaú) lang:pt -is:retweet")
TweetPrinterV2(bearer_token).add_rules(rule)
TweetPrinterV2(bearer_token).filter()"""

api = tweepy.StreamingClient(bearer_token)
rule = tweepy.StreamRule(value="(Itau ou Itaú) lang:pt -is:retweet")
#tweet=tweepy.StreamingClient(bearer_token).add_rules(rule)
#print(tweet)
tweet=api.add_rules(rule)
print(tweet)
print(type(tweet))
to_kinesis(tweet)