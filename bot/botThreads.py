import random
import requests
import time
from decouple import config
from bot.database import *
from bot.utils import shortLinkShopee
from bot.caption_generator import generate_caption
from bot.image_utils import parse_image_urls, download_images, cleanup_images
from function_list import *

def autoPostingThreads():
    result = funtion('autoPostingThreads')
    if not result or len(result) == 0:
        print("\n[WARN] autoPostingThreads not found in function_bot table, skipping")
        return
    if result[0]['is_active'] != 1:
        print("\n[INFO] autoPostingThreads is inactive")
        return
    
    print("\n[BOT] AUTO POSTING THREADS")

    # Coba ambil dari product_video dulu (untuk video post)
    query = "SELECT name, product_url, video_url FROM product_video"
    video_posts = db_connection(query)
    
    shopeid = 1
    access_token = config('THREADS_ACCESS_TOKEN')
    user_id = config('THREADS_USER_ID')
    base_url = f"https://graph.threads.net/v1.0/{user_id}"

    # Coba post video dulu kalau ada data
    if video_posts and len(video_posts) > 0:
        try:
            random_index = random.randrange(len(video_posts))
            product = video_posts[random_index]
            
            link = shortLinkShopee(product['product_url'], shopeid, "racunshopee", "Threads")
            caption = generate_caption(
                product['name'],
                link,
                platform="Threads"
            )
            
            video_url = product.get('video_url')
            if video_url:
                print(f"[INFO] Posting video: {video_url[:60]}...")
                
                # Step 1: Create video container
                container_url = f"{base_url}/threads"
                payload = {
                    'text': caption,
                    'media_type': 'VIDEO',
                    'video_url': video_url,
                    'access_token': access_token,
                }
                r = requests.post(container_url, data=payload)
                result = r.json()

                if 'id' not in result:
                    print(f"[ERR] Failed to create video container: {result}")
                else:
                    creation_id = result['id']
                    print(f"[INFO] Video container created: {creation_id}")
                    
                    # Step 2: Tunggu video selesai diproses
                    print("[INFO] Waiting for video processing...")
                    max_wait = 120  # max 120 detik
                    for i in range(max_wait):
                        status_url = f"{base_url}/{creation_id}"
                        status_r = requests.get(status_url, params={
                            'access_token': access_token,
                            'fields': 'status'
                        })
                        status_data = status_r.json()
                        
                        if status_data.get('status') == 'FINISHED':
                            break
                        elif status_data.get('status') == 'ERROR':
                            print(f"[ERR] Video processing failed: {status_data}")
                            return
                        time.sleep(1)
                    
                    # Step 3: Publish
                    publish_url = f"{base_url}/threads_publish"
                    publish_payload = {
                        'creation_id': creation_id,
                        'access_token': access_token,
                    }
                    r = requests.post(publish_url, data=publish_payload)
                    result = r.json()

                    if result.get('status') == 'SUCCESS' or 'id' in result:
                        print("[OK] - Video Posting Berhasil")
                        return
                    else:
                        print(f"[ERR] Video publish: {result}")
                        return
        except Exception as e:
            print(f"[ERR] Threads video: {e}")
    
    # Fallback ke image post
    query = "SELECT product_name, product_link, product_img FROM database_post"
    database_post = db_connection(query)
    
    if not database_post or len(database_post) == 0:
        print("[ERR] No data found")
        return

    random_index = random.randrange(len(database_post))
    product = database_post[random_index]

    link = shortLinkShopee(product['product_link'], shopeid, "racunshopee", "Threads")
    caption = generate_caption(
        product['product_name'],
        link,
        platform="Threads"
    )

    # Parse image URLs
    img_urls = parse_image_urls(product['product_img'])
    if len(img_urls) == 0:
        print("[ERR] No images found")
        return

    # Threads API only supports 1 image per thread
    image_url = img_urls[0]

    try:
        # Step 1: Create media container
        container_url = f"{base_url}/threads"
        payload = {
            'text': caption,
            'media_type': 'IMAGE',
            'image_url': image_url,
            'access_token': access_token,
        }
        r = requests.post(container_url, data=payload)
        result = r.json()

        if 'id' not in result:
            print(f"[ERR] Failed to create container: {result}")
            return

        creation_id = result['id']
        print(f"[INFO] Container created: {creation_id}")

        # Step 2: Publish the thread
        publish_url = f"{base_url}/threads_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': access_token,
        }
        r = requests.post(publish_url, data=publish_payload)
        result = r.json()

        if result.get('status') == 'SUCCESS' or 'id' in result:
            print("[OK] - Posting Berhasil")
        else:
            print(f"[ERR] {result}")

    except Exception as e:
        print(f"[ERR] Threads: {e}")
