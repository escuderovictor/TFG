import signal
import sys
import tweepy
import json
from nltk.sentiment import SentimentIntensityAnalyzer
from keys import *
from elasticsearch import Elasticsearch
from sentiment_analysis_spanish import sentiment_analysis
from pysentimiento import create_analyzer


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_data(self, data):

        # stemmed = SnowballStemmer("spanish")
        data_aux = json.loads(data)
        text = data_aux["text"]
        text = text.lower()
        text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        text = re.sub(r"[^a-zA-Z0-9]", " ", text)
        # text = word_tokenize(text)    #Separa el tweet en palabras
        # stemmed_text = [stemmed.stem(i) for i in word_tokenize(text)]

        tweet_export = {
            "created_at": data_aux["created_at"],
            "id": data_aux["id"],
            # "text": stemmed_text,
            "text": text,
            "user": data_aux["user"]["screen_name"],
            "user_followers": data_aux["user"]["followers_count"],
            "user_follows": data_aux["user"]["friends_count"],
            "user_location": data_aux["user"]["location"],
            "retweets": data_aux["retweet_count"],
            "favourites": data_aux["favorite_count"]
        }

        print(tweet_export)
        es = Elasticsearch([elastic_host])

        aux = SentimentIntensityAnalyzer()  # Analisis de opinion positiva o negativa en ingles

        print(aux.polarity_scores(tweet_export["text"])['compound'])

        if aux.polarity_scores(tweet_export["text"])['compound'] < 0:
            opinion = {'op': 'positive'}
        elif aux.polarity_scores(tweet_export["text"])['compound'] > 0:
            opinion = {'op': 'negative'}
        else:
            opinion = {'op': 'neutral'}

        es.index(index=index_name_compound, id=tweet_export["id"], document=opinion)
        es.index(index=index_name, id=tweet_export["id"], document=tweet_export)
        print('Tweet indexado ✔ \n')


class Classifier:

    def nltkSentiment(self, text):
        aux = SentimentIntensityAnalyzer()
        print(aux.polarity_scores(text))

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
            tweet_export = {
                "created_at": tweet.created_at,
                "id": tweet.id,
                "text": tweet.text,
                "user": tweet.user.screen_name,
                "user_followers": tweet.user.followers_count,
                "user_follows": tweet.user.friends_count,
                "user_location": tweet.user.location,
                "retweets": tweet.retweet_count,
                "favourites": tweet.favorite_count
            }

            es.index(index=index_name_off, id=tweet_export['id'], document=tweet_export)

        print('Últimos', tweets_index,  'tweets de las cuentas ', screen_name, ' indexados ✔ ')

    def lematz(self, text):

        stemmed = SnowballStemmer("spanish")
        text = text.lower()
        text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        text = re.sub(r"[^a-zA-Z0-9]", " ", text)
        stemmed_text = [stemmed.stem(i) for i in word_tokenize(text)]

        print(stemmed_text)


if __name__ == "__main__":

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

    print("Opción 1: Stream   Opción 2: Obtener Tweets off stream   Opción 3: Test" )
    option = input()
    if option == '1':
        myListener = MyStreamListener()
        print('Recopilando tweets...')
        stream = MyMaxStream(auth, myListener)
        stream.start()
    elif option == '2':
        # Esta opcion obtiene los tweets de la cuenta pasada por parametro y los indexa en elastic
        searcher = OffStream()
        searcher.obtain_tweets(user_tweets)
    elif option == '3':

        # sentiment = sentiment_analysis.SentimentAnalysisSpanish()
        # print(sentiment.sentiment('modern warfare 2 es un juego para niños'))   # Positive ~ 1 / Negative ~ 0
        #
        # analyzer = create_analyzer(task="sentiment", lang="es")
        # analyzer.predict('modern warfare 2 es un juego para niños')
