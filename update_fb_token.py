from decouple import config
import re
import sys

def update_facebook_token(new_token):
    """Update Facebook access token in .env file."""
    if not new_token or len(new_token) < 10:
        print("Error: Token is too short or empty.")
        return False
    
    # Read current .env
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: .env file not found. Create it first from .env.example")
        return False
    
    # Find and replace the Facebook access token
    pattern = r'FACEBOOK_ACCESS_TOKEN=[^\n]+'
    replacement = f'FACEBOOK_ACCESS_TOKEN={new_token}'
    
    if not re.search(pattern, content):
        print("Error: FACEBOOK_ACCESS_TOKEN not found in .env")
        return False
    
    new_content = re.sub(pattern, replacement, content)
    
    # Write back
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('Facebook token updated successfully!')
    print(f'New token: {new_token[:20]}...{new_token[-10:]}')
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_fb_token.py <NEW_TOKEN>")
        print("Example: python update_fb_token.py EAAH...")
        sys.exit(1)
    
    token = sys.argv[1]
    update_facebook_token(token)
