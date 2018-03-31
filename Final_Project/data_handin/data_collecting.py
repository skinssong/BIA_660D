
# coding: utf-8

# # connect to sql server to store tweepy result
from secrets import SQL_UID, SQL_PWD, WATSON_UNAME, WATSON_PWD, ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
import pyodbc

conn = pyodbc.connect(
    r'DRIVER={SQL Server};'
    r'SERVER=DESKTOP-JJ15EJV;'
    r'DATABASE=KAIJU;'
    r'UID={};'.format(SQL_UID)
    r'PWD={};'.format(SQL_PWD)
)

cursor = conn.cursor()

# # connect to mongo db

import pymongo
Client = pymongo.MongoClient()

db = Client["KAIJU"]
collection_db = db["tweets"]


# # Connection to Waston_analysis

# In[4]:

import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions


# In[5]:


natural_language_understanding = NaturalLanguageUnderstandingV1(
  username=WATSON_UNAME,
  password=WATSON_PWD,
  version='2017-02-27')

def NLP_analyze(text):
    response = natural_language_understanding.analyze(
      text=text,
      features=Features(
        entities=EntitiesOptions(
          emotion=True,
          sentiment=True,
          limit=3),
        keywords=KeywordsOptions(
          emotion=True,
          sentiment=True,
          limit=3)))
    return response


# In[ ]:


test = 'Looks like Pacific Rim: Uprising will not top the first one, which made $112M in 2013. All Hollywood movies failed to top Indian movie Secret Superstar in the first quarter of 2018. '
NLP_analyze(test)


# # connection to twitter

# In[6]:


from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import regex as re

# In[8]:


def parse_tweet(raw_data):
    query = """INSERT INTO KAIJU_TWEET (TweetID, TweetTime, TweetText, TweetLang, TimeZone, FollowerCount) VALUES ('{}',SYSUTCDATETIME(),'{}','{}','{}',{})"""
    data = json.loads(raw_data)
    tweet_id = data['id_str']
    tweet_text = str(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|(RT +)", " ",data['text']).split(' ')))
    tweet_lang = data['lang']
    time_zone = data['user']['time_zone']
    followers_count = data['user']['followers_count']
    print((tweet_id, tweet_text, tweet_lang, time_zone))
    final_q = query.format(tweet_id, tweet_text, tweet_lang, time_zone, followers_count)
    if tweet_lang == 'en':
        NLP_result = NLP_analyze(tweet_text)
        NLP_result['TweetID'] = tweet_id
        collection_db.insert_one(NLP_result)
        cursor.execute(final_q)
        conn.commit()


# In[9]:


class listener(StreamListener):
    
    def on_data(self, raw_data):
        try:
            parse_tweet(raw_data)
            return True
        except BaseException as e:
            print(str(e))
            time.sleep(1)

    def on_error(self, status_code):
        print(status_code)
        pass
    
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

twitterStream = Stream(auth, listener())


twitterStream.filter(track=['Pacific Rim'])
