import signal
import sys
import tweepy
import json
import pandas as pd
from keys import *
from elasticsearch import Elasticsearch
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googletrans import Translator
from geopy.geocoders import ArcGIS


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_data(self, data):

        data_aux = json.loads(data)

        if (not data_aux['retweeted']) and ('RT @' not in data_aux['text']):
            date = pd.to_datetime(pd.Series(data_aux['created_at']))
            date_format = date.dt.strftime('%d/%m/%Y')
            tweet_export = {
                'created_at': date_format.values,
                'is_retweeted': data_aux['retweeted'],
                'id': data_aux['id'],
                'text': data_aux['text'],
                'user': data_aux['user']['screen_name'],
                'user_followers': data_aux['user']['followers_count'],
                'user_follows': data_aux['user']['friends_count'],
                'user_location': data_aux['user']['location'],
                'user_location_coordinates': 0,
                'retweets': data_aux['retweet_count'],
                'favourites': data_aux['favorite_count'],
                'polarity': 0,
                'polarity_avg': 0,
                'platform': '',
                'opinion': ''
            }

            TweetInfo().obtain_polarity(tweet_export)
            TweetInfo().clasify_platform(tweet_export)
            TweetInfo().clasify_opinion(tweet_export)

            print(tweet_export)

            es = Elasticsearch([elastic_host])
            es.index(index=index_name, id=tweet_export['id'], document=tweet_export)
            print('Indexed Tweet ✔ \n')


class MyMaxStream:

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self):
        self.stream.filter(track=filter_words, languages=filter_languages)


class OffStream:

    def obtain_tweets(self):

        api = tweepy.API(auth, wait_on_rate_limit=True)
        # for i in screen_name:
        #     public_tweets = api.user_timeline(screen_name=i, count=tweets_off, include_rts=True,
        #                                       tweets_mode='extended')

        for tweet in tweepy.Cursor(api.search, q='Elden ring', Since='2022-05-25', lang='en').items(3000):
            if (not tweet.retweeted) and ('RT @' not in tweet.text):
                date = pd.to_datetime(pd.Series(tweet.created_at))
                date_format = date.dt.strftime('%d/%m/%Y')
                tweet_export = {
                    'created_at': date_format.values,
                    'id': tweet.id,
                    'text': tweet.text,
                    'user': tweet.user.screen_name,
                    'user_followers': tweet.user.followers_count,
                    'user_follows': tweet.user.friends_count,
                    'user_location': tweet.user.location,
                    'retweets': tweet.retweet_count,
                    'favourites': tweet.favorite_count,
                    'polarity': 0,
                    'polarity_avg': 0,
                    'platform': '',
                    'opinion': ''
                }
                es = Elasticsearch([elastic_host])
                TweetInfo().obtain_polarity(tweet_export)
                TweetInfo().clasify_platform(tweet_export)
                TweetInfo().clasify_opinion(tweet_export)
                print(tweet_export)
                es.index(index=index_name_off, id=tweet_export['id'], document=tweet_export)


class TweetInfo:

    def obtain_polarity(self, tweet_export):

        text = tweet_export['text']
        text = re.sub(r'https?:\/\/.\S+', "", text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'^RT[\s]+', '', text)

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

    def clasify_platform(self, tweet_export):

        text = TextTreatment().clean_translate(tweet_export['text'])

        platforms = {
            'Xbox': ['xbox', 'xbox series', 'xbox series x', 'xbox series s', 'xbox one', 'microsoft'],
            'Play Station': ['ps4', 'ps5', 'play station', 'sony', 'dual sense', 'dualsense', 'dual shock',
                             'dualshock'],
            'PC': ['steam', 'epic games', 'origin', 'graphic card', 'cpu'],
            'Nintendo Switch': ['nintendo', 'switch', 'joycon', 'eShop']
        }
        platform_aux = ''
        for tag, keywords in platforms.items():
            for i in text:
                if i in keywords:
                    platform_aux = tag

        tweet_export['platform'] = platform_aux

    def clasify_opinion(self, tweet_export):

        text = TextTreatment().clean_translate(tweet_export['text'])
        stemmed = SnowballStemmer('english')
        stemmed_text = [stemmed.stem(i) for i in text]

        opinions = {
            'Precio': ['price', 'cost', 'valu', 'valuat', 'premium', 'charg', 'expens', 'cheap', 'cost', 'high-pric',
                       'excess', 'exorbit'],
            'Gráficos': ['environ', 'appear', 'look', 'aspect', 'appear', 'impres', 'concept', 'art', 'beauti',
                         'pleasant'],
            'Rendimiento': ['perform', 'run', 'work', 'render', 'oper', 'feel', 'effici', 'execut', 'display'],
            'Difcultad': ['difficult', 'complic', 'difficulti', 'hard', 'abstrus', 'hardship', 'hurdl', 'impenetr',
                          'unfathom', 'exhaust', 'arduous', 'exasper', 'frustrat', 'simpl', 'painless', 'easy-peasi',
                          'friend', 'casua', 'light'],
            'Duración': ['length', 'durat', 'term', 'extent', 'short', 'concis']

        }
        opinion_aux = ''
        for tag, keywords in opinions.items():
            for i in stemmed_text:
                if i in keywords:
                    opinion_aux = tag

        tweet_export['opinion'] = opinion_aux


class TextTreatment:

    def clean_translate(self, text):
        text = re.sub(r'https?:\/\/.\S+', "", text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'^RT[\s]+', '', text)
        text = text.lower()
        text = word_tokenize(text)
        return text


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
        searcher.obtain_tweets()
    elif option == '3':

        s1 = 'abc'
        s2 = '123'
        s1.join(s2)  # 1abc2abc3

        nom = ArcGIS()
        m = nom.geocode('None')
        p = m.latitude, m.longitude

        delimiter = ','
        b = '[]'
        e = ','.join([str(value) for value in p]).join('[]')

        print(e.join(b))
        print(e)

        print(m.latitude, m.longitude)
