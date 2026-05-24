import sys
import os

# Tambahin path biar bisa import dari bot/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.token_manager import (
    exchange_long_lived_token,
    get_page_token,
    save_token_to_env,
    check_token_validity,
    is_page_token,
    exchange_threads_token,
    check_threads_token,
)


def setup_facebook_from_graph_api_explorer():
    """
    Setup Facebook token pakai token dari Graph API Explorer.
    Flow: paste token → exchange long-lived → get page token (permanent) → save .env
    """
    print("=" * 60)
    print("FACEBOOK TOKEN SETUP - Graph API Explorer")
    print("=" * 60)
    print()
    print("Langkah-langkah:")
    print("1. Buka https://developers.facebook.com/tools/explorer/")
    print("2. Pilih Aplikasi kamu di dropdown")
    print("3. Klik 'Generate Access Token'")
    print("4. Beri permission: pages_show_list, pages_manage_posts, pages_read_engagement")
    print("5. Copy token yang muncul")
    print()

    token = input("Paste token dari Graph API Explorer: ").strip()
    if not token:
        print("[ERR] Token kosong")
        return False

    # Simpan sementara ke .env
    print("[INFO] Menyimpan token sementara...")
    save_token_to_env('FACEBOOK_ACCESS_TOKEN', token)

    # Cek valid
    if not check_token_validity():
        print("[ERR] Token tidak valid. Coba generate ulang di Graph API Explorer.")
        return False

    # Exchange ke long-lived
    print("[INFO] Exchanging ke long-lived token (60 hari)...")
    long_token = exchange_long_lived_token()
    if not long_token:
        print("[ERR] Gagal exchange. Token mungkin sudah expired.")
        return False

    # Get page token (permanent)
    print("[INFO] Mengambil Page Token (permanent)...")
    page_token = get_page_token()
    if page_token:
        print("[OK] Berhasil! Facebook Page Token (permanent) sudah disimpan di .env")
        print("[INFO] Token ini tidak akan expire lagi.")
        return True
    else:
        print("[WARN] Gagal ambil Page Token. Long-lived token (60 hari) disimpan.")
        print("[INFO] Coba jalankan lagi nanti: python bot/token_manager.py page")
        return True


def setup_threads_from_graph_api_explorer():
    """
    Setup Threads token pakai token dari Graph API Explorer.
    Flow: paste token → exchange long-lived (60 hari) → save .env
    """
    print("=" * 60)
    print("THREADS TOKEN SETUP - Graph API Explorer")
    print("=" * 60)
    print()
    print("Langkah-langkah:")
    print("1. Buka https://developers.facebook.com/tools/explorer/")
    print("2. Pilih Aplikasi kamu di dropdown")
    print("3. Klik 'Generate Access Token'")
    print("4. Beri permission: threads_basic, threads_manage_posts, threads_content_publish")
    print("5. Copy token yang muncul")
    print()

    token = input("Paste token dari Graph API Explorer: ").strip()
    if not token:
        print("[ERR] Token kosong")
        return False

    # Simpan sementara ke .env
    print("[INFO] Menyimpan token sementara...")
    save_token_to_env('THREADS_ACCESS_TOKEN', token)

    # Cek valid
    if not check_threads_token():
        print("[ERR] Token tidak valid untuk Threads.")
        print("[INFO] Pastikan:")
        print("  - Aplikasi sudah dikoneksi ke Threads")
        print("  - Permission threads_manage_posts sudah diberikan")
        return False

    # Exchange ke long-lived
    print("[INFO] Exchanging ke long-lived token (60 hari)...")
    new_token = exchange_threads_token()
    if new_token:
        print("[OK] Berhasil! Threads long-lived token disimpan di .env")
        print("[INFO] Token ini berlaku 60 hari. Setelah itu perlu refresh lagi.")
        print("[INFO] Untuk refresh nanti: python bot/token_manager.py auto-th")
        return True
    else:
        print("[WARN] Gagal exchange. Token short-lived masih bisa dipakai sementara.")
        return True


def main():
    print("Facebook & Threads Token Setup via Graph API Explorer")
    print("=" * 60)
    print()
    print("Pilih platform:")
    print("1. Facebook (Page Token - Permanent)")
    print("2. Threads (Long-lived Token - 60 hari)")
    print("3. Keduanya")
    print()

    choice = input("Pilih (1/2/3): ").strip()

    if choice == '1':
        setup_facebook_from_graph_api_explorer()
    elif choice == '2':
        setup_threads_from_graph_api_explorer()
    elif choice == '3':
        setup_facebook_from_graph_api_explorer()
        print()
        print("-" * 60)
        print()
        setup_threads_from_graph_api_explorer()
    else:
        print("[ERR] Pilihan tidak valid")
        sys.exit(1)

    print()
    print("[OK] Setup selesai! Sekarang kamu bisa jalankan bot:")
    print("  python main.py")


if __name__ == "__main__":
    main()
