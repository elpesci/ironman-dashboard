import tweepy
#from data_utils import *
import pymongo

# twitter credentials
consumer_key="UWTWoiY04fgfWMmdJK96axbsz"
consumer_token="d9jtM8SVFyPxRYJpNSfRjtHMsWuz0tBJIszo4PNJvRHMw3Dtsl"

access_key = "2315641352-NBpeHxvMHJVvs0WIENpxmKOObdCwMWaFbbDhZoE"
access_token = "pS08ki553vq8so7XKbuzekn9Y0cPJtqS9ndi8DkCJFUC9"

# setting up mongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.users
coll = db.user

auth = tweepy.OAuthHandler(consumer_key,consumer_token)
auth.set_access_token(access_key, access_token)
api = tweepy.API(auth)


def get_or_create_user(userid):
    user = coll.find_one({"id_str":str(userid)})
    if user: return user
    else:
        coll.insert_one(api.get_user(id=userid)._json)
        return coll.find_one({"id_str":str(userid)})

"""
users = get_top_users("Aguascaliente","seguridad",sdate=get_days_ago(3))
for user in users:
    tempu = api.get_user(id=user[1])._json
    if not coll.find_one({"screen_name":tempu["screen_name"]}):
        coll.insert_one(tempu)
        print "inserted:",tempu["screen_name"]

"""

