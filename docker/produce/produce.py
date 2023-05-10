import json
import tweepy
import boto3
import time
import os
from datetime import date

# Set up Twitter API credentials using environment variables

consumer_key = '4ED9ORBXkJXhBGE8fZEueVbYo'
consumer_secret = '8SNjYhh7VvCoDUZ1NoUnbOfzJMd1kTJYF86f90Nta3omC0DLS8'
access_token = '1551802014-1551802014-l6o5nw1vJ7JgpwrQqoiUBR1GGPn6x9aOFyhyBYM'
access_token_secret ='DFRCT3Elg59NUKlxdEe5GeRw7pj0l3Ud5ihGHrkrlwIji'
bearer_token ='AAAAAAAAAAAAAAAAAAAAADMlbgEAAAAA83ftMr%2FuwnmZQ924OyzKzYfdBD4%3DiVmjk38LwLC8ntk6DxD68kfZUvMBL4EP6QgTYy5iRhINORUZnI'



print('consumer key é')
print(consumer_key)

"""
consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']"""

# Authenticate with the Twitter API
"""auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)"""

"""
auth = tweepy.OAuth2BearerHandler(bearer_token)
api = tweepy.API(auth)"""

client = tweepy.Client(bearer_token)



# Initialize the Kinesis client and set the stream name
kinesis_client = boto3.client('kinesis', region_name='us-west-2')
kinesis_stream_name = 'kinesis_twitter_stream'

# Initialize the tweet counter
tweet_count = 0

# Search for recent tweets containing the keyword 'itau'
# tweets = api.search(q='itau', lang='pt', count=10)

query = '(Itau ou Itaú) lang:pt -is:retweet'
resp = client.search_recent_tweets(
    query=query,
    tweet_fields = ['author_id','created_at','text','source','lang','geo'],
    user_fields = ['name','username','location','verified'],
    expansions = ['geo.place_id', 'author_id'],
    )
tweets = resp.data
includes = resp.includes
users = includes["users"]
print(f'Tweets: \n {tweets}')
print(f'includes: \n {includes}')
print(f'users: \n {users}\n')

print(f'tipo do tweets é : {type(tweets)}')

# Check if there are any tweets
if not tweets:
    print('\nNo tweets found.')

# Send each tweet to the Kinesis stream
print(len(tweets))
i=0
for tweet in tweets:
    i+=1
    print(f'\nTweet número {i}')
    print(f'tipo do tweet é : {type(tweet)}')
    print(len(tweet))
    print(tweet)
    print(f'Created at:{tweet.created_at}')    #print(f'Tweet id:{tweet.id}')
    #list(tweet.json.keys())
    #print(tweet[0][0])
    
    try:
        # Create a record for the Kinesis stream
        kinesis_record = {
            'Data': str(tweet),
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
        tweet_count += 1
    except Exception as e:
        print(f"Failed to send tweet with id {tweet.id} to Kinesis. Error: {e}")

# Print the total number of tweets processed
print(f"{tweet_count} tweets processed.")

# Sleep for 30 seconds
time.sleep(30)
