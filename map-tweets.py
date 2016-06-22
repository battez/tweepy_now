'''
    - get all tweets in order of date which had a coordinate
    - map them out 
    - also get all bounding boxes tweets in order ~ 1100
    - d= new Date('2016-06-15');
    db.getCollection('tweet_aber_process')
    .find({'date_created_at':{$gt:d},$or:[{'place.bounding_box':{$exists:true}}, {'coordinates.type':{$exists:true}}]})
    .sort({'date_created_at':1});
'''
import sys
import os
import json
import folium
from pymongo import MongoClient, errors

TWITDIR = '/home/luke/programming/'

# get the Twitter API app Oauth tokens
sys.path.insert(0, TWITDIR)
import config

try:
    client = MongoClient(config.MLAB_URI)
except pymongo.errors.ConnectionFailure as e:
    print ("Could not connect to MongoDB: %s" % e)

db = client.demo 

tweets = db.tweet_aber_process

from datetime import datetime
# start = datetime.strptime("15/06/16 00:00", "%d/%m/%y %H:%M")
start = datetime(2016, 6, 15, 0, 0, 0)
cursor = tweets.find({'date_created_at':{'$gt':start},\
    '$or':[{'place.bounding_box':{'$exists':True}}, \
    {'coordinates.type':{'$exists':True}}]})\
    .sort([('date_created_at',1)])



# centre the map on:
origin = [57.0769745,-2.7927203] # aboyne
map_osm = folium.Map(location=origin, zoom_start=9)



#add markers
not_geo = 0
for tweet in cursor[:4]:
    if not tweet['geo']:
        not_geo += 1
        
    else:
        coords = tweet['geo']['coordinates'][0], tweet['geo']['coordinates'][1]
        map_osm.simple_marker(location=coords, popup=tweet['text'] \
            + ' DATE:' + tweet['created_at'])
    #folium.Marker(tweet).add_to(map_osm)
map_osm.save(outfile='foliage/osm.html')
print(not_geo)
#add lines
#folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(map_osm)