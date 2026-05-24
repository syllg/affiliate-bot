from bot.token_manager import get_page_token
import os

token = get_page_token()
if token:
    # Read current .env
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and replace FACEBOOK_ACCESS_TOKEN
    new_lines = []
    for line in lines:
        if line.startswith('FACEBOOK_ACCESS_TOKEN='):
            new_lines.append(f'FACEBOOK_ACCESS_TOKEN={token}\n')
        else:
            new_lines.append(line)
    
    # Write back
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n[OK] Token saved to .env")
    print(f"[INFO] Token length: {len(token)} chars")
else:
    print("[ERR] Failed to get token")
