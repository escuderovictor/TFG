import signal
import sys
import tweepy
import json
import pandas as pd
from keys import *
from elasticsearch import Elasticsearch
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

    def obtain_tweets(self, screen_name):

        api = tweepy.API(auth, wait_on_rate_limit=True)
        for i in screen_name:
            public_tweets = api.user_timeline(screen_name=i, count=tweets_off, include_rts=True,
                                              tweets_mode='extended')

        es = Elasticsearch([elastic_host])
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
                'polarity_avg': 0,
                'platform': '',
                'opinion': ''
            }

            TweetInfo().obtain_polarity(tweet_export)
            TweetInfo().clasify_platform(tweet_export)
            TweetInfo().clasify_opinion(tweet_export)
            print(tweet_export)

            es.index(index=index_name_off, id=tweet_export['id'], document=tweet_export)

        print('\nLast ', tweets_off, ' tweets of', screen_name, ' accounts indexed ✔ ')


class TweetInfo:

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
            tweet_export['polarity_avg'] = 'Negative'
        elif polarity > 0:
            tweet_export['polarity'] = polarity
            tweet_export['polarity_avg'] = 'Positive'
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
        print(text)
        stemmed = SnowballStemmer('english')
        stemmed_text = [stemmed.stem(i) for i in text]

        opinions = {
            'Price': ['price', 'cost', 'valu', 'valuat', 'premium', 'charg', 'expens', 'cheap'],
            'Graphics': ['environ', 'appear', 'look', 'aspect', 'appear', 'impres', 'concept'],
            'Performance': ['perform', 'run', 'work', 'render', 'oper', 'feel'],
            'Difficulty': ['difficult', 'complic', 'difficulti', 'hard', 'abstrus', 'hardship', 'hurdl'],
            'Length': ['length', 'durat', 'term', 'extent'],

        }
        opinion_aux = ''
        for tag, keywords in opinions.items():
            for i in text:
                if i in keywords:
                    opinion_aux = tag

        tweet_export['opinion'] = opinion_aux


class TextTreatment:

    def clean_translate(self, text):
        text = re.sub(r'https?:\/\/.\S+', "", text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'^RT[\s]+', '', text)
        text = text.lower()

        translator = Translator()
        tweet_trad = translator.translate(text, dest='en')
        tweet_trad = word_tokenize(tweet_trad.text)

        return tweet_trad


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

        text = 'expensive cheap'
        text = TextTreatment().clean_translate(text)
        print(text)
        stemmed = SnowballStemmer('english')

        stemmed_text = [stemmed.stem(i) for i in text]

        print(stemmed_text)
