import random
from decouple import config


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE FALLBACK
# Dipakai kalau AI tidak tersedia atau error
# ─────────────────────────────────────────────────────────────────────────────

_TEMPLATES_WITH_PRICE = [
    "eh ini ternyata bagus banget\n\n{nama}\n\nHarga: Rp {price} | Rating: {rating}/5\n\n{link}",
    "nyesel baru tau sekarang\n\n{nama}\n\nHarga: Rp {price} | Rating: {rating}/5\n\n{link}",
    "temen aku yang rekomendasiin ini dan ternyata emang worth it\n\n{nama}\n\nRp {price} | {rating}/5\n\n{link}",
    "udah lama nyari yang kayak gini, akhirnya ketemu\n\n{nama}\n\nHarga: Rp {price}\n\n{link}",
    "ini salah satu yang paling sering aku pake sekarang\n\n{nama}\n\nRp {price} | Rating {rating}/5\n\n{link}",
]

_TEMPLATES_SIMPLE = [
    "eh ini ternyata bagus banget\n\n{nama}\n\n{link}",
    "nyesel baru tau sekarang\n\n{nama}\n\n{link}",
    "temen aku yang rekomendasiin ini dan ternyata emang worth it\n\n{nama}\n\n{link}",
    "udah lama nyari yang kayak gini, akhirnya ketemu\n\n{nama}\n\n{link}",
    "ini salah satu yang paling sering aku pake sekarang\n\n{nama}\n\n{link}",
]

# Hashtag per platform
_HASHTAGS = {
    "Pinterest": "#racunshopee #racunbelanja #rekomendasiproduk #shopee #belanjashopee",
    "Telegram": "#racunshopee #rekomendasiproduk",
    "Facebook": "#racunshopee #rekomendasiproduk",
    "Threads": "#racunshopee #racunbelanja",
    "general": "#racunshopee",
}


def _format_price(price):
    """Format harga ke Rupiah."""
    try:
        return f"{int(price):,}".replace(",", ".")
    except Exception:
        return str(price)


def _clean_product_name(name: str) -> str:
    """
    Bersihkan nama produk dari teks boilerplate Shopee dan link yang ikut masuk.
    Contoh input: "Temukan Serum Vitamin C seharga Rp89.000. Dapatkan sekarang juga di Shopee! https://s.shopee.co.id/xxx"
    Output: "Serum Vitamin C"
    """
    import re
    # Hapus prefix "Temukan "
    name = re.sub(r'^Temukan\s+', '', name.strip())
    # Hapus suffix " seharga Rp... Dapatkan sekarang juga di Shopee! <link>"
    name = re.sub(r'\s+seharga\s+Rp[\d.,]+.*$', '', name, flags=re.DOTALL)
    # Hapus URL yang tersisa
    name = re.sub(r'https?://\S+', '', name)
    return name.strip()


def generate_caption_template(product_name, link, price=None, rating=None, platform="general"):
    """Generate caption dari template (fallback, tanpa API)."""
    product_name = _clean_product_name(product_name)
    hashtags = _HASHTAGS.get(platform, _HASHTAGS["general"])

    if price is not None and rating is not None:
        template = random.choice(_TEMPLATES_WITH_PRICE)
        caption = template.format(
            nama=product_name,
            price=_format_price(price),
            rating=rating,
            link=link,
        )
    else:
        template = random.choice(_TEMPLATES_SIMPLE)
        caption = template.format(nama=product_name, link=link)

    return f"{caption}\n\n{hashtags}"


# ─────────────────────────────────────────────────────────────────────────────
# AI CAPTION — "Racun Belanja" style
# ─────────────────────────────────────────────────────────────────────────────

# Prompt utama: gaya "racun belanja" — teman yang kasih rekomendasi jujur
_SYSTEM_PROMPT = """Kamu adalah content creator yang ahli bikin konten "racun belanja" di media sosial Indonesia.
Gaya kamu: casual, relatable, jujur, seperti teman yang cerita pengalaman pakai produk.
Bukan iklan. Bukan sales pitch. Tapi tetap bikin orang penasaran dan pengen beli.
JANGAN gunakan emoji atau emoticon."""

_PLATFORM_RULES = {
    "Twitter": (
        "Buat caption SANGAT singkat, maks 200 karakter sebelum link. "
        "Satu kalimat hook yang bikin penasaran."
    ),
    "Facebook": (
        "Buat caption 3-5 kalimat. Boleh sedikit lebih panjang dan storytelling. "
        "Akhiri dengan hashtag: #racunshopee #rekomendasiproduk"
    ),
    "Pinterest": (
        "Buat caption 2-4 kalimat yang deskriptif. "
        "Akhiri dengan banyak hashtag: #racunshopee #racunbelanja #rekomendasiproduk #shopee #belanjashopee"
    ),
    "Telegram": (
        "Buat caption informatif 3-4 kalimat. "
        "Akhiri dengan hashtag: #racunshopee #rekomendasiproduk"
    ),
    "Threads": (
        "Buat caption singkat dan casual, 2-3 kalimat. "
        "Gaya Threads/Instagram — conversational, relatable. "
        "Akhiri dengan hashtag: #racunshopee #racunbelanja"
    ),
    "general": (
        "Buat caption 3-4 kalimat yang natural dan relatable."
    ),
}

# Variasi opening agar tidak monoton
_OPENING_VARIANTS = [
    "Cerita dari sudut pandang orang yang baru nemuin produk ini dan kaget ternyata bagus.",
    "Cerita dari sudut pandang orang yang udah lama nyari solusi dan akhirnya ketemu produk ini.",
    "Cerita dari sudut pandang orang yang awalnya skeptis tapi ternyata produk ini beneran ngaruh.",
    "Cerita dari sudut pandang orang yang direkomendasiin temen dan ternyata emang worth it.",
    "Cerita dari sudut pandang orang yang nyesel baru tau produk ini sekarang.",
]


def generate_caption_ai(product_name, link, price=None, rating=None, platform="general"):
    """
    Generate caption pakai AI dengan gaya 'racun belanja'.
    Fallback ke template kalau API tidak tersedia atau error.
    """
    api_key = config('OPENAI_API_KEY', default=None)
    if not api_key:
        print("[WARN] OPENAI_API_KEY tidak ditemukan, fallback ke template")
        return generate_caption_template(product_name, link, price, rating, platform)

    try:
        return _call_ai(product_name, link, price, rating, platform, api_key)
    except Exception as e:
        print(f"[WARN] AI caption error: {e}, fallback ke template")
        return generate_caption_template(product_name, link, price, rating, platform)


def _call_ai(product_name, link, price, rating, platform, api_key):
    import requests as req

    product_name = _clean_product_name(product_name)
    base_url = config('OPENAI_API_BASE', default='https://opencode.ai/zen/go/v1')
    platform_rule = _PLATFORM_RULES.get(platform, _PLATFORM_RULES["general"])
    opening_variant = random.choice(_OPENING_VARIANTS)

    price_text = f"Harga: Rp {_format_price(price)}" if price is not None else ""
    rating_text = f"Rating: {rating}/5" if rating is not None else ""

    prompt = f"""Buat caption media sosial untuk produk berikut dengan gaya "racun belanja".

Produk: {product_name}
{price_text}
{rating_text}
Link: {link}

Instruksi gaya:
- {opening_variant}
- Tone: santai, informal, relatable — seperti chat ke teman dekat
- Jangan terdengar seperti iklan atau sales pitch
- Fokus pada "eh ini ternyata bagus banget" bukan "BUY NOW LIMITED OFFER"
- Boleh cerita masalah dulu, terus kasih solusi (problem → discovery → result)
- Autentik, seperti UGC (user generated content)

Format untuk platform {platform}:
- {platform_rule}

Rules wajib:
1. Tulis dalam Bahasa Indonesia
2. JANGAN gunakan emoji atau emoticon
3. Sertakan link di akhir caption (sebelum hashtag)
4. Langsung tulis captionnya saja, tanpa penjelasan tambahan"""

    response = req.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "qwen3.6-plus",
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500,
            "temperature": 0.9,
        },
        timeout=120,
    )

    data = response.json()

    if "choices" not in data or not data["choices"]:
        print(f"[WARN] AI caption: no choices in response: {data}")
        return generate_caption_template(product_name, link, price, rating, platform)

    message = data["choices"][0]["message"]
    caption = message.get("content", "").strip()

    # Beberapa model taruh output di reasoning kalau content kosong
    if not caption:
        caption = message.get("reasoning", "").strip()

    if not caption:
        print(f"[WARN] AI caption: empty response, fallback ke template")
        return generate_caption_template(product_name, link, price, rating, platform)

    # Pastikan link ada di caption
    if link not in caption:
        caption += f"\n\n{link}"

    return caption


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def generate_caption(product_name, link, price=None, rating=None, platform="general", use_ai=True):
    """
    Generate caption otomatis dengan gaya 'racun belanja'.

    Default pakai AI (use_ai=True). Kalau API key tidak ada atau error,
    otomatis fallback ke template.

    Args:
        product_name : Nama produk
        link         : Link affiliate
        price        : Harga produk (opsional)
        rating       : Rating produk (opsional)
        platform     : "Facebook" | "Threads" | "Pinterest" | "Telegram" | "Twitter" | "general"
        use_ai       : True = pakai AI, False = pakai template saja

    Returns:
        str: Caption siap posting
    """
    if use_ai:
        return generate_caption_ai(product_name, link, price, rating, platform)
    return generate_caption_template(product_name, link, price, rating, platform)
