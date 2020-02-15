import pandas as pd
import numpy as np
import json
import glob
import os
import chardet



SAVE_TWEET_PATH = 'TweetScraper/Chhapak/tweet/' #path where tweets json are present
SAVE_USER_PATH = 'TweetScraper/Chhapak/user/' #path where the user json are present
SAVE_TWEET_DB='CHAPPAK_DATA/'  #Path where the merged csv will be changes
SAVE_USER_DB='CHAPPAK_DATA/'
def readTweets():
	files=glob.iglob(SAVE_TWEET_PATH+'**/*',recursive=True)
	tweets_list=[]

	for __file__ in files:

		## Get encoding for the file
		with open(__file__,'rb') as f:
			result = chardet.detect(f.read())
			print(result)
		try:
			with open(__file__,encoding=result['encoding']) as f:
				d = json.load(f)
				tweets_list.append(d)
		except:
			pass
	return pd.DataFrame(tweets_list)

def readUsers():
	files=glob.iglob(SAVE_USER_PATH+'**/*',recursive=True)
	users_list=[]

	for __file__ in files:

		with open(__file__) as f:
			d = json.load(f)
			users_list.append(d)
	return pd.DataFrame(users_list)


def saveUsers(data):
	if not os.path.exists(SAVE_USER_DB):
		os.mkdir(SAVE_USER_DB)
	data.to_csv(SAVE_USER_DB+"Users.csv",encoding='utf-8',index=False)




def saveTweets(data):
	if not os.path.exists(SAVE_TWEET_DB):
		os.makedirs(SAVE_TWEET_DB)
	data.to_csv(SAVE_TWEET_DB+'Tweets.csv',encoding='utf-8',index=False)




if __name__ == '__main__':
	data=readTweets()
	saveTweets(data)
