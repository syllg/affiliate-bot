import random
import requests
import urllib.request
import os
from decouple import config
from bot.database import *
from bot.utils import shortLinkShopee
from bot.caption_generator import generate_caption
from function_list import *

def _download_video(video_url, filename='videoPost.mp4'):
    """Download video dari URL."""
    try:
        urllib.request.urlretrieve(video_url, filename)
        print(f"[INFO] Video downloaded: {filename}")
        return True
    except Exception as e:
        print(f"[ERR] Failed to download video: {e}")
        return False

def _post_facebook_video(video_path, caption):
    """Post video ke Facebook Page."""
    page_id = config('FACEBOOK_PAGE_ID')
    access_token = config('FACEBOOK_ACCESS_TOKEN')
    
    # Step 1: Upload video
    upload_url = f'https://graph.facebook.com/v18.0/{page_id}/videos'
    
    try:
        with open(video_path, 'rb') as f:
            payload = {
                'description': caption,
                'access_token': access_token,
            }
            files = {'source': f}
            r = requests.post(upload_url, data=payload, files=files)
            response = r.json()
            
            if 'id' in response:
                print("[OK] Facebook - Video posted successfully")
                return True
            elif 'error' in response:
                print(f"[ERR] Facebook: {response['error']}")
                return False
            else:
                print(f"[ERR] Facebook: {response}")
                return False
    except Exception as e:
        print(f"[ERR] Facebook video upload: {e}")
        return False

def _extract_cover_image(video_path, cover_path):
    """Extract first frame as cover image using imageio (no ffmpeg needed)."""
    try:
        import imageio.v3 as iio
        frame = iio.imread(video_path, index=0)
        iio.imwrite(cover_path, frame)
        print(f"[INFO] Cover image extracted: {cover_path}")
        return cover_path
    except Exception as e:
        print(f"[WARN] Could not extract cover image: {e}")
        return None

def _get_video_metadata(video_path):
    """Get video duration, width, height using imageio (no ffprobe needed)."""
    try:
        import imageio.v3 as iio
        
        # Read first frame to get dimensions
        first_frame = iio.imread(video_path, index=0)
        height, width = first_frame.shape[:2]
        
        # Get duration by reading all frames metadata
        props = iio.improps(video_path)
        duration_ms = None
        
        if hasattr(props, 'duration') and props.duration is not None:
            duration_ms = int(props.duration * 1000)
        elif hasattr(props, 'fps') and props.fps and props.fps != float('inf'):
            if hasattr(props, 'n_frames') and props.n_frames:
                duration_ms = int((props.n_frames / props.fps) * 1000)
        
        # Fallback: try reading video properties
        if duration_ms is None:
            try:
                with iio.imopen(video_path, 'r', plugin='FFMPEG') as file:
                    meta = file.metadata()
                    if 'duration' in meta:
                        duration_ms = int(meta['duration'] * 1000)
            except:
                pass
        
        return {
            'width': width,
            'height': height,
            'duration_ms': duration_ms,
        }
    except Exception as e:
        print(f"[WARN] Could not get video metadata: {e}")
        return {}

def _post_pinterest_video(video_path, caption, product_name, link):
    """Post video pin ke Pinterest."""
    try:
        from py3pin.Pinterest import Pinterest
    except ImportError:
        print("[WARN] py3pin tidak terinstall, skip Pinterest video")
        return False
    
    print("[INFO] Logging in to Pinterest...")
    pinterest = Pinterest(
        email=config('PINTEREST_EMAIL'),
        password=config('PINTEREST_PASSWORD'),
        username=config('PINTEREST_USERNAME'),
        cred_root='cred_root'
    )
    
    board_id = config('PINTEREST_BOARD_ID')
    
    # Extract cover image using imageio (avoid ffmpeg dependency)
    import tempfile
    cover_path = None
    try:
        cover_fd, cover_path = tempfile.mkstemp(suffix='.jpg')
        os.close(cover_fd)
        cover_path = _extract_cover_image(video_path, cover_path)
    except Exception as e:
        print(f"[WARN] Cover extraction failed: {e}")
        cover_path = None
    
    try:
        print("[INFO] Uploading video to Pinterest...")
        
        # Get video metadata to skip ffprobe requirement
        meta = _get_video_metadata(video_path)
        print(f"[INFO] Video metadata: {meta}")
        
        kwargs = {
            'video_file': video_path,
            'board_id': board_id,
            'title': product_name,
            'description': caption,
            'link': link,
        }
        
        # Add metadata if available
        if meta.get('duration_ms'):
            kwargs['duration_ms'] = meta['duration_ms']
        if meta.get('width'):
            kwargs['width'] = meta['width']
        if meta.get('height'):
            kwargs['height'] = meta['height']
        if cover_path:
            kwargs['cover_image_file'] = cover_path
        
        pinterest.upload_video_pin(**kwargs)
        print("[OK] Pinterest - Video pin posted successfully")
        return True
    except Exception as e:
        print(f"[ERR] Pinterest video: {e}")
        return False
    finally:
        # Cleanup cover image
        if cover_path and os.path.exists(cover_path):
            try:
                os.remove(cover_path)
            except:
                pass

def _post_telegram_video(video_path, caption):
    """Post video ke Telegram channel."""
    bot_token = config('TELEGRAM_BOT_TOKEN')
    channel_ids = [c.strip() for c in config('TELEGRAM_CHANNEL_IDS').split(',')]
    
    success = True
    for channel_id in channel_ids:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
            with open(video_path, 'rb') as f:
                r = requests.post(url, data={
                    'chat_id': channel_id,
                    'caption': caption,
                }, files={'video': f})
                
                if r.json().get('ok'):
                    print(f"[OK] Telegram - Video posted to {channel_id}")
                else:
                    print(f"[ERR] Telegram {channel_id}: {r.json()}")
                    success = False
        except Exception as e:
            print(f"[ERR] Telegram video: {e}")
            success = False
    
    return success


def _post_threads_video(video_url, caption, product_name, link):
    """Post video ke Threads menggunakan video URL."""
    try:
        access_token = config('THREADS_ACCESS_TOKEN')
        user_id = config('THREADS_USER_ID')
        base_url = f"https://graph.threads.net/v1.0/{user_id}"
        
        print("[INFO] Posting video to Threads...")
        
        # Step 1: Create video container dengan video_url
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
            print(f"[ERR] Failed to create container: {result}")
            return False
        
        creation_id = result['id']
        print(f"[INFO] Video container created: {creation_id}")
        
        # Step 2: Tunggu video selesai diproses
        print("[INFO] Waiting for video processing...")
        max_wait = 120
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
                return False
            time.sleep(1)
        
        # Step 3: Publish
        publish_url = f"{base_url}/threads_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': access_token,
        }
        r2 = requests.post(publish_url, data=publish_payload)
        result2 = r2.json()
        
        if result2.get('status') == 'SUCCESS' or 'id' in result2:
            print("[OK] Threads - Video posted successfully")
            return True
        else:
            print(f"[ERR] Threads publish: {result2}")
            return False
            
    except Exception as e:
        print(f"[ERR] Threads video: {e}")
        return False

def postingVideo():
    if funtion('postingVideo')[0]['is_active'] != 1:
        return
    
    print("\n\n[BOT] AUTO POSTING VIDEO\n")

    query = "SELECT name, price, discount, rating, product_url, video_url, img_url FROM product_video"
    database_post = db_connection(query)

    if len(database_post) == 0:
        print("[ERR] Tidak ada data di tabel product_video")
        return

    shopeid = 1
    random_index = random.randrange(len(database_post))
    product = database_post[random_index]

    print(f"[INFO] Posting produk: {product['name']}")
    print(f"[INFO] Video URL: {product['video_url']}")

    # Download video
    video_filename = os.path.join(os.getcwd(), 'videoPost.mp4')
    if not _download_video(product['video_url'], video_filename):
        return

    try:
        # Generate caption per platform (dengan harga & rating kalau tersedia)
        price = product.get('price') or product.get('discount')
        rating = product.get('rating')

        link_fb = shortLinkShopee(product['product_url'], shopeid, "idmyfashion", "Facebook")
        caption_fb = generate_caption(product['name'], link_fb, price=price, rating=rating, platform="Facebook")

        link_pin = shortLinkShopee(product['product_url'], shopeid, "idmyfashion", "Pinterest")
        caption_pin = generate_caption(product['name'], link_pin, price=price, rating=rating, platform="Pinterest")

        link_tg = shortLinkShopee(product['product_url'], shopeid, "racunshopee", "Telegram")
        caption_tg = generate_caption(product['name'], link_tg, price=price, rating=rating, platform="Telegram")

        # Post ke Facebook
        if funtion('autoPostingFacebook')[0]['is_active'] == 1:
            print("\n[INFO] Posting ke Facebook...")
            _post_facebook_video(video_filename, caption_fb)
        else:
            print("\n[SKIP] Facebook tidak aktif, melewati posting video")

        # Post ke Pinterest
        if funtion('autoPostingPinterest')[0]['is_active'] == 1:
            print("\n[INFO] Posting ke Pinterest...")
            print(f"[DEBUG] File exists: {os.path.exists(video_filename)}")
            _post_pinterest_video(video_filename, caption_pin, product['name'], link_pin)
        else:
            print("\n[SKIP] Pinterest tidak aktif, melewati posting video")

        # Post ke Telegram
        if funtion('autoPostingTelegram')[0]['is_active'] == 1:
            print("\n[INFO] Posting ke Telegram...")
            _post_telegram_video(video_filename, caption_tg)
        else:
            print("\n[SKIP] Telegram tidak aktif, melewati posting video")

        # Post ke Threads
        if funtion('autoPostingThreads')[0]['is_active'] == 1:
            print("\n[INFO] Posting ke Threads...")
            link_th = shortLinkShopee(product['product_url'], shopeid, "racunshopee", "Threads")
            caption_th = generate_caption(product['name'], link_th, price=price, rating=rating, platform="Threads")
            _post_threads_video(product['video_url'], caption_th, product['name'], link_th)
        else:
            print("\n[SKIP] Threads tidak aktif, melewati posting video")

    finally:
        # Cleanup
        import time
        if os.path.exists(video_filename):
            try:
                os.remove(video_filename)
                print("[INFO] Video file cleaned up")
            except PermissionError:
                # Windows file lock - retry after short delay
                time.sleep(2)
                try:
                    os.remove(video_filename)
                    print("[INFO] Video file cleaned up (after retry)")
                except:
                    print("[WARN] Could not cleanup video file, will overwrite next run")
