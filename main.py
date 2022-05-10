import signal
import sys
import tweepy
import json
from keys import *
from elasticsearch import Elasticsearch
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
from googletrans import Translator

pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows',None)


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_data(self, data):

        data_aux = json.loads(data)
        text = data_aux['text']
        text = re.sub(r'https?:\/\/.\S+', "", text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'^RT[\s]+', '', text)

        translator = Translator()
        twtraduction = translator.translate(text, dest='en')

        print(text)

        print(twtraduction.text)

        # date = data_aux['created_at']
        # date = datetime.strptime(date, '%a %b %d %H %z %Y')
        # # date = datetime.strftime(date, '%a %b %d')

        tweet_export = {
            'created_at': data_aux['created_at'],
            'id': data_aux['id'],
            # 'text': stemmed_text,
            'text': text,
            'user': data_aux['user']['screen_name'],
            'user_followers': data_aux['user']['followers_count'],
            'user_follows': data_aux['user']['friends_count'],
            'user_location': data_aux['user']['location'],
            'coordinates': data_aux['coordinates'],
            'retweets': data_aux['retweet_count'],
            'favourites': data_aux['favorite_count'],
            'opinion': 0,
            'opnionavg': 0
        }

        # print(tweet_export)

        es = Elasticsearch([elastic_host])

        aux = SentimentIntensityAnalyzer()

        polarity = aux.polarity_scores(twtraduction.text)['compound']
        print(polarity)

        if polarity < 0:
            tweet_export['opinion'] = polarity
            tweet_export['opinionavg'] = 'negative'
        elif polarity > 0:
            tweet_export['opinion'] = polarity
            tweet_export['opinionavg'] = 'positive'
        else:
            tweet_export['opinion'] = polarity
            tweet_export['opinionavg'] = 'neutral'

        es.index(index=index_name, id=tweet_export['id'], document=tweet_export)
        print('Tweet indexado ✔ \n')


class MyMaxStream:

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self):
        self.stream.filter(track=filter_words, languages=filter_languages)


class OffStream:

    def obtain_tweets(self, screen_name):

        api = tweepy.API(auth, wait_on_rate_limit=True)
        for i in screen_name:
            public_tweets = api.user_timeline(screen_name=i, count=tweets_index, include_rts=True, tweets_mode='extended')

        es = Elasticsearch([elastic_host])
        print('Conectado a elastic')
        for tweet in public_tweets:
            # translator = Translator()
            # twtraduction = translator.translate(tweet.text, dest='en')
            # print(twtraduction.text)
            tweet_export = {
                'created_at': tweet.created_at,
                'id': tweet.id,
                'text': tweet.text,
                'user': tweet.user.screen_name,
                'user_followers': tweet.user.followers_count,
                'user_follows': tweet.user.friends_count,
                'user_location': tweet.user.location,
                'retweets': tweet.retweet_count,
                'favourites': tweet.favorite_count
            }
            print(tweet_export['text'])

            # es.index(index=index_name_off, id=tweet_export['id'], document=tweet_export)

        print('Últimos', tweets_index,  'tweets de las cuentas ', screen_name, ' indexados ✔ ')


if __name__ == '__main__':

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
    auth.set_access_token(access_token, access_token_secret)

    def sigint_handler(signal, frame):
        print('\033[1m' + '⌨ Programa parado manualente ⌨ ' + '\033[0m')
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    # myListener = MyStreamListener()
    # print('\033[1m' + 'Recopilando tweets... ' + '\033[0m')
    # stream = MyMaxStream(auth, myListener)
    # stream.start()

    print('Opción 1: Stream   Opción 2: Obtener Tweets off stream   Opción 3: Test' )
    option = input()
    if option == '1':
        myListener = MyStreamListener()
        print('\nRecopilando tweets... \n')
        stream = MyMaxStream(auth, myListener)
        stream.start()
    elif option == '2':
        searcher = OffStream()
        searcher.obtain_tweets(user_tweets)
    elif option == '3':
        print('test')



