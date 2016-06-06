''' search twitter REST API 7 day window for tweets using Tweepy lib.
Some automated queries.
'''
import sys
import os
import jsonpickle, json
from time import sleep

from pymongo import MongoClient


# basic logging for this task.
import logging
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(filename="search_log.txt", level=logging.INFO, format=FORMAT)

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

# The JSON response from the Twitter API is available in the attribute 
# _json (with a leading underscore), which is not raw JSON but dictionary.
try:
    client = MongoClient(config.MONGO_URI)
except e:
    print ("Could not connect to MongoDB: %s" % e)

db = client['Twitter']

# remote test
post = {"author": "Luke","text": "My first blog post!"}
client_alt = MongoClient(config.MLAB_URI)
db_alt = client_alt.demo 


def process_or_store(tweet):
    '''do something with tweets we get from Twitter API'''
    collection = db_alt['tweets']
    try:
        collection.insert(tweet)
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
csv_file = 'compiled_france.csv'
with open(csv_file, "r") as f_obj:
    queries = csv_reader(f_obj)

logging.info('Queries include:'+ ','.join(queries))
since = " since:2016-05-30 "
geos = {'midway_paris_sens':'48.5377029,2.4897794,30mi'}
geo = geos['midway_paris_sens']
 # geocode – Returns tweets by users located within a given radius of
# the given latitude/longitude. The location is preferentially taking from 
#the Geotagging API, but will fall back to their Twitter profile. The 
# parameter value is specified by “latitide,longitude,radius”
# might need to do until Saturday date so get max sweep of Wed Thu Fri
qualify = since
max_tweets = 2000
for query in queries:
    sleep(2) # in case we overstep our mongo lab free access
    print('processing...', query + ' geocode:' + geo)
    
    for status in tweepy.Cursor(api.search, \
        q=query + qualify, geocode=geo).items(max_tweets):
        # Process a single status
        process_or_store(status._json) # convenience: json from Status obj

