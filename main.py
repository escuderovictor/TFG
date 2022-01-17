import tweepy
import json

consumer_key = "8BvefOC1ydZ9zTXhddQexIf4T"
consumer_secret = "Zdcz0ToSLTvBcru3KLhrTftUkbqtw4nCU8te3N5T0ENnhC3wtV"

access_token = "253251337-ALmcpBN7ICriJnyGAMy0t24Pyg8TFPhrRTcnINCp"
access_token_secret = "i1dGHsWynzkLl1GyFfCnXc70J3dxqwBkZccblytN2F5uW"

callback_uri = 'oob'


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.user.screen_name + " tweeted:" + status.text)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False


class MyMaxStream:

        def __init__(self, auth, listener):
            self.stream = tweepy.Stream(auth=auth, listener=listener)

        def start(self):
            self.stream.filter(track= ['Elden ring', 'eldenring', 'from software'], languages=['es', 'en'])


if __name__ == "__main__":
    myListener = MyStreamListener()

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
    auth.set_access_token(access_token, access_token_secret)

    stream = MyMaxStream(auth, myListener)
    stream.start()
