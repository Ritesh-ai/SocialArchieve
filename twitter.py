import os
import sys
import string
import random
import pandas as pd
import urllib
import datetime
import openpyxl
import webbrowser as wb
import requests
import json
import six
import flask
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
import credentialss
import serializers
import shutil
import logging

##-----------------------------------------------------------



##### ---- Twitter Imports----------------------------------------------------------------------------------------
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from twython import Twython, TwythonAuthError, TwythonError, TwythonRateLimitError
import tweepy
# import twitter
from instagram.client import InstagramAPI


app = flask.Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits)for x in range(32))

twitter_consumer_key = 'x1MmILheA2rZUOt3ASe8Ml3Ay'
twitter_consumer_secret = 'SALsd26Rqdlemn2qgShY9Nuc4nwIrrfxhmwOyq6SSmpzk5JPxf'

@app.route('/twitter')
def twitter():
    twitter = Twython(twitter_consumer_key, twitter_consumer_secret)
    auth = twitter.get_authentication_tokens(callback_url='http://127.0.0.1:5000/twittercallback')
    session['OAUTH_TOKEN'] = auth['oauth_token']
    session['OAUTH_TOKEN_SECRET'] = auth['oauth_token_secret']
    print(auth['auth_url'])
    return redirect(auth['auth_url'])

@app.route('/twittercallback')
def twittercallback():
    try:
        oauth_verifier = request.args.get('oauth_verifier')
        OAUTH_TOKEN=session['OAUTH_TOKEN']
        OAUTH_TOKEN_SECRET=session['OAUTH_TOKEN_SECRET']
        twitter = Twython(twitter_consumer_key, twitter_consumer_secret, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        final_step = twitter.get_authorized_tokens(oauth_verifier)
        session['OAUTH_TOKEN'] = final_step['oauth_token']
        session['OAUTH_TOKEN_SECRET'] = final_step['oauth_token_secret']
        OAUTH_TOKEN = session['OAUTH_TOKEN']
        OAUTH_TOKEN_SECRET = session['OAUTH_TOKEN_SECRET']

        auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret, callback='http://127.0.0.1:5000/twittercallback')
        auth.get_authorization_url()
        auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        twitter_client = API(auth)

        for data in twitter_client.home_timeline:
            print(data.text)

        return render_template("result_twitter.html")
    except Exception as e:
        print(e)


_GOOGLE_OAUTH2_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'

if __name__ == '__main__':
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  app.run(debug=True)
