import pandas as pd
import random
import requests
from decouple import config
from bot.database import *
from bot.utils import shortLinkShopee
from bot.caption_generator import generate_caption
from bot.image_utils import parse_image_urls, download_images, cleanup_images
from function_list import *

def autoPostingTelegram():
  if(funtion('autoPostingTelegram')[0]['is_active'] == 1) :
    print("\n[BOT] AUTO POSTING")

    query = "SELECT product_name, product_link, product_img FROM database_post"
    database_post = db_connection(query)

    shopeid = 1
    
    idChannelTelegrams = [c.strip() for c in config('TELEGRAM_CHANNEL_IDS').split(',')]

    for channelTelegram in idChannelTelegrams:
      try:
          random_index = random.randrange(len(database_post))
          product = database_post[random_index]
          
          link = shortLinkShopee(product['product_link'], shopeid, "racunshopee", "Telegram")
          caption = generate_caption(
              product['product_name'],
              link,
              platform="Telegram"
          )
          
          # Parse image URLs (support single or multiple comma-separated)
          img_urls = parse_image_urls(product['product_img'])
          
          if len(img_urls) == 0:
              print("[ERR] No images found")
              continue
          elif len(img_urls) == 1:
              # Single image - use sendPhoto
              url = f"https://api.telegram.org/bot{config('TELEGRAM_BOT_TOKEN')}/sendPhoto"
              r = requests.post(url, data={
                  'chat_id': channelTelegram,
                  'photo': img_urls[0],
                  'caption': caption
              })
              if r.json().get('ok'):
                  print("[OK] - Posting Berhasil")
              else:
                  print(f"[ERR] {r.json()}")
          else:
              # Multiple images - use sendMediaGroup
              print(f"[INFO] Downloading {len(img_urls)} images...")
              local_files = download_images(img_urls, prefix="tg_img")
              
              if len(local_files) == 0:
                  print("[ERR] Failed to download images")
                  continue
              
              # Build media array for sendMediaGroup
              # First image gets caption
              media = []
              files = {}
              for i, fname in enumerate(local_files):
                  key = f"photo{i}"
                  media.append({
                      "type": "photo",
                      "media": f"attach://{key}",
                      **({"caption": caption, "parse_mode": "HTML"} if i == 0 else {})
                  })
                  files[key] = open(fname, 'rb')
              
              url = f"https://api.telegram.org/bot{config('TELEGRAM_BOT_TOKEN')}/sendMediaGroup"
              r = requests.post(url, data={
                  'chat_id': channelTelegram,
                  'media': str(media).replace("'", '"')
              }, files=files)
              
              # Close files
              for f in files.values():
                  f.close()
              
              if r.json().get('ok'):
                  print(f"[OK] - Posting Berhasil ({len(local_files)} images)")
              else:
                  print(f"[ERR] sendMediaGroup failed: {r.json()}")
                  # Fallback: send first image only
                  url = f"https://api.telegram.org/bot{config('TELEGRAM_BOT_TOKEN')}/sendPhoto"
                  r = requests.post(url, data={
                      'chat_id': channelTelegram,
                      'photo': img_urls[0],
                      'caption': caption
                  })
                  if r.json().get('ok'):
                      print("[OK] - Posting Berhasil (fallback to 1 image)")
              
              cleanup_images(local_files)
      except Exception as e:
          print(f"[ERR] Telegram: {e}")
