#!C:\Users\Ritesh\PycharmProjects\MyPro\venv\Scripts\python.exe
import sys
import pandas as pd
import datetime
import urllib
import webbrowser as wb
import tweepy
from tweepy import API
from tweepy import Cursor


consumer_key = 'x1MmILheA2rZUOt3ASe8Ml3Ay'
consumer_secret = 'SALsd26Rqdlemn2qgShY9Nuc4nwIrrfxhmwOyq6SSmpzk5JPxf'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

wb.open_new_tab(auth.get_authorization_url())
pin = input('Verification Oauth number from Redirect Url: ').strip()

token = auth.get_access_token(verifier=pin)

auth.set_access_token(token[0], token[1])
twitter_client = API(auth)

data = [{'id': data.id_str, 'created_at': data.created_at, 'name': data.user.name, 'location': data.user.location,
         'text': data.text.encode("utf-8"), 'retweet_count': data.retweet_count,
         'favorite_count': data.favorite_count, 'followers_count': data.user.followers_count,
         'status_count': data.user.statuses_count,
         'profile_background_image': data.user.profile_background_image_url_https,
         'profile_image_url_https': data.user.profile_image_url_https} for data in
        Cursor(twitter_client.user_timeline).items()]

twitter_data = pd.DataFrame(data)
images_url = []
for item in Cursor(twitter_client.user_timeline).items():
    try:
        images_url.append(list(list(item.entities.values())[-1][0].values())[4])
    except:
        images_url.append('')
twitter_data['images_url'] = images_url
try:
    for index, item in enumerate(images_url):
        urllib.request.urlretrieve(str(item),'C:\\Users\\Ritesh\\Downloads\\twitter\\twitter_images\\' + str(index) + '.jpg')
except Exception as e:
    pass
twitter_data.to_excel('C:\\Users\\Ritesh\\Downloads\\twitter\\twitter_data__'+str(datetime.datetime.now().date())+'.xlsx')
