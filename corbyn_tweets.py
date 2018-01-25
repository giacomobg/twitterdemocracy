import credentials
import json,time,requests
from requests_oauthlib import OAuth1
from pprint import pprint
import sqlite3

class tweets():
    """docstring for tweets"""
    def __init__(self, search_term,seconds):
        self.search_term = search_term
        self.seconds = seconds

    def start_stream(self):
        """ Starts stream of tweets about Corbyn"""
        filter_params = {'track': self.search_term}
        url = 'https://stream.twitter.com/1.1/statuses/filter.json'
        auth = OAuth1(credentials.consumer_key, credentials.consumer_secret, credentials.access_token, credentials.access_token_secret)

        r = requests.get(url,auth=auth, stream=True, params=filter_params)
        print(r.status_code)
        return r

    def connect_to_db(self):
        """ Connect to sqlite3 db and remove existing rows"""
        self.db = sqlite3.connect(self.search_term+'.db')
        # Remove existing rows from db
        self.cursor = self.db.cursor()
        # delete tweets table if it exists
        self.cursor.execute('''DROP TABLE IF EXISTS tweets;''')
        # create tweets table
        self.cursor.execute('''
                                CREATE TABLE tweets (
                                    num PRIMARY KEY,
                                    user_name text,
                                    tweet_text text,
                                    in_reply_to text,
                                    tweet_time time,
                                    tweet_object text
                                );
                            ''')
        self.db.commit()
        
    def parse_tweet(self,line):
        """ Extract information about tweet (line) and return as dict"""
        decoded_line = line.decode('utf-8')
        # print(decoded_line)
        try:
            tweet = json.loads(decoded_line)
        except:
            return None

        # There must be a simpler way to figure out if a tweet has been retweeted?
        tmp = tweet
        if 'retweeted_status' in tmp.keys():
            return None
        if 'extended_tweet' in tmp.keys():
            try:
                text = tmp['extended_tweet']['full_text']
            except:
                pprint(tmp)
        else:
            try:
                text = tmp['text']
            except:
                pprint(tmp)

        extracted_info = {
            'num': self.counter,
            'user_name': tweet['user']['screen_name'],
            'tweet_text': text,
            'in_reply_to': tweet['in_reply_to_screen_name'],
            'tweet_time': tweet['created_at'],
            'tweet_object': decoded_line
        }
        return extracted_info

    def insert_tweet_into_db(self,info):
        """ Insert tweet information into sqlite3 db"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO tweets(num, user_name, tweet_text, in_reply_to, tweet_time, tweet_object)
            VALUES(:num, :user_name, :tweet_text, :in_reply_to, :tweet_time, :tweet_object)
            ''', (info))
        self.db.commit()

    def twitter_api_to_db(self):
        """ Wrapper for rest of the class.
        Gets twitter from the API, extracts information and inserts in sqlite3 db."""
        self.connect_to_db()
        
        r = self.start_stream()
        
        start_time = time.time()
        self.counter = 0
        for line in r.iter_lines():
            # # Comment out to run ad infinitum
            # if time.time() - start_time > self.seconds:
            #     break
            extracted_info = self.parse_tweet(line)
            if extracted_info != None:
                self.insert_tweet_into_db(extracted_info)
                self.counter += 1
        self.db.close()


if __name__ == '__main__':
    # Set number of minutes' worth of tweets to record
    minutes = 1
    corbyn = tweets('UKIP',minutes*60)
    corbyn.twitter_api_to_db()