# Auto Affiliate Bot

Bot otomatis untuk mempromosikan produk Shopee Affiliate ke berbagai platform media sosial (Facebook, Pinterest, Telegram, Threads). Bot membaca data produk dan konfigurasi akun dari **Google Sheets**
> **Update Terbaru**: 
> - ✅ **Threads** ditambahkan sebagai platform baru
> - ✅ **AI Caption Generator** dengan OpenCode (Qwen3.6 Plus)
> - ✅ **Video Posting** ke Facebook, Pinterest, Telegram, Threads
> - ✅ **Token Manager** untuk auto-refresh Facebook & Threads token
> - ❌ **Twitter/X** dinonaktifkan (silakan aktifkan jika perlu)

## Status Platform

| Platform | Status | 
|----------|--------|
| **Facebook** | ✅ Jalan | 
| **Pinterest** | ✅ Jalan | 
| **Telegram** | ✅ Jalan |
| **Threads** | ✅ Jalan |
| **Twitter/X** | ❌ Dinonaktifkan (silakan aktifkan jika perlu) |

## Fitur

### Platform Support
- **Facebook**: Auto posting ke halaman Facebook (text + image + video)
- **Pinterest**: Auto pin dengan deskripsi dan hashtag otomatis (image + video)
- **Telegram**: Auto posting ke channel Telegram (text + image + video)
- **Threads**: Auto posting ke Threads (text + image + video)
- **Twitter/X**: ❌ Dinonaktifkan sementara (silakan aktifkan jika perlu) 

### AI Caption Generator
- Generate caption otomatis menggunakan **OpenCode API** dengan model **Qwen3.6 Plus**
- Gaya bahasa: curhat/pengalaman pribadi (bukan iklan keras)
- Support platform hints untuk tiap platform
- Fallback ke template-based caption jika AI error

### Video Posting
- Download video dari URL Shopee
- Post video ke: Facebook, Pinterest, Telegram, Threads
- Extract cover image untuk Pinterest video pin

### Token Manager
- Auto-generate long-lived token Facebook (60 hari)
- Generate permanent page token
- Generate URL OAuth untuk Threads
- Cek validasi token

## Struktur Project

```
auto-affiliate-bot/
├── main.py                 # Entry point, scheduler semua bot
├── Makefile               # Perintah cepat untuk menjalankan fitur
├── function_list.py        # Konfigurasi fungsi bot dari database
├── requirements.txt        # Dependencies Python
├── .env                    # File environment variables (buat sendiri dari .env.example)
├── bot/
│   ├── botFacebook.py      # Bot Facebook
│   ├── botPinterest.py     # Bot Pinterest
│   ├── botTelegram.py      # Bot Telegram
│   ├── botThreads.py       # Bot Threads (NEW)
│   ├── postVideoTwiiter.py # Bot posting video ke semua platform
│   ├── caption_generator.py# AI Caption Generator (OpenCode)
│   ├── token_manager.py    # Token manager (Facebook & Threads)
│   ├── image_utils.py      # Image helper functions
│   ├── utils.py            # Helper functions (shortLinkShopee)
│   └── database.py         # Koneksi ke Google Sheets
├── shopee_affiliate/
│   └── __init__.py         # Shopee Affiliate API client
├── cred_root/              # Credential Pinterest (auto-generated)
└── file/                   # File pendukung
```

## Quick Start (Makefile)

### Install & Setup
```bash
make install          # Install dependencies
make setup-env        # Copy .env.example ke .env
```

### Menjalankan Bot
```bash
make run              # Jalankan bot utama (scheduler)
make run-facebook     # Post 1x ke Facebook
make run-telegram     # Post 1x ke Telegram
make run-pinterest    # Post 1x ke Pinterest
make run-threads      # Post 1x ke Threads
make run-video        # Post video ke semua platform
```

### Token Management
```bash
make token-check      # Cek semua token valid
make token-refresh    # Perpanjang Facebook token (60 hari)
make token-page       # Generate permanent page token
make token-threads    # Generate URL OAuth untuk Threads
```

### Utility
```bash
make test             # Test semua koneksi
make clean            # Hapus file temporary
```

## Instalasi Manual

### 1. Clone Repository

```bash
git clone https://github.com/username/auto-affiliate-bot.git
cd auto-affiliate-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Copy file `.env.example` jadi `.env` dan isi dengan credential milikmu:

```bash
cp .env.example .env
```

Isi `.env` dengan data dari masing-masing platform:

```env
# Facebook (dari https://developers.facebook.com/)
FACEBOOK_PAGE_ID=your_facebook_page_id
FACEBOOK_ACCESS_TOKEN=your_facebook_page_access_token
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Pinterest (login credential kamu)
PINTEREST_EMAIL=your_pinterest_email
PINTEREST_PASSWORD=your_pinterest_password
PINTEREST_USERNAME=your_pinterest_username
PINTEREST_BOARD_ID=your_pinterest_board_id

# Telegram (dari @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_IDS=-1001234567890,-1009876543210

# Threads (dari https://developers.facebook.com/)
THREADS_USER_ID=your_threads_user_id
THREADS_ACCESS_TOKEN=your_threads_access_token

# AI Caption Generator (OpenCode)
OPENAI_API_KEY=sk-your_opencode_api_key
OPENAI_API_BASE=https://opencode.ai/zen/go/v1

# Google Sheets
GOOGLE_SHEET_ID=your_google_sheet_id
```

### 4. Setup Google Sheets

#### a. Buat Google Cloud Service Account

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru (atau gunakan yang existing)
3. Aktifkan **Google Sheets API** dan **Google Drive API**
4. Pergi ke **IAM & Admin > Service Accounts**
5. Buat service account baru
6. Buat key JSON dan download (simpan sebagai `service_account.json` di root project)

#### b. Buat Google Sheet

1. Buka [Google Sheets](https://sheets.google.com/) dan buat spreadsheet baru
2. Copy **Spreadsheet ID** dari URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. Paste ke `.env` di variabel `GOOGLE_SHEET_ID`
4. Share spreadsheet dengan email service account kamu (contoh: `nama-service@project-id.iam.gserviceaccount.com`)

#### c. Buat Tab/Sheet

Buat tab dengan nama-nama berikut di dalam spreadsheet:

| Tab Name | Wajib? | Keterangan |
|----------|--------|------------|
| `function_bot` | ✅ Wajib | Pengaturan aktif/nonaktif dan interval tiap bot |
| `database_post` | ✅ Wajib | Data produk untuk diposting (nama, link, gambar) |
| `product_video` | ⚪ Opsional | Data produk video untuk posting video |
| `account_eleved` | ⚪ Opsional | Akun Twitter elevated (tidak dipakai) |
| `account_shopeeaff` | ⚪ Opsional | Credential Shopee Affiliate |
| `account_non_eleved` | ⚪ Opsional | Akun Twitter non-elevated (tidak dipakai) |
| `account_backup` | ⚪ Opsional | Akun Twitter backup (tidak dipakai) |

#### d. Isi Data

**function_bot**

| name | is_active | set_time |
|------|-----------|----------|
| autoPostingFacebook | 1 | 3 |
| autoPostingPinterest | 1 | 2 |
| autoPostingTelegram | 1 | 1 |
| autoPostingThreads | 1 | 2 |
| postingVideo | 1 | 1 |

**database_post**

| product_name | product_link | product_img |
|--------------|--------------|-------------|
| Kaos Polos Premium | https://shopee.co.id/... | https://cf.shopee.co.id/... |
| Jaket Hoodie | https://shopee.co.id/... | `https://img1.jpg, https://img2.jpg, https://img3.jpg` |

> **Multi-Image Support**: Kolom `product_img` bisa isi **banyak URL pisah koma** untuk posting beberapa gambar sekaligus. Platform yang support multi-image: **Telegram**, **Facebook**. Pinterest dan Threads otomatis pakai gambar pertama saja.

**product_video** (opsional)

| name | price | product_url | video_url |
|------|-------|-------------|-----------|
| SKINFLAIR Lotion | 25000 | https://shopee.co.id/... | https://down-...mp4 |

## Cara Menjalankan

### Dengan Makefile (Rekomendasi)

```bash
# Jalankan bot utama (scheduler)
make run

# Post 1x ke platform tertentu
make run-facebook
make run-telegram
make run-pinterest
make run-threads

# Post video
make run-video

# Perpanjang token
make token-refresh
```

### Tanpa Makefile

```bash
# Jalankan bot utama
python main.py

# Post 1x ke platform
python -c "from bot.botFacebook import autoPostingFacebook; autoPostingFacebook()"
python -c "from bot.botTelegram import autoPostingTelegram; autoPostingTelegram()"
python -c "from bot.botPinterest import autoPostingPinterest; autoPostingPinterest()"
python -c "from bot.botThreads import autoPostingThreads; autoPostingThreads()"

# Post video
python -c "from bot.postVideoTwiiter import postingVideo; postingVideo()"

# Token management
python bot/token_manager.py check       # Cek Facebook token
python bot/token_manager.py check-th    # Cek Threads token
python bot/token_manager.py exchange    # Perpanjang Facebook token
python bot/token_manager.py page        # Generate page token
python bot/token_manager.py oauth-th    # Generate OAuth URL Threads
```

## Konfigurasi Fungsi

Setiap fungsi bot dapat diaktifkan/nonaktifkan dan diatur intervalnya melalui tab `function_bot` di Google Sheets:

| Fungsi | Deskripsi | Interval |
|--------|-----------|----------|
| `autoPostingFacebook` | Auto posting ke halaman Facebook | menit |
| `autoPostingPinterest` | Auto pin ke Pinterest | menit |
| `autoPostingTelegram` | Auto posting ke channel Telegram | menit |
| `autoPostingThreads` | Auto posting ke Threads | menit |
| `postingVideo` | Auto posting video ke semua platform | menit |

## Alur Kerja

1. Bot membaca konfigurasi dari tab `function_bot` di Google Sheets
2. Jika fungsi aktif (`is_active = 1`), bot akan jalan sesuai interval `set_time`
3. Bot mengambil data produk dari tab `database_post` (pilih random)
4. Bot generate caption otomatis dari nama produk (pakai AI atau template)
5. Bot generate short link affiliate via Shopee Affiliate API (kalau credential tersedia)
6. Kalau credential Shopee Affiliate belum ada, bot pakai **link asli dari spreadsheet**
7. Bot download gambar/video produk dari URL Shopee
8. Bot posting ke platform sesuai fungsi masing-masing

## Token Management

### Facebook Token

Token Facebook perlu diperpanjang secara berkala:

```bash
# Cek token masih valid atau tidak
make token-check

# Perpanjang ke long-lived token (60 hari)
make token-refresh

# Generate permanent page token (tidak expired)
make token-page
```

**Cara manual:**
1. Buka https://developers.facebook.com/tools/explorer/
2. Pilih App, generate User Token dengan permission `pages_manage_posts`
3. Tukar jadi long-lived token:
   ```bash
   python bot/token_manager.py exchange
   ```
4. Generate page token (permanent):
   ```bash
   python bot/token_manager.py page
   ```

### Threads Token

Threads menggunakan Meta Graph API yang sama dengan Facebook:

```bash
# Generate URL OAuth untuk mendapatkan token
make token-threads

# Buka URL di browser, login, copy token ke .env
```

**Cara manual:**
1. Buka https://developers.facebook.com/tools/explorer/
2. Pilih App: `35442965975351695`
3. Klik "Add a Permission" → tambah `threads_manage_posts`
4. Klik "Generate Access Token"
5. Copy token ke `.env`:
   ```env
   THREADS_ACCESS_TOKEN=token_baru
   ```

## AI Caption Generator

Bot menggunakan **OpenCode API** dengan model **Qwen3.6 Plus** untuk generate caption otomatis.

**Cara kerja:**
- Prompt dioptimasi untuk gaya curhat/pengalaman pribadi
- Contoh: *"Jujur dulu aku sering minder karena kulit tubuh belang..."*
- Fallback ke template-based caption jika AI error atau rate limit

**Konfigurasi di `.env`:**
```env
OPENAI_API_KEY=sk-your_opencode_api_key
OPENAI_API_BASE=https://opencode.ai/zen/go/v1
```

## Catatan Penting

### Facebook
- Wajib pakai **Page Access Token** (bukan User Token)
- Token didapat dari `GET /me/accounts` di Graph API Explorer
- Kalau token expired, jalankan `make token-refresh`

### Threads
- Threads User ID berbeda dengan Facebook Page ID
- User ID bisa dicek dengan query `GET /me` menggunakan Threads token
- Token harus punya permission `threads_manage_posts`

### Pinterest
- Board ID harus milik board yang sudah dibuat di akun Pinterest kamu
- Gunakan `py3pin` library, credential disimpan di folder `cred_root/`

### Shopee Affiliate
- Kalau `account_shopeeaff` belum diisi (dummy), bot otomatis fallback ke link asli dari spreadsheet
- Link di spreadsheet bisa langsung pakai Shopee short link yang sudah ada tracking affiliate

### Multi-Image Posting
- **Cara isi**: Di kolom `product_img`, tulis banyak URL dipisah koma:
  ```
  https://img1.jpg, https://img2.jpg, https://img3.jpg
  ```
- **Telegram**: Kirim semua gambar sebagai album (sendMediaGroup)
- **Facebook**: Upload semua gambar sebagai multi-photo post
- **Pinterest**: Hanya pakai gambar pertama
- **Threads**: Hanya pakai gambar pertama

## Troubleshooting

**Error: Spreadsheet not found**
- Pastikan `GOOGLE_SHEET_ID` benar
- Pastikan service account sudah di-share ke spreadsheet

**Error: Worksheet not found**
- Pastikan nama tab di Google Sheets persis sama dengan yang diharapkan (case-sensitive)

**Posting tidak jalan**
- Cek `is_active` di tab `function_bot` bernilai `1`
- Cek interval `set_time` tidak terlalu pendek

**Error gspread authentication**
- Pastikan file `service_account.json` ada di root project
- Pastikan Google Sheets API dan Drive API sudah diaktifkan di Google Cloud Console

**Facebook token expired**
- Jalankan `make token-refresh` untuk perpanjang token
- Atau generate baru dari Graph API Explorer

**Threads token invalid**
- Pastikan token punya permission `threads_manage_posts`
- Pastikan `THREADS_USER_ID` benar (bukan Instagram User ID)
- Generate token baru dari Graph API Explorer

**AI caption error**
- Cek `OPENAI_API_KEY` dan `OPENAI_API_BASE` di `.env`
- Kalau rate limit, bot otomatis fallback ke template caption

## Catatan Keamanan

- **Jangan pernah commit file `.env` dan `service_account.json` ke Git!**
- File `.env` sudah di-ignore di `.gitignore`
- Buat `service_account.json` baru jika credential bocor
- Rotate token API jika ada yang mencurigakan

## Changelog

### v2.0 (Latest)
- ✅ Tambah platform Threads
- ✅ AI Caption Generator dengan OpenCode (Qwen3.6 Plus)
- ✅ Video posting ke semua platform (Facebook, Pinterest, Telegram, Threads)
- ✅ Token Manager untuk auto-refresh token
- ✅ Makefile untuk perintah cepat
- ❌ Nonaktifkan Twitter/X (silakan aktifkan jika perlu)

### v1.0
- Auto posting ke Twitter, Facebook, Pinterest, Telegram
- Multi-image support
- Shopee Affiliate link generator
- Google Sheets integration
