from nltk.stem import SnowballStemmer
from nltk import word_tokenize
import re

consumer_key = "8BvefOC1ydZ9zTXhddQexIf4T"
consumer_secret = "Zdcz0ToSLTvBcru3KLhrTftUkbqtw4nCU8te3N5T0ENnhC3wtV"
access_token = "253251337-ALmcpBN7ICriJnyGAMy0t24Pyg8TFPhrRTcnINCp"
access_token_secret = "i1dGHsWynzkLl1GyFfCnXc70J3dxqwBkZccblytN2F5uW"

callback_uri = 'oob'

filter_words = ['call of duty', 'warzone', 'modern warfare 2', 'mw2', 'cod', 'activision']
filter_languages = ['en']
user_tweets = ['powerbazinga', 'joseju']

index_name = 'tweets'
index_name_off = 'tweets_off_stream'
index_name_compound = 'tweets_compound'
tweets_index = 20
# elastic_host = {'host': 'localhost', 'port': 9200}
elastic_host = 'http://elastic:JvZpQ9D9JBMrza7KyHbW@localhost:9200'





