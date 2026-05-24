import random
import requests
from decouple import config
from bot.database import *
from bot.utils import shortLinkShopee
from bot.caption_generator import generate_caption
from bot.image_utils import parse_image_urls
from function_list import *

# Auto Posting Halaman Facebook
def autoPostingFacebook():
    if(funtion('autoPostingFacebook')[0]['is_active'] == 1) :
        query = "SELECT product_name, product_link, product_img FROM database_post"
        database_post = db_connection(query)
        if not database_post or len(database_post) == 0:
            print("[ERR] database_post is empty")
            raise ValueError("empty range for randrange() — database_post has no data")
        random_index = random.randrange(len(database_post))
        
        shopeid = 1
        product = database_post[random_index]

        page_id = config('FACEBOOK_PAGE_ID')
        facebook_access_token = config('FACEBOOK_ACCESS_TOKEN')
        link = shortLinkShopee(product['product_link'], shopeid, "idmyfashion", "Facebook")
        caption = generate_caption(
            product['product_name'],
            link,
            platform="Facebook"
        )
        
        # Parse image URLs
        img_urls = parse_image_urls(product['product_img'])
        
        if len(img_urls) == 0:
            print("[ERR] No images found")
            return
        elif len(img_urls) == 1:
            # Single image - use /photos endpoint (current behavior)
            post_url = 'https://graph.facebook.com/v18.0/{}/photos'.format(page_id)
            payload = {
                'message': caption,
                'access_token': facebook_access_token,
                'url': img_urls[0]
            }
            
            try:
                posting = requests.post(post_url, data=payload)
                response = posting.json()
                if 'id' in response:
                    print("[OK] - Posting Berhasil")
                elif 'error' in response:
                    print(f"[ERR] Facebook: {response['error']}")
            except Exception as e:
                print(f"[ERR] Facebook: {e}")
        else:
            # Multiple images - upload unpublished photos then create multi-photo post
            print(f"[INFO] Uploading {len(img_urls)} images...")
            media_ids = []
            
            for i, img_url in enumerate(img_urls):
                upload_url = f'https://graph.facebook.com/v18.0/{page_id}/photos'
                payload = {
                    'url': img_url,
                    'published': 'false',
                    'access_token': facebook_access_token,
                }
                try:
                    r = requests.post(upload_url, data=payload)
                    data = r.json()
                    if 'id' in data:
                        media_ids.append(data['id'])
                        print(f"  [OK] Image {i+1} uploaded")
                    else:
                        print(f"  [ERR] Image {i+1}: {data}")
                except Exception as e:
                    print(f"  [ERR] Image {i+1}: {e}")
            
            if len(media_ids) > 0:
                # Create post with attached media
                post_url = f'https://graph.facebook.com/v18.0/{page_id}/feed'
                attached_media = ','.join([f'{{"media_fbid":"{mid}"}}' for mid in media_ids])
                payload = {
                    'message': caption,
                    'access_token': facebook_access_token,
                    'attached_media': f'[{attached_media}]'
                }
                
                try:
                    r = requests.post(post_url, data=payload)
                    response = r.json()
                    if 'id' in response:
                        print(f"[OK] - Posting Berhasil ({len(media_ids)} images)")
                    elif 'error' in response:
                        print(f"[ERR] Facebook post: {response['error']}")
                        # Fallback: post single image
                        fallback_post = requests.post(
                            f'https://graph.facebook.com/v18.0/{page_id}/photos',
                            data={'message': caption, 'access_token': facebook_access_token, 'url': img_urls[0]}
                        )
                        if 'id' in fallback_post.json():
                            print("[OK] - Posting Berhasil (fallback 1 image)")
                except Exception as e:
                    print(f"[ERR] Facebook: {e}")
            else:
                print("[ERR] No images uploaded successfully")
