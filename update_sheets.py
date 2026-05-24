import sys
sys.path.insert(0, r'C:\Users\sylvi\works\auto-affiliate-bot')

from bot.database import get_worksheet

# Update account_eleved in Google Sheets
ws = get_worksheet('account_eleved')
records = ws.get_all_records()

print(f"Current data: {records}")

# Update row 2 (first data row, header is row 1)
# Column E = ACCESS_TOKEN, Column F = SECRET_ACCESS_TOKEN
ws.update_cell(2, 5, '2054825447867994112-MyjcpKwI9to2WtD3jBJ80rPC4jI3gQ')  # E2
ws.update_cell(2, 6, 'rEeNHXCig13PNyGRYtJyC5wJrk9GxcVFVmuPPnquNefcu')  # F2

print("[OK] Google Sheets updated")

# Verify
records = ws.get_all_records()
print(f"Updated data: {records}")
