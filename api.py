import os, sys
import string
import random
import urllib
import datetime
import openpyxl
import requests
import json
import six
import flask
import serializers
import shutil
import logging
import pandas as pd
import webbrowser as wb
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from flask import Flask, flash, redirect, render_template, request, session, url_for,send_file
from oauth2client import client, GOOGLE_TOKEN_URI
from oauth2client.client import flow_from_clientsecrets,GoogleCredentials
from flask_session import Session
from tempfile import mkdtemp
from google.auth import _helpers,credentials,exceptions
from google.oauth2 import _client
from config import *

import tweepy
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from twython import Twython, TwythonAuthError, TwythonError, TwythonRateLimitError
from instagram.client import InstagramAPI


SCOPES = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/plus.profile.agerange.read https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/plus.stream.write https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/plus.profile.language.read https://www.googleapis.com/auth/drive.metadata.readonly'

API_SERVICE_NAME = API_SERVICE_NAME
API_VERSION = 'v1'
CLIENT_SECRETS_FILE = "client_secret.json"


dir_path = os.path.dirname(os.path.realpath(__file__))+'\\'
# dir_path = 'C:\\Users\\Ritesh\\Downloads\\'


try:
    if os.path.exists(dir_path + 'logs'):
        shutil.rmtree(dir_path + 'logs')
except:
    pass
try:
    if not os.path.exists(dir_path + 'logs'):
        os.makedirs(dir_path + 'logs')
        f = open(dir_path +'logs\\app_logs','w+')
except:
    pass

log_lvl_val = 20
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',level=log_lvl_val,filename=dir_path+'logs\\app_logs')
log = logging.getLogger(__file__)

#------------------------------------------------------------------------------------------------------------------

app = flask.Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits)for x in range(32))

twitter_consumer_key = 'x1MmILheA2rZUOt3ASe8Ml3Ay'
twitter_consumer_secret = 'SALsd26Rqdlemn2qgShY9Nuc4nwIrrfxhmwOyq6SSmpzk5JPxf'

BASE_URL = 'https://api.instagram.com/v1/'
# configure Instagram API
instaConfig = {
    'client_id': '4c9486f3ca62407b89fa39dc6bb45ca8',
    'client_secret':'99fe3d35529e4f75aec835be6b5b175f',
    'redirect_uri':'http://127.0.0.1:5000/instagram'
}
api = InstagramAPI(**instaConfig)


@app.route('/')
def index():
    log.info("In the Index Page...........")
    try:
        os.remove(dir_path +'logs.zip')
    except:
        pass
    try:
        os.remove(dir_path +'twitter.zip')
        log.info("Twitter Zip file Removed Successfully..")
    except:
        log.info("Twitter Zip is not Found in the Directory..")
        pass
    try:
        os.remove(dir_path +'instagram.zip')
        log.info("InstaGram Zip file Removed Successfully..")
    except:
        log.info("InstaGram Zip is not Found in the Directory..")
        pass
    try:
        os.remove(dir_path +'google_plus.zip')
        log.info("Google Plus Zip file Removed Successfully..")
    except:
        log.info("Google Plus Zip is not Found in the Directory..")
        pass

    return render_template('index.html')
    log.info("Exiting the Index Page............")

#-----------------------------
@app.route('/Twitter')
def twitter_return():
    log.info("In the twitter_return function...........")
    return send_file(dir_path +'twitter.zip',attachment_filename='twitter.zip')

@app.route('/Instagram')
def instagram_return():
    log.info("In the Instagram_return function..........")
    return send_file(dir_path +'instagram.zip',attachment_filename='instagram.zip')

@app.route('/Google+')
def google_plus_return():
    log.info("In the Google_plus_return function........")
    return send_file(dir_path +'google_plus.zip',attachment_filename='google_plus.zip')

@app.route('/logs')
def logs():
    log.info("In the Logs Function to get the Logs File for the Debugging...")
    try:
        shutil.make_archive(dir_path + 'logs', 'zip', dir_path + 'logs')
        log.info("Zip file successfully created for Logs Directory....")
    except Exception as e:
        log.info("Unable to Create the Zip file for Logs Directory....")
        log.debug("Unable to Create Zip = "+str(e))

    return send_file(dir_path +'logs.zip',attachment_filename='logs.zip')

#-----------------------------

@app.route('/instaGram')
def instaGram():
    log.info("In the Instagram Function...........")
    return redirect('/data')

#---------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/data')
def user_photos():
    log.info("In the user_photos function.........")
    log.info("Check whether InstaGram info is in Session Variables......")
    # if instagram info is in session variables, then display user photos
    if 'instagram_access_token' in session and 'instagram_user' in session:
        log.info("Instagram info is in session variables.........")
        APP2 = session['instagram_access_token']
        log.info("Instagram App2 value from the session..........")
        request_url = (BASE_URL + 'users/self/media/recent/?access_token=%s') % (APP2)
        log.info("Getting the Request_url from the user_photos")

        recent_post = requests.get(request_url).json()['data']
        log.info("Getting the recent_post from the request_url.........")
        result_data = pd.io.json.json_normalize(recent_post)
        log.info("Creation of Dataframe as result_data........")
        try:
            try:
                if result_data['caption'].to_frame().all().isnull().tolist()[0] == True:
                    log.info("If Caption Column Empty..........")
                    log.info("In the First(1) model of Instagram..........")
                    mask = ['attribution', 'caption', 'caption.from.id', 'caption.created_time',
                            'caption.from.username', 'caption.id', 'id',
                            'created_time', 'images.low_resolution.url', 'comments.count', 'filter',
                            'images.low_resolution.height',
                            'images.low_resolution.width', 'images.standard_resolution.height',
                            'images.standard_resolution.width',
                            'images.thumbnail.height', 'images.thumbnail.width', 'location', 'tags', 'type', 'user.id',
                            'user.username',
                            'user_has_liked', 'users_in_photo']

                    log.info("Selection of Columns for removal from the Dataframe.")
                    result = result_data.drop(mask, axis=1)
                    log.info("After Dropping of the Column from the Dataframe..")
                    result.rename(columns={'caption.from.full_name': 'caption_name',
                                           'caption.from.profile_picture': 'caption_picture',
                                           'caption.text': 'caption_text',
                                           'images.standard_resolution.url': 'images_url',
                                           'images.thumbnail.url': 'thumbnail_url', 'likes.count': 'likesCount',
                                           'user.full_name': 'username', 'user.profile_picture': 'profile_picture'},
                                  inplace=True)
                    log.info("Renaming the columns from the Dataframe")
                    log.info("Exiting the First(1) Model of the Instagram.........")
                else:
                    try:
                        log.info("If Caption Column is not Empty......")
                        log.info("In the Second(2) model of the Instagram..........")
                        mask = ['attribution', 'caption', 'id', 'images.low_resolution.url', 'comments.count', 'filter',
                                'images.low_resolution.height', 'images.low_resolution.width',
                                'images.standard_resolution.height',
                                'images.standard_resolution.width', 'images.thumbnail.height', 'images.thumbnail.width',
                                'location',
                                'tags', 'type', 'user.id', 'user.username', 'user_has_liked', 'users_in_photo']
                        log.info("Selection of Columns for removal from the Dataframe.")
                        result = result_data.drop(mask, axis=1)
                        log.info("After Dropping of the Column from the Dataframe..")
                        result.rename(columns={'images.standard_resolution.url': 'images_url',
                                               'images.thumbnail.url': 'thumbnail_url', 'likes.count': 'likesCount',
                                               'user.full_name': 'username', 'user.profile_picture': 'profile_picture'},
                                      inplace=True)
                        log.info("Renaming the columns from the Dataframe")
                        log.info("Exiting the Second(2) Model of the Instagram.........")
                    except:
                        log.info("In the Third(3) model of the Instagram.............")
                        mask = ['attribution', 'caption', 'comments.count', 'filter', 'id',
                                'images.low_resolution.height',
                                'images.low_resolution.url', 'images.low_resolution.width',
                                'images.standard_resolution.height',
                                'images.standard_resolution.width', 'images.thumbnail.height', 'images.thumbnail.width',
                                'location.id',
                                'location.latitude', 'location.longitude', 'tags', 'type', 'user.id', 'user.username',
                                'user_has_liked', 'users_in_photo']
                        log.info("Selection of Columns for removal from the Dataframe.")
                        result = result_data.drop(mask, axis=1)
                        log.info("After Dropping of the Column from the Dataframe..")
                        result.rename(columns=
                                      {'location.name': 'location_name', 'user.full_name': 'username',
                                       'user.profile_picture': 'profile_picture',
                                       'likes.count': 'likesCount', 'images.standard_resolution.url': 'images_url',
                                       'images.thumbnail.url': 'thumbnail_url', }, inplace=True)
                        log.info("Renaming the columns from the Dataframe")
                        log.info("Exiting the Third(3) Model of the Instagram.........")
            except:
                log.info("In the Fourth(4) model of the Instagram...........")
                result_data['caption_create_time'] = result_data['caption.created_time']
                log.info("Renaming the Create_time Column from the result_data........")
                mask = ['attribution', 'caption.from.id', 'caption.created_time', 'caption.from.username',
                        'caption.id', 'id',
                        'created_time', 'images.low_resolution.url', 'comments.count', 'filter',
                        'images.low_resolution.height',
                        'images.low_resolution.width', 'images.standard_resolution.height',
                        'images.standard_resolution.width',
                        'images.thumbnail.height', 'images.thumbnail.width', 'location', 'tags', 'type', 'user.id',
                        'user.username',
                        'user_has_liked', 'users_in_photo']
                log.info("Selection of Columns for removal from the Dataframe.")
                result = result_data.drop(mask, axis=1)
                log.info("After Dropping of the Column from the Dataframe..")
                result.rename(
                    columns={'caption.from.full_name': 'caption_name',
                             'caption.from.profile_picture': 'caption_picture',
                             'caption.text': 'caption_text', 'images.standard_resolution.url': 'images_url',
                             'images.thumbnail.url': 'thumbnail_url', 'likes.count': 'likesCount',
                             'user.full_name': 'username', 'user.profile_picture': 'profile_picture'}, inplace=True)
                log.info("Renaming the columns from the Dataframe")
                log.info("Exiting the Fourth(4) Model of the Instagram.........")

            log.info("Check Whether the Directory Exist or Not...")
            if not os.path.exists(dir_path + 'instagram'):
                log.info("Creation of the Instagram Directory..")
                os.makedirs(dir_path + 'instagram')
                log.info("Creation of the Insta_images sub-directory in the Instagram Directory..")
                os.makedirs(dir_path + 'instagram\\Insta_images')

            log.info("Checking for available Images for Downloading...")
            try:
                for index, item in enumerate(result['images_url'].tolist()):
                    if item!= '':
                        log.info("Downloading of Instagram Image........."+str(index))
                        urllib.request.urlretrieve(str(item),dir_path + 'instagram\\Insta_images\\' + str(index) + '.jpg')
            except Exception as e:
                log.info("Unable to Download the Instagram Images.......")
                print(e)
            log.info("Before the Creation of InstaGram Excel Sheet........")
            result.to_excel(dir_path + 'instagram\\Insta__' + str(datetime.datetime.now().date()) + '.xlsx')
            log.info("After the Creation of InstaGram Excel Sheet........")

            try:
                shutil.make_archive(dir_path + 'instagram', 'zip',dir_path + 'instagram')
                log.info("Converting the InstaGram Directory into the InstaGram Zip File.......")
            except Exception as e:
                log.debug("Failed to Create the InstaGram Zip file = "+str(e))
            log.info("Check for the InstaGram Directory into the Directory Path............")
            if os.path.exists(dir_path + 'instagram'):
                log.info("Removal of InstaGram Directory from the Directory Path...........")
                shutil.rmtree(dir_path + 'instagram')
            log.info("Redirecting the function to the main_data function................")
            return redirect('/main_data')

        except Exception as e:
            log.info("Abnormally Termination of the Program and control goes to the Exception")
            log.debug("InstaGram Exception Message = "+str(e))
            return render_template('failed.html')
    else:
        log.info("Connect for the InstaGram Info.....")
        log.info("Redirecting to the connect function for the InstaGram Info...........")
        return redirect('/connect')

# Redirect users to Instagram for login
@app.route('/main_data')
def main_data():
    log.info("For the Deletion of Access_Token from the Session.......")
    try:
        if session['instagram_access_token']:
            try:
                del session['instagram_access_token']
                log.info("InstaGram Access Token deleted from the Session.....")
            except:
                log.info("No Access Token was Found in the Session...")
                pass
    except:
        log.info("Access Token not Found in the Session...")
        pass
    log.info("Redirecting the function to the Result_InstaGram Page.....")
    return render_template('result_instagram.html')

@app.route('/connect')
def main():
    log.info("Function for the Connection of the Instagram Api.......")
    url = api.get_authorize_url(scope=["likes", "comments"])
    log.info("Redirecting the Url..........")
    return redirect(url)

@app.route('/instagram')
def on_callback():
    log.info("Getting the Authorization code from the callback Url for the Verification....")
    code = request.args.get('code', '')
    if code:
        log.info("If Verification Code is Successfully getted from the Callback...")
        payload = {"client_id": '4c9486f3ca62407b89fa39dc6bb45ca8',
                   "client_secret": '99fe3d35529e4f75aec835be6b5b175f',
                   "grant_type": "authorization_code",
                   "redirect_uri": 'http://127.0.0.1:5000/instagram',
                   "code": code}
        log.info("Credentials for the InstaGram Api for the Requesting the Data...")
        r = requests.post('https://api.instagram.com/oauth/access_token', data=payload)
        log.info("Successfully getting the Data from the InstaGram API..")
        recent_post = r.json()
        log.info("Getting the response from the InstaGram API in the form of Json Data..")
        session['instagram_access_token'] = recent_post['access_token']
        log.info("Storing the InstaGram Access Token in the Session...")
        session['instagram_user'] = recent_post['user']
        log.info("Storing the InstaGram InstaGram User Data in the Session...")
        log.info("Redirecting the Page to the Data Section....")
        return redirect('/data')  # redirect back to main page
    else:
        log.info("No Code Getting from the callback.....")
        return "Uhoh no code provided"


@app.route('/fb')
def fb():
    log.info("Redirecting the Facebook Section to the home Section....")
    return render_template('home.html')

@app.route('/home',methods= ["GET","POST"])
def home():
    log.info("Check for the Get or Post Method....")
    if request.method == "POST":
        log.info("If the Method is POST........")
        data = request.form['data']
        log.info("Getting the Facebook Data from the callback....")
        from callback import fb_token
        result = fb_token()
        if result == 1:
            return render_template("result.html", result=result)
        else:
            return render_template("failed.html")


@app.route('/twitter')
def twitter():
    log.info("In the Twitter Section for the Data........")
    twitter = Twython(twitter_consumer_key, twitter_consumer_secret)
    log.info("Setting up the Consumer_Key and Consumer_Secret in the Function......")
    auth = twitter.get_authentication_tokens(callback_url='http://127.0.0.1:5000/twittercallback')
    log.info("Getting the Authentication Tokens from the Callback Url of Twitter....")
    session['OAUTH_TOKEN'] = auth['oauth_token']
    log.info("Get and Store the Oauth Token in the Session....")
    session['OAUTH_TOKEN_SECRET'] = auth['oauth_token_secret']
    log.info("Get and Store Oauth_Token_Secret in the Session......")
    log.info("Redirecting the Authorization to the auth_url.......")
    print(auth['auth_url'])
    return redirect(auth['auth_url'])

@app.route('/twittercallback')
def twittercallback():
    try:
        log.info("In the TwitterCallBack Section........")
        oauth_verifier = request.args.get('oauth_verifier')
        log.info("Getting the oauth_verifier from the twittercallback...")
        OAUTH_TOKEN=session['OAUTH_TOKEN']
        log.info("Getting the Oauth_Token from the Session.....")
        OAUTH_TOKEN_SECRET=session['OAUTH_TOKEN_SECRET']
        log.info("Getting the Oauth_Token_Secret from the Session.....")
        twitter = Twython(twitter_consumer_key, twitter_consumer_secret, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        log.info("Setting the Oauth_Token and Oauth_Token_Secret in the Function......")
        final_step = twitter.get_authorized_tokens(oauth_verifier)
        log.info("Gett the Authorized Tokens with the help og Oauth_Verifier.....")
        session['OAUTH_TOKEN'] = final_step['oauth_token']
        log.info("Get and Store the Oauth_Token in the Session......")
        session['OAUTH_TOKEN_SECRET'] = final_step['oauth_token_secret']
        log.info("Get and Store the Oauth_Token_Secret in the Session....")
        OAUTH_TOKEN = session['OAUTH_TOKEN']
        log.info("Getting the Oauth_Token from the Session....")
        OAUTH_TOKEN_SECRET = session['OAUTH_TOKEN_SECRET']
        log.info("Getting the Oauth_Token_Secret from the Session....")

        auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret, callback='http://127.0.0.1:5000/twittercallback')
        auth.get_authorization_url()
        log.info("Setting the Oauth_Token and Oauth_Token_Secret in the auth for calling the Twitter API....")
        auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        log.info("Setting the Auth in the Twitter API....")
        twitter_client = API(auth)

        try:
            log.info("Creation of Twitter_Data Dataframe....")
            twitter_data = pd.DataFrame(
                [{'id': data.id_str, 'created_at': data.created_at, 'name': data.user.name, 'location': data.user.location,
                  'text': data.text.encode("utf-8"), 'retweet_count': data.retweet_count,
                  'favorite_count': data.favorite_count, 'followers_count': data.user.followers_count,
                  'status_count': data.user.statuses_count,
                  'profile_background_image': data.user.profile_background_image_url_https,
                  'profile_image_url_https': data.user.profile_image_url_https} for data in
                 Cursor(twitter_client.user_timeline).items()])
            log.info("Creation of DataFrame Successful..")
            images_url = []
            log.info("Creating a List containing all the Images Url from the Twitter...")
            for item in Cursor(twitter_client.user_timeline).items():
                try:
                    log.info("If Image_Url is Present......")
                    images_url.append(list(list(item.entities.values())[-1][0].values())[4])
                except:
                    log.info("If Images_Url is Not Present......")
                    images_url.append('')
            log.info("Creating the Images_Url Column in the DataFrame......")
            twitter_data['images_url'] = images_url

            log.info("Check Whether the Twitter Directory is Present Or Not...")
            if not os.path.exists(dir_path + 'twitter'):
                log.info("If Twitter Directory Not Present Create the Directory...")
                os.makedirs(dir_path + 'twitter')
                log.info("Creation of Twitter_Images sub-directory in the Twitter Directory...")
                os.makedirs(dir_path + 'twitter\\twitter_images')

            log.info("For the Downloading the Getted Images From the Data....")
            try:
                for index, item in enumerate(images_url):
                    if item != '':
                        log.info("If Image_Url is present in the Images_Url..")
                        try:
                            urllib.request.urlretrieve(str(item),dir_path + 'twitter\\twitter_images\\IMG_' +str(index) + '.jpg')
                            log.info("Image Downloaded Successfully with the Name = "+'IMG_' +str(index) + '.jpg')
                        except:
                            log.info("Failed to Download the Image...")
                            pass
            except Exception as e:
                log.info("Unable to Download the Image And Controller in the Exception...")
                log.debug("Exception for Downloading the Twitter Images = "+str(e))
                pass

            log.info("Attempt for the Creation of Twitter Excel DataSheet..")
            twitter_data.to_excel(dir_path + 'twitter\\twitter_data__' + str(datetime.datetime.now().date()) + '.xlsx')
            log.info("Twitter_Data Excel Sheet Created Successfully...")

            log.info("Creating the Zip file From the Twitter Directory....")
            shutil.make_archive(dir_path + 'twitter', 'zip', dir_path + 'twitter')

            log.info("Check Whether The Twitter Directory is Present or Not....")
            if os.path.exists(dir_path + 'twitter'):
                log.info("Remove the Twitter Directory.........")
                shutil.rmtree(dir_path + 'twitter')

            log.info("Redirecting the Function to the Result_Twitter Template.......")
            return render_template("result_twitter.html")

        except Exception as e:
            log.info("Redirecting the Function to the Failed Template due to some Error....")
            log.debug("Exception in the Twitter DataFrame Creation = "+str(e))
            return render_template("failed.html")
    except:
        pass

@app.route('/google_plus')
def test_api_request():
  log.info("In the Google_Plus Section.......")
  if 'credentials' not in flask.session:
     log.info("Redirecting the Control to the Google Plus Authorize Section...")
     return flask.redirect('authorize')

  log.info("Check for the Google Plus Credentials and Get it from the Session...")
  credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
  
  log.info("Building and Creating the Data of Google Plus...")
  drive = build('plus', API_VERSION, credentials=credentials)
  
  log.info("Getting the people Data from the Google Plus....")
  people_document = drive.people().get(userId='me').execute()
  
  log.info("Getting the All the Data of Google Plus...........")
  google_request = drive.activities().list(userId='me',collection='public')
  
  log.info("Executing the Request and ready for Data Retrieval.......")
  activities_document = google_request.execute()

  log.info("Creation of Google Plus DataFrame..........")
  try:
    google_plus_data = pd.DataFrame([{"id": data['actor']['id'], 'text': data['title'], 'Date': data['published'],
             "UserName": data['actor']['displayName'], "post_url": data['object']['url']} for data in
            list(activities_document.values())[-1]])
    log.info("Google Plus DataFrame Created Successfully..")

    images_url, image_link = [], []
    for data in list(activities_document.values())[-1]:
      try:
        print(data,"-----------------------")
        log.info("Getting the Image_url from the Google Plus Data....")
        images_url.append(data['object']['attachments'][0]['url'])
      except:
        log.info("Image_Url is Empty........")
        images_url.append('')

      try:
          log.info("Getting the Image_link from the Google Plus Data....")
          image_link.append(data['object']['attachments'][0]['image']['url'])
      except:
          log.info("Image_Link is Empty......")
          image_link.append('')

    log.info("Inserting the Image_Url as the Column in the Google Plus DataFrame...")
    google_plus_data['images_url'] = images_url
    log.info("Inserting the Image_Link as the Column in the Google Plus DataFrame....")
    google_plus_data['image_link'] = image_link

    log.info("Changing the Date Format in the Google Plus DataFrame....")
    google_plus_data['Date'] = google_plus_data['Date'].apply(lambda x: x.replace('T',' ')).apply(lambda y: y.replace('Z',''))

    log.info("Check Whether the Google Plus Directory Is Present Or Not...")
    if not os.path.exists(dir_path + 'google_plus'):
        log.info("Create the Google Plus Directory....")
        os.makedirs(dir_path + 'google_plus')
        log.info("Create the Google Plus Images Sub-Directory in the Google Plus Directory...")
        os.makedirs(dir_path + 'google_plus\\google_plus_images')

    log.info("Saving the Google Plus Images........")
    try:
      for index, item in enumerate(image_link):
          if item != '':
            try:
                log.info("Try to Download the Image using Url.....")
                urllib.request.urlretrieve(str(item),dir_path + 'google_plus\\google_plus_images\\' + str(index) + '.jpg')
                log.info("Image Saved Successfully.........")
            except Exception as e:
                log.info("Unable to Download the Image....")
                log.debug("Exception while downloading the Google Plus Images = "+str(e))
    except Exception as e:
        log.info("In the Exception Block during the Image Downloading.....")
        log.debug("Exception While Entering the Image Download Section = "+str(e))

    log.info("Creating the Google Plus ExcelSheet........")
    google_plus_data.to_excel(dir_path + 'google_plus\\Google_plus__'+str(datetime.datetime.now().date())+'.xlsx')
    log.info("Google Plus ExcelSheet Created SUccessfully.......")

    try:
        log.info("Converting the Google Plus Directory into the Google Plus Zip File.")
        shutil.make_archive(dir_path + 'google_plus', 'zip', dir_path + 'google_plus')
        log.info("Creation of Google Plus Zip File Successful....")
    except Exception as e:
        log.info("Error in the Creation of Google Plus Zip File...")
        log.debug("Error in the Creation of Google Plus Zip File = "+str(e))

    log.info("Check Whether the Google Plus Directory is Present or Not..")
    if os.path.exists(dir_path + 'google_plus'):
        try:
            log.info("Remove the Google Plus Directory..")
            shutil.rmtree(dir_path + 'google_plus')
            log.info("Removal of Google Plus Directory Successful....")
        except Exception as e:
            log.info("Failed to remove the Google Plus Directory...")
            log.debug("Failed to remove the Google Plus Directory = "+str(e))

    log.info("Redirecting the Control to the Result Google Plus Template....")
    return render_template('result_google_plus.html')

  except Exception as e:
    log.info("Failed to Execute the Google Plus Section....")
    log.debug("Failed Google Plus Section = "+str(e))
    return render_template('failed.html')

  log.info("Getting the Credentials from the Credentials to Dictionary Function and Store into the Session...")
  flask.session['credentials'] = credentials_to_dict(credentials)


@app.route('/authorize')
def authorize():
  log.info("In the Authorize Section of the Google Plus...")

  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  log.info("Getting the AUthorization of the Google Plus for the Validation...")
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES.split(' '))
  
  log.info("Getting the Redirect_Uri of the Google Plus.......")
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
  
  log.info("Getting the Authorization_url of the Google Plus....")
  authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')

  log.info("Inserting the State of the Google Plus in the Session...")
  flask.session['state'] = state

  log.info("Redirecting the Function...")
  return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
  log.info("In the Oauth2Callback Function...")
  log.info("Getting the State from the Session..")
  state = flask.session['state']

  log.info("Getting the Authorization from the oauth2callback....")
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES.split(' '), state=state)
  
  log.info("Getting the Redirect Uri from the Google OauthCallBack...")
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  log.info("Get the Authorization Response of the Google Plus....")
  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url

  log.info("Get the Access Token of the Google Plus...")
  flow.fetch_token(authorization_response=authorization_response)

  log.info("Get the Credentials of the Google Plus...")
  credentials = flow.credentials

  log.info("Storing the Crdentials of the Google Plus in the Session... ")
  flask.session['credentials'] = credentials_to_dict(credentials)

  log.info("Redirecting the Function to the Test_API_Request..")
  
  return flask.redirect(flask.url_for('test_api_request'))


@app.route('/clear')
def clear_credentials():
  log.info("In the Clear Credentials Function........")
  log.info("Checking for credentials in the Session...")
  
  if 'credentials' in flask.session:
    log.info("Delete the Credentials from the Session...")
    del flask.session['credentials']

  log.info("Redirecting the Control to the Home Page with the print_index_table function..")
  
  return ('<h1>Credentials have been cleared.</h1><br><br>' +print_index_table())

def credentials_to_dict(credentials):
  log.info("In the Credentials_to_Dictionary Function...")
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  log.info("In the Print_Index_Table Function..")
  log.info("Redirecting to the Home Page......")
  return render_template('index.html')


_GOOGLE_OAUTH2_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'

if __name__ == '__main__':
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  app.run(debug=True)