import tweepy
import keys
import json
import pandas as pd
from keys import *
from elasticsearch import Elasticsearch

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False

    def on_data(self, data):
        try:
            with open('tweets.json', 'a') as f:
                f.write(data+ ',')
                print ('Tweet añadido ✔')
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True


class MyMaxStream:

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth=auth, listener=listener)

    def start(self):
        self.stream.filter(track=word_filter, languages=languages_filter)


class OffStream:

    def obtain_tweets(self, screen_name):

        api = tweepy.API(auth, wait_on_rate_limit=True)
        public_tweets = api.user_timeline(screen_name=screen_name, count=100, include_rts=False, tweets_mode='extended')

        # create dataframe
        columns = ['created_at', 'id', 'text', 'screen_name']
        data = []
        for tweet in public_tweets:
            data.append([tweet.created_at, tweet.id, tweet.text, tweet.user.screen_name])

        df = pd.DataFrame(data, columns=columns)

        df.to_csv('tweetsOffStream.csv')
        csv_data = pd.read_csv("tweetsOffStream.csv", sep=",")
        csv_data.to_json("tweetsOffStream.json", orient="records")


if __name__ == "__main__":

    callback_uri = 'oob'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
    auth.set_access_token(access_token, access_token_secret)

    try:
        es = Elasticsearch({'host': 'localhost', 'port': 9200})
        print("Conectado a Elastic")
    except BaseException as e:
        print("Error on_data: %s" % str(e))

    print("Opción 1: Stream   Opción 2: Obtener Tweets")
    option = input()

    if option == "1":
        myListener = MyStreamListener()
        print('Recopilando tweets...')
        stream = MyMaxStream(auth, myListener)
        stream.start()
    elif option == "2":
        searcher = OffStream()
        searcher.obtain_tweets(twitter_profile)
    else:
        print("Opción Inválida")




