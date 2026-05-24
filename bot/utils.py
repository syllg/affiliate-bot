from bot.database import db_connection

def shortLinkShopee(link, idshopee, akun, sosialmedia):
    """
    Generate Shopee Affiliate short link.
    Kalau account_shopeeaff belum diisi (dummy/empty), fallback ke link asli.
    """
    try:
        query = "SELECT id, appid, rahasia FROM account_shopeeaff WHERE id={}".format(idshopee)
        account_shopee = db_connection(query)
        
        # Fallback kalau data kosong atau masih dummy
        if not account_shopee:
            return link
        appid = account_shopee[0].get('appid')
        rahasia = account_shopee[0].get('rahasia')
        if not appid or not rahasia or str(appid) in ('', '12345', '0'):
            return link
        
        from shopee_affiliate import ShopeeAffiliate    
        sa = ShopeeAffiliate(appid, rahasia)
        res = sa.generateShortLink(link, akun, sosialmedia)
        res = res.replace("shope", "shpe")
        return res
    except Exception:
        return link
