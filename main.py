import sys
import time
import schedule
from bot.botFacebook import *
from bot.botTwitter import *
from bot.botPinterest import *
from bot.botTelegram import *
from bot.botThreads import *
from bot.botReplyTwitter import *
from bot.postVideoTwiiter import *
from bot.token_manager import (
    ensure_tokens_active,
    _auto_refresh_threads_daily,
)
from function_list import *


def _schedule_safe(name, job_func):
    """Schedule a job — skip if not found, inactive, or set_time invalid (0)."""
    result = funtion(name)
    if not result or len(result) == 0:
        print(f"[WARN] Skipped {name} (not found in function_bot table)")
        return
    row = result[0]
    if row.get('is_active') != 1:
        print(f"[SKIP] {name} is inactive")
        return
    set_time = row.get('set_time', 0)
    if not set_time or int(set_time) <= 0:
        print(f"[WARN] Skipped {name} (set_time={set_time} invalid)")
        return
    schedule.every(int(set_time)).minutes.do(job_func)
    print(f"[OK] Scheduled {name} every {set_time} min")


# ─────────────────────────────────────────────────────────────────────────────
# TOKEN PIPELINE: reload .env → cek → auto-refresh sebelum bot jalan
# ─────────────────────────────────────────────────────────────────────────────
token_status = ensure_tokens_active()

if not token_status['facebook'] and not token_status['threads']:
    print("[STOP] Semua token tidak aktif. Bot tidak dapat dijalankan.")
    print("[INFO] Jalankan: python setup_token.py untuk setup token.")
    sys.exit(1)

if not token_status['facebook']:
    print("[WARN] Facebook token tidak aktif. Posting Facebook akan dilewati.")
if not token_status['threads']:
    print("[WARN] Threads token tidak aktif. Posting Threads akan dilewati.")

# ─────────────────────────────────────────────────────────────────────────────
# SCHEDULER
# ─────────────────────────────────────────────────────────────────────────────

# Auto-refresh Threads token setiap hari jam 03:00 (fully otomatis)
schedule.every().day.at("03:00").do(_auto_refresh_threads_daily)
print("[OK] Scheduled daily Threads token refresh at 03:00")

# Twitter - DISABLED (403 Forbidden - limited API access)
# _schedule_safe('autoposting', autoposting)
# _schedule_safe('autoRetweetNonEleved', autoRetweetNonEleved)
# _schedule_safe('autoRepostNonEleved', autoRepostNonEleved)
# _schedule_safe('autopostingAkunBackUp', autopostingAkunBackUp)
# _schedule_safe('autopostingTrendingTopik', autopostingTrendingTopik)

# Video posting (Facebook, Pinterest, Telegram, Threads)
_schedule_safe('postingVideo', postingVideo)

# Reply Twitter
# _schedule_safe('posting', posting)

# Telegram
_schedule_safe('autoPostingTelegram', autoPostingTelegram)

# Pinterest
_schedule_safe('autoPostingPinterest', autoPostingPinterest)

# Facebook
_schedule_safe('autoPostingFacebook', autoPostingFacebook)

# Threads
_schedule_safe('autoPostingThreads', autoPostingThreads)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────
bar = [".     ", " .    ", "  .   ", "   .  ", "    . ", "     .",
       "    . ", "   .  ", "  .   ", " .    "]
i = 0

while True:
    print("The bot is running", bar[i % len(bar)], end="\r")
    try:
        schedule.run_pending()
    except Exception as e:
        print(f"\n[ERR] Exception pada scheduled job: {e}")
        if "empty range" in str(e) or "randrange" in str(e):
            raise
    time.sleep(1)
    i += 1
