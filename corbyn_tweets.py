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
        self.db = sqlite3.connect('tweets.db')
        # Remove existing rows from db
        self.cursor = self.db.cursor()
        # deleting contents of the database without knowing what is in it is probably not good practice
        self.cursor.execute('''DELETE FROM tweets;''')
        self.db.commit()
        
    def parse_tweet(self,line):
        """ Extract information about tweet (line) and return as dict"""
        decoded_line = line.decode('utf-8')
        # print(decoded_line)
        try:
            tweet = json.loads(decoded_line)
        except:
            return None

        tmp = tweet
        if tweet['text'][:4] == 'RT @':
            try:
                tmp = tweet['retweeted_status']
            except:
                pprint(tweet)
            retweeted_status = True
        else:
            retweeted_status = False
        if 'extended_tweet' in tmp.keys():
            text = tmp['extended_tweet']['full_text']
        else:
            text = tmp['text']

        # SELECT strftime('%s','2004-01-01 02:34:56')
        # parsed = datetime.datetime.strptime('Tue Dec 19 22:10:03 +0000 2017', "%a %b %d %X %z %Y")
        # print(tweet['created_at'])

        extracted_info = {
            'user_name': tweet['user']['screen_name'],
            'tweet_text': text,
            'retweeted_status': retweeted_status,
            'in_reply_to': tweet['in_reply_to_screen_name'],
            'tweet_time': tweet['created_at'],
        }
        return extracted_info

    def insert_tweet_into_db(self,info):
        """ Insert tweet information into sqlite3 db"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO tweets(user_name, tweet_text, retweeted_status, in_reply_to, tweet_time)
            VALUES(:user_name, :tweet_text, :retweeted_status, :in_reply_to, :tweet_time)
            ''', (info))
        self.db.commit()

    def twitter_api_to_db(self):
        """ Wrapper for rest of the class.
        Gets twitter from the API, extracts information and inserts in sqlite3 db."""
        self.connect_to_db()
        
        r = self.start_stream()
        
        start_time = time.time()
        for line in r.iter_lines():
            if time.time() - start_time > self.seconds:
                break
            extracted_info = self.parse_tweet(line)
            if extracted_info != None:
                self.insert_tweet_into_db(extracted_info)
        self.db.close()


if __name__ == '__main__':
    # Set number of minutes' worth of tweets to record
    minutes = 1
    corbyn = tweets('Corbyn',minutes*60)
    corbyn.twitter_api_to_db()