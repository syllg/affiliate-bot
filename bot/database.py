import re
import time
import gspread
import requests
import urllib3
from google.oauth2.service_account import Credentials
from decouple import config

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

GOOGLE_SHEET_ID = config('GOOGLE_SHEET_ID')

_client = None
_spreadsheet = None
_worksheet_cache = {}
_records_cache = {}

_MAX_RETRIES = 3
_BASE_DELAY = 2
_CACHE_TTL_SECONDS = int(config('GOOGLE_SHEET_CACHE_TTL', default=60))


def _with_retries(func):
    """Decorator untuk retry koneksi saat terjadi error jaringan transient."""
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                urllib3.exceptions.ProtocolError,
            ) as e:
                last_exception = e
                if attempt == _MAX_RETRIES:
                    break
                sleep_time = _BASE_DELAY * (2 ** (attempt - 1))
                print(f"[WARN] Koneksi ke Google Sheets gagal (attempt {attempt}/{_MAX_RETRIES}): {e}. Retry dalam {sleep_time}s...")
                time.sleep(sleep_time)
        raise last_exception
    return wrapper


def get_client():
    """Lazy-load gspread client menggunakan service account."""
    global _client
    if _client is None:
        creds = Credentials.from_service_account_file(
            'service_account.json', scopes=SCOPES
        )
        _client = gspread.authorize(creds)
    return _client


def get_spreadsheet():
    """Cache spreadsheet object agar tidak open_by_key berulang."""
    global _spreadsheet
    if _spreadsheet is None:
        client = get_client()
        _spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
    return _spreadsheet


@_with_retries
def get_worksheet(table_name):
    """Ambil worksheet dari Google Sheets berdasarkan nama tab."""
    worksheet = _worksheet_cache.get(table_name)
    if worksheet is None:
        spreadsheet = get_spreadsheet()
        worksheet = spreadsheet.worksheet(table_name)
        _worksheet_cache[table_name] = worksheet
    return worksheet


def invalidate_cache(table_name=None):
    """Hapus cache worksheet/records untuk satu tab atau seluruh tab."""
    if table_name:
        _worksheet_cache.pop(table_name, None)
        _records_cache.pop(table_name, None)
        return

    _worksheet_cache.clear()
    _records_cache.clear()


def _is_cache_fresh(cached_at):
    return (time.time() - cached_at) < _CACHE_TTL_SECONDS


@_with_retries
def get_records(table_name, use_cache=True):
    """Ambil records worksheet dengan cache TTL untuk menekan quota API."""
    cached = _records_cache.get(table_name)
    if use_cache and cached and _is_cache_fresh(cached['cached_at']):
        return [dict(record) for record in cached['records']]

    worksheet = get_worksheet(table_name)
    records = worksheet.get_all_records()
    _records_cache[table_name] = {
        'cached_at': time.time(),
        'records': records,
    }
    return [dict(record) for record in records]


def _parse_where(where_clause):
    """Parse WHERE clause sederhana."""
    conditions = []
    parts = [p.strip() for p in where_clause.split(' AND ')]
    for part in parts:
        if '<>' in part:
            key, val = part.split('<>', 1)
            conditions.append((key.strip(), val.strip().strip("'\""), '!='))
        elif '=' in part:
            key, val = part.split('=', 1)
            conditions.append((key.strip(), val.strip().strip("'\""), '=='))
    return conditions


def _check_condition(record, key, val, op):
    """Cek apakah record memenuhi kondisi WHERE."""
    actual = str(record.get(key, ''))
    if op == '==':
        return actual == val
    elif op == '!=':
        return actual != val
    return False


@_with_retries
def db_connection(query):
    """
    Eksekusi query SELECT sederhana ke Google Sheets.
    Format yang didukung:
      SELECT * FROM table_name
      SELECT * FROM table_name WHERE col = 'value'
      SELECT * FROM table_name WHERE col1 = 'val1' AND col2 = 1
      SELECT col1, col2 FROM table_name
    """
    match = re.match(
        r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?',
        query,
        re.IGNORECASE
    )
    if not match:
        return []

    columns_str, table_name, where_clause = match.groups()
    records = get_records(table_name)

    # Filter WHERE clause
    if where_clause:
        conditions = _parse_where(where_clause)
        records = [
            r for r in records
            if all(_check_condition(r, k, v, op) for k, v, op in conditions)
        ]

    # Filter kolom jika bukan SELECT *
    if columns_str.strip() != '*':
        cols = [c.strip() for c in columns_str.split(',')]
        records = [
            {k: v for k, v in r.items() if k in cols}
            for r in records
        ]

    return records
