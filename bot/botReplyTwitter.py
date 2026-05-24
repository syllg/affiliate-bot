import tweepy as twitter
import pandas as pd
import random
import urllib.request
import requests
from decouple import config
from bot.database import *
from bot.utils import shortLinkShopee
from bot.caption_generator import generate_caption
from bot.image_utils import parse_image_urls
from function_list import *

userID = "tanyakanrl"

# Twitter disabled - API access revoked
TWITTER_ENABLED = False

# API BotTwitter
def botTwitter():
    API_KEY = config('API_KEY')
    API_SECRET_KEY = config('API_SECRET_KEY')
    BEARER_TOKEN = config('BEARER_TOKEN')
    ACCESS_TOKEN = config('ACCESS_TOKEN')
    SECRET_ACCESS_TOKEN = config('SECRET_ACCESS_TOKEN')
    
    auth = twitter.OAuthHandler(API_KEY,  API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, SECRET_ACCESS_TOKEN)
    API = twitter.API(auth)
    
    return API

def posting():
    if not TWITTER_ENABLED:
        print("[INFO] Twitter disabled")
        return
    if(funtion('posting')[0]['is_active'] == 1) :
        print("\n\n[BOT] AUTO POSTING\n")

        query = "SELECT username, API_KEY, API_SECRET_KEY, BEARER_TOKEN, ACCESS_TOKEN, SECRET_ACCESS_TOKEN FROM account_eleved"
        accountResult = db_connection(query)

        query = "SELECT product_name, product_link, product_img FROM database_post"
        database_post = db_connection(query)

        shopeid = 1
        
        tweets = botTwitter().user_timeline(screen_name=userID, count=20)
        random_index = random.randrange(len(tweets))
        replayTweetId = tweets[random_index].id

        for account in accountResult:
            try :
                auth = twitter.OAuthHandler(account['API_KEY'], account['API_SECRET_KEY'])
                auth.set_access_token(account['ACCESS_TOKEN'], account['SECRET_ACCESS_TOKEN'])
                api = twitter.API(auth)

                profile = api.update_profile()
                print("\nAccount : {}".format(profile.name) + " ({})".format(profile.screen_name))

                random_index = random.randrange(len(database_post))
                product = database_post[random_index]

                # Use first image only for reply
                img_urls = parse_image_urls(product['product_img'])
                if len(img_urls) == 0:
                    continue

                # Download Image
                urllib.request.urlretrieve(img_urls[0], "imagePost.png")

                try:
                    link = shortLinkShopee(product['product_link'], shopeid, "idmyfashion", "Twitter")
                    statusTweet = generate_caption(
                        product['product_name'],
                        link,
                        platform="Twitter"
                    )
                    media = api.media_upload("imagePost.png")
                    api.update_status(status=statusTweet, media_ids=[media.media_id], in_reply_to_status_id=replayTweetId, auto_populate_reply_metadata=True)
                    
                    print("[OK] - Posting Berhasil")
                except:
                    print('Error posting')
                    pass
            except:
                pass
