import signal
import sys
import tweepy
import json
from keys import *
from elasticsearch import Elasticsearch
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googletrans import Translator


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_data(self, data):

        data_aux = json.loads(data)

        date = pd.to_datetime(pd.Series(data_aux['created_at']))
        date_format = date.dt.strftime('%d/%m/%Y')

        tweet_export = {
            'created_at': date_format.values,
            'id': data_aux['id'],
            'text': data_aux['text'],
            'user': data_aux['user']['screen_name'],
            'user_followers': data_aux['user']['followers_count'],
            'user_follows': data_aux['user']['friends_count'],
            'user_location': data_aux['user']['location'],
            'retweets': data_aux['retweet_count'],
            'favourites': data_aux['favorite_count'],
            'polarity': 0,
            'polarity_avg': 0
        }

        polarity = Polarity()
        polarity.obtain_polarity(tweet_export)
        print(tweet_export)

        es = Elasticsearch([elastic_host])
        es.index(index=index_name, id=tweet_export['id'], document=tweet_export)
        print('Indexed Tweet ✔ \n')


class OffStream:

    def obtain_tweets(self, screen_name):

        api = tweepy.API(auth, wait_on_rate_limit=True)
        for i in screen_name:
            public_tweets = api.user_timeline(screen_name=i, count=tweets_index, include_rts=True,
                                              tweets_mode='extended')

        es = Elasticsearch([elastic_host])
        print('Connected to Elastic')
        for tweet in public_tweets:

            tweet_export = {
                'created_at': tweet.created_at,
                'id': tweet.id,
                'text': tweet.text,
                'user': tweet.user.screen_name,
                'user_followers': tweet.user.followers_count,
                'user_follows': tweet.user.friends_count,
                'user_location': tweet.user.location,
                'retweets': tweet.retweet_count,
                'favourites': tweet.favorite_count,
                'polarity': 0,
                'polarity_avg': 0
            }
            polarity = Polarity()
            polarity.obtain_polarity(tweet_export)
            print(tweet_export)

            es.index(index=index_name_off, id=tweet_export['id'], document=tweet_export)

        print('Last ', tweets_index, ' tweets of', screen_name, ' accounts indexed ✔ ')


class Polarity:

    def obtain_polarity(self, tweet_export):
        text = tweet_export['text']
        text = re.sub(r'https?:\/\/.\S+', "", text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'^RT[\s]+', '', text)

        translator = Translator()
        tweet_trad = translator.translate(text, dest='en')

        aux = SentimentIntensityAnalyzer()

        polarity = aux.polarity_scores(tweet_trad.text)['compound']

        if polarity < 0:
            tweet_export['polarity'] = polarity
            tweet_export['polarity_avg'] = 'negative'
        elif polarity > 0:
            tweet_export['polarity'] = polarity
            tweet_export['polarity_avg'] = 'positive'
        else:
            tweet_export['polarity'] = polarity
            tweet_export['polarity_avg'] = 'neutral'


class MyMaxStream:

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self):
        self.stream.filter(track=filter_words, languages=filter_languages)


if __name__ == '__main__':

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
    auth.set_access_token(access_token, access_token_secret)

    def sigint_handler(signal, frame):
        print('\033[1m' + '⌨ Program stopped manually ⌨ ' + '\033[0m')
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    print('Option 1: Stream   Option 2: Obtain off stream Tweets   Option 3: Test')
    option = input()
    if option == '1':
        myListener = MyStreamListener()
        print('\nCollecting tweets... \n')
        stream = MyMaxStream(auth, myListener)
        stream.start()
    elif option == '2':
        searcher = OffStream()
        searcher.obtain_tweets(user_tweets)
    elif option == '3':
        print('option test')
