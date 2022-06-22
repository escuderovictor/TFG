
# MyStreamListener
index_name = 'tweets_stream_mario'

# MyMaxStream
filter_words = ['Mario Strikers']
filter_languages = ['en']

# OffStream
cursor_filter = 'Mario Strikers'
cursor_since_date = '2022-06-19'
cursor_until_date = '2022-06-20'
cursor_language = 'en'
index_name_off = 'tweets_stream_mario'

#TweetInfo
platforms = {
            'Xbox': ['xbox', 'xbox series', 'xbox series x', 'xbox series s', 'xbox one', 'microsoft'],
            'Play Station': ['ps4', 'ps5', 'play station', 'sony', 'dual sense', 'dualsense', 'dual shock',
                             'dualshock'],
            'PC': ['steam', 'epic games', 'origin', 'graphic card', 'cpu'],
            'Nintendo Switch': ['nintendo', 'switch', 'joycon', 'eShop']
        }

topics = {
    'Precio': ['price', 'cost', 'valu', 'valuat', 'premium', 'charg', 'expens', 'cheap', 'cost', 'high-pric',
               'excess', 'exorbit'],
    'Gráficos': ['environ', 'appear', 'look', 'aspect', 'appear', 'impres', 'concept', 'art', 'beauti',
                 'pleasant'],
    'Rendimiento': ['perform', 'run', 'work', 'render', 'oper', 'feel', 'effici', 'execut'],
    'Dificultad': ['difficult', 'complic', 'difficulti', 'hard', 'abstrus', 'hardship', 'hurdl', 'impenetr',
                   'unfathom', 'exhaust', 'arduous', 'exasper', 'frustrat', 'simpl', 'painless', 'easy-peasi',
                   'friend', 'casua', 'light'],
    'Duración': ['length', 'durat', 'term', 'extent', 'short', 'concis']

}

