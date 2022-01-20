import tweepy
import json

consumer_key = "8BvefOC1ydZ9zTXhddQexIf4T"
consumer_secret = "Zdcz0ToSLTvBcru3KLhrTftUkbqtw4nCU8te3N5T0ENnhC3wtV"

access_token = "253251337-ALmcpBN7ICriJnyGAMy0t24Pyg8TFPhrRTcnINCp"
access_token_secret = "i1dGHsWynzkLl1GyFfCnXc70J3dxqwBkZccblytN2F5uW"

callback_uri = 'oob'


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
        self.stream.filter(track=['Elden ring', 'eldenring', 'from software', 'basket'], languages=['es', 'en'])


class OffStream:

    def obtain_tweets(self, screen_name):
        api = tweepy.API(auth, wait_on_rate_limit=True)
        tweets_list = []
        tweets = api.user_timeline(screen_name=screen_name, count=100, include_rts=False, tweets_mode='extended')
        # print(tweets)
        try:
            with open('tweetsOffStream.json', 'a') as f:
                f.write(tweets)
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True


if __name__ == "__main__":
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
    auth.set_access_token(access_token, access_token_secret)

    print("Opción 1: Stream   Opción 2: Obtener Tweets")
    option = input()

    if option == "1":
        myListener = MyStreamListener()
        print('Recopilando tweets...')
        stream = MyMaxStream(auth, myListener)
        stream.start()
    elif option == "2":
        searcher = OffStream()
        searcher.obtain_tweets("ELDENRING")
    else:
        print("Opción Inválida")




