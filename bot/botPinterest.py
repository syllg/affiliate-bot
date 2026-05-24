import random
from py3pin.Pinterest import Pinterest
from decouple import config
from bot.database import *
from bot.utils import shortLinkShopee
from bot.caption_generator import generate_caption
from bot.image_utils import parse_image_urls
from function_list import *

# Login Pinters
pinterest = Pinterest(
    email=config('PINTEREST_EMAIL'),
    password=config('PINTEREST_PASSWORD'),
    username=config('PINTEREST_USERNAME'),
    cred_root='cred_root'
)

# Auto Posting Pinterest
def autoPostingPinterest():
  if(funtion('autoPostingPinterest')[0]['is_active'] == 1) :
    query = "SELECT product_name, product_link, product_img FROM database_post"
    database_post = db_connection(query)

    random_index = random.randrange(len(database_post))
    product = database_post[random_index]

    shopeeid=1

    board_id=config('PINTEREST_BOARD_ID')
    section_id=None
    
    # Pinterest only supports 1 image per pin - use first image
    img_urls = parse_image_urls(product['product_img'])
    if len(img_urls) == 0:
        print("[ERR] No images found")
        return
    
    image_url = img_urls[0]  # First image only
    
    link= shortLinkShopee(product['product_link'], shopeeid, "idmyfashion", "Pinterest")
    description=generate_caption(
        product['product_name'],
        link,
        platform="Pinterest"
    )
    title= product['product_name']
    alt_text='alt text'

    try:
      pinterest.pin(board_id=board_id, image_url=image_url, description=description, title=title, link=link)
      print("[OK] - Posting Berhasil\n")
    except Exception as e:
      print(f"[ERR] Pinterest: {e}")
