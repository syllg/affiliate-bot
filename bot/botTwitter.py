import tweepy as twitter
import pandas as pd
import random
import urllib.request
import requests
from decouple import config
from bot.database import *
from bot.utils import shortLinkShopee
from bot.caption_generator import generate_caption
from bot.image_utils import parse_image_urls, download_images, cleanup_images
from function_list import *

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


# AUTO POSTING id_myfashion
def autoposting():
    if not TWITTER_ENABLED:
        print("[INFO] Twitter disabled")
        return
    if(funtion('autoposting')[0]['is_active'] == 1) :
        print("\n\n[BOT] AUTO POSTING\n")

        query = "SELECT username, API_KEY, API_SECRET_KEY, BEARER_TOKEN, ACCESS_TOKEN, SECRET_ACCESS_TOKEN FROM account_eleved"
        accountResult = db_connection(query)

        query = "SELECT product_name, product_link, product_img FROM database_post"
        database_post = db_connection(query)

        shopeid = 1

        for account in accountResult:
            try :
                auth = twitter.OAuthHandler(account['API_KEY'], account['API_SECRET_KEY'])
                auth.set_access_token(account['ACCESS_TOKEN'], account['SECRET_ACCESS_TOKEN'])
                api = twitter.API(auth)

                profile = api.update_profile()
                print("\nAccount : {}".format(profile.name) + " ({})".format(profile.screen_name))

                random_index = random.randrange(len(database_post))
                product = database_post[random_index]

                # Parse image URLs
                img_urls = parse_image_urls(product['product_img'])
                if len(img_urls) == 0:
                    print("[ERR] No images found")
                    continue

                # Download images
                local_files = download_images(img_urls, prefix="tw_img")
                if len(local_files) == 0:
                    print("[ERR] Failed to download images")
                    continue

                try:
                    link = shortLinkShopee(product['product_link'], shopeid, "idmyfashion", "Twitter")
                    statusTweet = generate_caption(
                        product['product_name'],
                        link,
                        platform="Twitter"
                    )
                    
                    # Upload all images and collect media_ids
                    media_ids = []
                    for fname in local_files[:4]:  # Twitter max 4 images
                        try:
                            media = api.media_upload(fname)
                            media_ids.append(media.media_id)
                        except Exception as e:
                            print(f"[WARN] Failed to upload {fname}: {e}")
                    
                    if len(media_ids) > 0:
                        api.update_status(status=statusTweet, media_ids=media_ids)
                        print(f"[OK] - Posting Berhasil ({len(media_ids)} images)")
                    else:
                        # Fallback: text-only tweet
                        api.update_status(status=statusTweet)
                        print("[OK] - Posting Berhasil (text only)")
                except Exception as e:
                    print(f"[ERR] Posting: {e}")
                finally:
                    cleanup_images(local_files)
            except Exception as e:
                print(f"[ERR] Account: {e}")
         

# Retweet Spongebob to Akun BackUp
def autoRetweetNonEleved():
    if not TWITTER_ENABLED:
        print("[INFO] Twitter disabled")
        return
    if(funtion('autoRetweetNonEleved')[0]['is_active'] == 1) :
        userID = "spongebobnfess"
        tweets = botTwitter().user_timeline(screen_name=userID, count=1, tweet_mode='extended')

        query = "SELECT username, API_KEY, API_SECRET_KEY, BEARER_TOKEN, ACCESS_TOKEN, SECRET_ACCESS_TOKEN FROM account_non_eleved WHERE is_retweet = 1"
        accountResult = db_connection(query)

        for account in accountResult:
            api = twitter.Client(bearer_token=account['BEARER_TOKEN'], consumer_key=account['API_KEY'], consumer_secret=account['API_SECRET_KEY'], access_token=account['ACCESS_TOKEN'], access_token_secret=account['SECRET_ACCESS_TOKEN'])

            for info in tweets[:1]:
                print("ID : {}".format(info.id))

            try:
                api.retweet(tweet_id=info.id)
                print("[OK] - Retweet Berhasil\n")
            except twitter.TweepyException as e:
                pass
                print(e)
        
        # Sementara
        query = "SELECT id_shopee, id, username, access_token, access_token_secret FROM account_backup WHERE id_shopee=1 AND is_retweet = 1"
        accountResult = db_connection(query)

        for account in accountResult:
            auth = twitter.OAuth1UserHandler(
                config('API_KEY'), config('API_SECRET_KEY'),
                account['access_token'], account['access_token_secret']
            )
            api = twitter.API(auth)

            for info in tweets[:1]:
                print("ID : {}".format(info.id))

            try:
                api.retweet(id=info.id)
                print("[OK] - Retweet Berhasil\n")
            except twitter.TweepyException as e:
                print(e)
                pass
        # Sementara
    
    
# Repost Barang dari akun id_myfashion ke akun backUp
def autoRepostNonEleved() :
    if(funtion('autoRepostNonEleved')[0]['is_active'] == 1) :
        userIDaccount = "id_myfashion"

        tweets = botTwitter().user_timeline(screen_name=userIDaccount, count=200, include_rts=False, tweet_mode='extended')

        query = "SELECT username, API_KEY, API_SECRET_KEY, BEARER_TOKEN, ACCESS_TOKEN, SECRET_ACCESS_TOKEN FROM account_non_eleved WHERE is_retweet = 1"
        accountResult = db_connection(query)

        for account in accountResult:
            API = twitter.Client(bearer_token=account['BEARER_TOKEN'], consumer_key=account['API_KEY'], consumer_secret=account['API_SECRET_KEY'], access_token=account['ACCESS_TOKEN'], access_token_secret=account['SECRET_ACCESS_TOKEN'])

            totalRetweet = 2
            for index in tweets:
                if totalRetweet != 0:
                    try :
                        random_index = random.randrange(len(tweets))
                        API.unretweet(source_tweet_id =tweets[random_index].id)
                        API.retweet(tweet_id=tweets[random_index].id)
                        print("[OK] - Repost Berhasil")
                        API.like(tweet_id=tweets[random_index].id)
                        totalRetweet = totalRetweet - 1
                    except twitter.TweepyException as e:
                        pass
                        print(e)
                else:
                    break
                

def autopostingAkunBackUp():
    if not TWITTER_ENABLED:
        print("[INFO] Twitter disabled")
        return
    if(funtion('autopostingAkunBackUp')[0]['is_active'] == 1) :
        query = "SELECT * FROM account_backup where id_shopee = '1' AND is_active = 1"
        accountResult = db_connection(query)

        query = "SELECT product_name, product_link, product_img FROM database_post"
        database_post = db_connection(query)

        for account in accountResult:
            random_index = random.randrange(len(database_post))
            product = database_post[random_index]
            
            try:
                # Parse and download images
                img_urls = parse_image_urls(product['product_img'])
                local_files = download_images(img_urls, prefix="tw_bu_img")
                if len(local_files) == 0:
                    continue
                    
                media = botTwitter().media_upload(local_files[0], additional_owners=[account['id_twitter']])

                auth = twitter.OAuth1UserHandler(
                    config('API_KEY'), config('API_SECRET_KEY'),
                    account['access_token'], account['access_token_secret']
                )
                api = twitter.API(auth)

                link = shortLinkShopee(product['product_link'],account['id_shopee'], account['id_twitter'] , "Twitter")
                statusTweet = generate_caption(
                    product['product_name'],
                    link,
                    platform="Twitter"
                )

                try:
                    api.update_status(status=statusTweet, media_ids=[media.media_id])
                    print("[OK] - Posting Berhasil\n")
                except:
                    pass   
            except:
                pass
            finally:
                cleanup_images(local_files)
           
# Repost akun backUp Ayah ke masitowae
def autoRepostAkunAyah() :
    if(funtion('autoRepostAkunAyah')[0]['is_active'] == 1) :
        userIDaccount = "masitowae"
        tweets = botTwitter().user_timeline(screen_name=userIDaccount, count=100, include_rts=False, tweet_mode='extended')

        query = "SELECT id_shopee, no, id, username, access_token, access_token_secret FROM account_backup WHERE id_shopee=2 AND username <> 'imamto2003'"
        accountResult = db_connection(query)

        for account in accountResult:
            auth = twitter.OAuth1UserHandler(
                config('API_KEY'), config('API_SECRET_KEY'),
                account['access_token'], account['access_token_secret']
            )
            api = twitter.API(auth)

            totalRetweet = 2
            for index in tweets:
                if totalRetweet != 0:
                    try :
                        random_index = random.randrange(len(tweets))
                        api.unretweet(id =tweets[random_index].id)
                        api.retweet(id=tweets[random_index].id)
                        print("[OK] - Repost Berhasil")
                        totalRetweet = totalRetweet - 1
                    except twitter.TweepyException as e:
                        pass
                        print(e) 
                else:
                    break
                
def autopostingTrendingTopik():
    if not TWITTER_ENABLED:
        print("[INFO] Twitter disabled")
        return
    if(funtion('autopostingTrendingTopik')[0]['is_active'] == 1) :
        API = botTwitter()

        #Scrap Trending ======================================================
        WOEID = 1047378

        top_trends = API.get_place_trends(WOEID)

        final = []

        for i in range(len(top_trends[0]['trends'])):
            # if(top_trends[0]['trends'][i]['tweet_volume']):
            name = top_trends[0]['trends'][i]['name']
            volume = top_trends[0]['trends'][i]['tweet_volume']
            final.append([name,volume])
        
        trending = ""

        query = "SELECT * FROM account_backup WHERE username='HappyRacun'"
        accountResult = db_connection(query)

        query = "SELECT product_name, product_link, product_img FROM database_post"
        database_post = db_connection(query)

        for account in accountResult:
            random_index = random.randrange(len(database_post))
            product = database_post[random_index]
            
            # Parse and download images
            img_urls = parse_image_urls(product['product_img'])
            local_files = download_images(img_urls[:4], prefix="tw_tr_img")  # Max 4 images
            if len(local_files) == 0:
                continue
                
            media = API.media_upload(local_files[0], additional_owners=[account['id']])

            auth = twitter.OAuth1UserHandler(
                config('API_KEY'), config('API_SECRET_KEY'),
                account['access_token'], account['access_token_secret']
            )
            api = twitter.API(auth)

            for x in range(10):
                random_index_trending = random.randrange(len(final))
                trending += " " + final[random_index_trending][0]

            link = shortLinkShopee(product['product_link'],account['id_shopee'], account['id'] , "Twitter")
            statusTweet = generate_caption(
                product['product_name'],
                link,
                platform="Twitter"
            )
            
            try:
                api.update_status(status=statusTweet, media_ids=[media.media_id])
                print("[OK] - Posting Berhasil\n")
            except:
                pass
            finally:
                cleanup_images(local_files)
