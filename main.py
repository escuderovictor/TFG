import signal
import sys
from keys import *
from config import *

import tweepy
import json
import pandas as pd
import re
from elasticsearch import Elasticsearch
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import SnowballStemmer


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_data(self, data):

        tweet = json.loads(data)

        if (not tweet['retweeted']) and ('RT @' not in tweet['text']):
            date = pd.to_datetime(pd.Series(tweet['created_at']))
            date_format = date.dt.strftime('%d/%m/%Y %Hh')
            tweet_export = {
                'created_at': date_format.values,
                'id': tweet['id'],
                'text': tweet['text'],
                'user': tweet['user']['screen_name'],
                'user_followers': tweet['user']['followers_count'],
                'user_follows': tweet['user']['friends_count'],
                'retweets': tweet['retweet_count'],
                'favourites': tweet['favorite_count'],
                'polarity': 0,
                'polarity_avg': 0,
                'platform': '',
                'topic': ''
            }

            TweetInfo().obtain_polarity(tweet_export)
            TweetInfo().classify_platform(tweet_export)
            TweetInfo().classify_topic(tweet_export)

            es = Elasticsearch([elastic_host])
            es.index(index=index_name, id=tweet_export['id'], document=tweet_export)


class MyMaxStream:

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self):
        self.stream.filter(track=filter_words, languages=filter_languages)


class OffStream:

    def obtain_tweets(self):

        for tweet in tweepy.Cursor(api.search, q=cursor_filter, since=cursor_since_date, until=cursor_until_date,
                                   lang=cursor_language).items(3000):

            if (not tweet.retweeted) and ('RT @' not in tweet.text):
                date = pd.to_datetime(pd.Series(tweet.created_at))
                date_format = date.dt.strftime('%d/%m/%Y %Hh')
                tweet_export = {
                    'created_at': date_format.values,
                    'id': tweet.id,
                    'text': tweet.text,
                    'user': tweet.user.screen_name,
                    'user_followers': tweet.user.followers_count,
                    'user_follows': tweet.user.friends_count,
                    'retweets': tweet.retweet_count,
                    'favourites': tweet.favorite_count,
                    'polarity': 0,
                    'polarity_avg': 0,
                    'platform': '',
                    'topic': ''
                }

                TweetInfo().obtain_polarity(tweet_export)
                TweetInfo().classify_platform(tweet_export)
                TweetInfo().classify_topic(tweet_export)

                es = Elasticsearch([elastic_host])
                es.index(index=index_name_off, id=tweet_export['id'], document=tweet_export)


class TweetInfo:

    def obtain_polarity(self, tweet_export):

        text = tweet_export['text']
        text = re.sub(r'https?:\/\/.\S+', "", text)
        text = re.sub(r'[^a-zA-Z0-9]', ' ', text)

        aux = SentimentIntensityAnalyzer()

        polarity = aux.polarity_scores(text)['compound']

        if polarity < 0:
            tweet_export['polarity'] = polarity
            tweet_export['polarity_avg'] = 'Negativo'
        elif polarity > 0:
            tweet_export['polarity'] = polarity
            tweet_export['polarity_avg'] = 'Positivo'
        else:
            tweet_export['polarity'] = polarity
            tweet_export['polarity_avg'] = 'Neutral'

    def classify_platform(self, tweet_export):

        text = TextTreatment().clean_text(tweet_export['text'])

        platform_aux = ''
        for tag, keywords in platforms.items():
            for i in text:
                if i in keywords:
                    platform_aux = tag

        tweet_export['platform'] = platform_aux

    def classify_topic(self, tweet_export):

        text = TextTreatment().clean_text(tweet_export['text'])
        stemmed = SnowballStemmer('english')
        stemmed_text = [stemmed.stem(i) for i in text]

        topic_aux = ''
        for tag, keywords in topics.items():
            for i in stemmed_text:
                if i in keywords:
                    topic_aux = tag

        tweet_export['text'] = stemmed_text
        tweet_export['topic'] = topic_aux


class TextTreatment:

    def clean_text(self, text):

        text = re.sub(r'https?:\/\/.\S+', '', text)
        text = re.sub(r'[^a-zA-Z0-9]', ' ', text)

        text = text.lower()
        text = word_tokenize(text)
        return text


if __name__ == '__main__':

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_url)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)

    def sigint_handler(signal, frame):
        print('\033[1m' + '⌨ Program stopped manually ⌨ ' + '\033[0m')
        sys.exit(0)


    signal.signal(signal.SIGINT, sigint_handler)

    print('Option 1: Stream   Option 2: Obtain off stream Tweets')
    option = input()
    if option == '1':

        myListener = MyStreamListener()
        stream = MyMaxStream(auth, myListener)
        stream.start()

    elif option == '2':

        searcher = OffStream()
        searcher.obtain_tweets()
