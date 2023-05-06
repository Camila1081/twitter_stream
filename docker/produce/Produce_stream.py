import requests
import os
import json
from datetime import date
import boto3

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ['BEARER_TOKEN']
#bearer_token = 'AAAAAAAAAAAAAAAAAAAAADMlbgEAAAAA83ftMr%2FuwnmZQ924OyzKzYfdBD4%3DiVmjk38LwLC8ntk6DxD68kfZUvMBL4EP6QgTYy5iRhINORUZnI'
#bearer_token = os.getenv('BEARER_TOKEN')
#bearer_token = os.environ['BEARER_TOKEN']
print(bearer_token)
# Initialize the Kinesis client and set the stream name
kinesis_client = boto3.client('kinesis', region_name='us-west-2')
kinesis_stream_name = 'kinesis_twitter_stream'

# Initialize the tweet counter


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    #print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    #print(json.dumps(response.json()))


def set_rules():
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "(Itau OR Unibanco) lang:pt -is:retweet"}
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    #print(json.dumps(response.json()))


def get_stream():
    response = requests.get(
        #"https://api.twitter.com/2/tweets/search/stream", 
        "https://api.twitter.com/2/tweets/search/stream?tweet.fields=created_at",
        auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    tweet_count = 0
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print('\n\njson_response:')
            print(json.dumps(json_response, indent=4, sort_keys=True))

            msg_tweet=json.dumps(json_response["data"], indent=4, sort_keys=True)
            id_tweet=json.dumps(json_response["data"]["id"], indent=4, sort_keys=True)
            created_at=json.dumps(json_response["data"]["created_at"], indent=4, sort_keys=True)
            #msg_tweet=tweet["data"][0]["text"][0]
            #id_tweet=tweet["data"][0]["idt"][0]
            
            print(f'\nText Tweet é: \n{msg_tweet}')
            print(f"""\nid_tweet é: {id_tweet.replace('"','')}""")
            id_tweet=id_tweet.replace('"','')
            try:
                # Create a record for the Kinesis stream
                
                kinesis_record = {
                    'Data': msg_tweet,
                    'PartitionKey': int(id_tweet)
                }
                print(f'tipo kinesis_record é : {type(kinesis_record)}')
                
                print(f'tipo msg é : {type(msg_tweet)}')
                print(f'\nmsg é : {msg_tweet}')
                #print(f"Created at: {created_at[0,10,1]}")
                # Put the record into the Kinesis stream
                response = kinesis_client.put_record(StreamName=kinesis_stream_name, Data=msg_tweet,
                                                     PartitionKey=str(date.today()))
                                                        #PartitionKey=created_at[0,10,1])
                # Print the record being sent to Kinesis
                print(f"Sending record to Kinesis: {msg_tweet}")
                # Increment tweet counter
                tweet_count += 1
            except Exception as e:
                print(f"""Failed to send tweet with id {id_tweet} to Kinesis. Error: {e}""")
                
        


def main():
    rules = get_rules()
    delete_all_rules(rules)
    set_rules()
    get_stream()


if __name__ == "__main__":
    main()