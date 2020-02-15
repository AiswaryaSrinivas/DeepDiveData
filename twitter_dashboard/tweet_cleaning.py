import pandas as pd
import numpy as np

from nltk.sentiment.util import *

from nltk import tokenize

from textblob import TextBlob

import sys


import string
from nltk.corpus import stopwords


from nltk.stem import PorterStemmer


STOPWORDS=stopwords.words("english")
STOPWORDS.append("with")

ps = PorterStemmer()

sys.path.append("TwitterEmotion/")

from TwitterEmotion.emotion_predictor import EmotionPredictor
import TwitterEmotion
## Function to remove URL from tweets
def removeURL(text,replace_text=""):
    re_url="http(\S+)*|\S+\.com\S+|bit.ly\S+|\S+utm_source\S+|bit\.ly(\S+)*|ow\.ly(\S+)*" #\S+ matched all non-whitespace characters
    return re.sub(re_url,replace_text,text)

## Remove any kind of user mention from tweet
def removeUserMentions(text,replace_text=""):
    re_usermentions="^@\w{1,15}|@\w{1,15}"
    return re.sub(re_usermentions,replace_text,text)

## Remove any HashTag present in the tweet
def removeHashTag(text,replace_text=""):
    re_hashtag="#\S+"
    return re.sub(re_hashtag,replace_text,text)

def getSenti(polarity):
    if polarity>0:
        return "positive"
    if polarity<0:
        return "negative"
    return "neutral"
import string
import re
from nltk.stem import PorterStemmer



def clean_text(text):
    ps=PorterStemmer()
    text = text.translate(str.maketrans({key: " {0} ".format(key) for key in string.punctuation}))
    #remove extra white space

    text_cleaned="".join([x for x in text if x not in string.punctuation])

    text_cleaned=re.sub(' +', ' ', text_cleaned)
    text_cleaned=re.sub(r'[^\x00-\x7F]+',' ', text_cleaned)
    text_cleaned=text_cleaned.lower()
    tokens=text_cleaned.split(" ")
    tokens=[token for token in tokens if token not in STOPWORDS]
    text_cleaned=" ".join([ps.stem(token) for token in tokens])


    return text_cleaned


def getEmotionModel(method="ekman",setting="mc"):
    return EmotionPredictor(classification=method, setting=setting)
def detectEmotion(tweet,model):

    return model.predict_classes([tweet])['Emotion'].tolist()[0]

if __name__ == '__main__':
    tweets=pd.read_csv("/Users/aiswarya/DataScienceArena/deep_dive_analytics/twitter_dashboard/TweetScraper-master/CHAPPAK_DATA/Tweets.csv",encoding="utf-8")
    tweets['cleaned_tweet']=tweets['text'].apply(lambda x:removeUserMentions(x))
    tweets['cleaned_tweet']=tweets['cleaned_tweet'].apply(lambda x:removeURL(x))
    tweets['cleaned_tweet']=tweets['cleaned_tweet'].apply(lambda x:removeHashTag(x))
    tweets['score']=tweets['cleaned_tweet'].apply(lambda x:TextBlob(x).sentiment)
    tweets['polarity']=tweets['score'].apply(lambda x:x.polarity)
    tweets['subjectivity']=tweets['score'].apply(lambda x:x.subjectivity)
    tweets['sentiment']=tweets['polarity'].apply(lambda x:getSenti(x))
    tweets['cleaned_tweet']=tweets['cleaned_tweet'].apply(lambda x:clean_text(x))
    print("Detecting Moods")
    model=getEmotionModel()
    tweets['ekman_mood']=tweets['text'].apply(lambda x:detectEmotion(x,model))
    model_2=getEmotionModel(method="plutchik")
    tweets['plutchik_mood']=tweets['text'].apply(lambda x:detectEmotion(x,model_2))

    tweets.to_csv("Chhapak_Tweets_Sentiment.csv",index=False,encoding="utf-8")
