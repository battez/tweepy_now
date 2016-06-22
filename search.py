''' search twitter REST API 7 day window for tweets using Tweepy lib.
Some automated queries.
PIPELINE:
- read in a CSV  (single column) of query terms
- with this list of terms, fine-tune the query, dates, location etc.
- loop through all queries, giving time for rate limit to restart
- save to mongo db along with logs of queries
- use multiple index on mongodb 
- db.tweets_more.createIndex( {"text": "text", "entities.hashtags.text":"text"}, 
{"weights": { 'entities.hashtags.text': 3, 'text':1 }} )
'''
import sys
import os
import jsonpickle, json
from time import sleep

from pymongo import MongoClient


# basic logging for this task.
import logging
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(filename="search_log_aberdeenshire.txt", \
    level=logging.INFO, format=FORMAT)

TWITDIR = '/home/luke/programming/'

# get the Twitter API app Oauth tokens
sys.path.insert(0, TWITDIR)
import config

# Twitter Setup
import tweepy
from tweepy import OAuthHandler
auth = OAuthHandler(config.alt_consumer_key, config.alt_consumer_secret)
auth.set_access_token(config.alt_access_token, config.alt_access_secret)

# allows greater access speed
from tweepy import AppAuthHandler
auth_app = AppAuthHandler(config.alt_consumer_key, config.alt_consumer_secret)

# choose which of above auth methods we are using:
api = tweepy.API(auth_app, wait_on_rate_limit = True, \
    wait_on_rate_limit_notify = True )

# uncomment to get places etc
# api_oauth = tweepy.API(auth, wait_on_rate_limit = True, \
#     wait_on_rate_limit_notify = True )


# The JSON response from the Twitter API is available in the attribute 
# _json (with a leading underscore), which is not raw JSON but dictionary.
try:
    client = MongoClient(config.MONGO_URI)
except e:
    print ("Could not connect to MongoDB: %s" % e)

db = client['local']

# remote test
client_alt = MongoClient(config.MLAB_URI)
db_alt = client_alt.demo 


def process_or_store(tweet):
    '''do something with tweets we get from Twitter API'''
    collection = db_alt['tweet_aberdeen']
    try:
        collection.insert(tweet)
        # print('tweet was', tweet)
    except:
        logging.error('could not insert to db')

def csv_reader(file_obj):
    """
    Read a csv file
    """
    import csv
    reader = csv.reader(file_obj)
    lines = []
    for row in reader:
        lines.append(row[0].strip())
    return lines

if __name__ == '__main__':
    csv_file = 'scotland_place_plus_aberdeenplaceterm.csv'

    with open(csv_file, "r") as f_obj:
        queries = csv_reader(f_obj)
    # queries = ['☂', '☔']
    queries = ['tarland','feugh']
    max_tweets = 2500
    logging.info('max tweets: ' + str(max_tweets) + ' Queries:'+ ','.join(queries))
    since = " since:2016-06-14 "
    until = " until:2016-06-18 "  
    geos = {'midway_paris_sens':'48.5377029,2.4897794,30mi', \
    'centred_on_paris':'48.8589507,1.2269498,90mi', \
    'paris':'48.8589507,2.27751752,10mi', \
    'centred_on_aboyne': '57.0769745,-2.7927203,60mi'}
    geo = geos['centred_on_aboyne']
     # geocode – Returns tweets by users located within a given radius of
    # the given latitude/longitude. The location is preferentially taking from 
    #the Geotagging API, but will fall back to their Twitter profile. The 
    # parameter value is specified by “latitide,longitude,radius”
    # might need to do until Saturday date so get max sweep of Wed Thu Fri

    # Finetune query:  also crues, intemperies, pariscrue, crueparis, 
    qualify = since + until

    # places = api_oauth.geo_search(query="Aberdeen, United Kingdom",granularity="city")
    # place_id = places[0].id

    # print(place_id) # 6416b8512febefc9 uk; aberdeen: 73cc26d418860ddd

    # UPDATED code for a very broad place search ( do not use the geocode )
    # test these searches with Apigee website console for simplicity
    places = {'Scotland':'0af014accd6f6e99','UK':'6416b8512febefc9', 'Aberdeen':'73cc26d418860ddd'}
    place = ' place:' + places['Scotland']
    geo = None # disable this for this type of query
    qualify = qualify + place
    for query in queries:
        sleep(10) # in case we overstep our mongo lab free access; or 
        # if queries to twitter are too quickly getting zero results back, 
        # so we end up bombard the API
        print('processing...', query + qualify + str(geo))
        count = 0
        for status in tweepy.Cursor(api.search, \
            q=query + qualify, geocode=geo).items(max_tweets):
            # Process a single status
            process_or_store(status._json) # convenience: json from Status obj
            count += 1

        logging.info('Query returned: ' + str(count) + ' tweets =================')
        print(str(count))

