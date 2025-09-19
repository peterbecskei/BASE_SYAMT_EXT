"""
Simple background runner (Python) replicating core parts of background.js
- No Chrome APIs
- No UI
- Minimal imports (stdlib only)
- Persists data to URL_data.csv and LastID.TXT in current working directory
"""

import csv
import os
import time
import json
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class Config:
    # Adjust as needed
    # START_ID falls back to value in LastID.TXT if present
    START_ID = 1251923
    BASE_URL = 'https://www.automobile.at/boerse/expose/'
    CHECK_INTERVAL_SECONDS = 0.65  # 650 ms

    URL_DATA_CSV = 'URL_data.csv'
    LAST_ID_FILE = 'LastID.TXT'


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def load_last_id() -> int:
    if os.path.exists(Config.LAST_ID_FILE):
        try:
            with open(Config.LAST_ID_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return int(content)
        except Exception:
            pass
    return int(Config.START_ID)


def save_last_id(last_id: int) -> None:
    try:
        with open(Config.LAST_ID_FILE, 'w', encoding='utf-8') as f:
            f.write(str(int(last_id)))
    except Exception:
        pass


def load_url_data() -> dict:
    data = {}
    if not os.path.exists(Config.URL_DATA_CSV):
        return data
    try:
        with open(Config.URL_DATA_CSV, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    _id = int(row.get('id', '').strip())
                except Exception:
                    continue
                data[_id] = {
                    'exists': (row.get('exists', 'false').lower() == 'true'),
                    'url': row.get('url', ''),
                    'timestamp': row.get('timestamp', ''),
                    'elemdata': row.get('elemdata', ''),
                }
    except Exception:
        pass
    return data


def save_url_data(data: dict) -> None:
    # Persist entire map each time for simplicity
    fields = ['id', 'exists', 'url', 'timestamp', 'elemdata']
    try:
        with open(Config.URL_DATA_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for _id in sorted(data.keys()):
                entry = data[_id]
                writer.writerow({
                    'id': _id,
                    'exists': 'true' if entry.get('exists') else 'false',
                    'url': entry.get('url', ''),
                    'timestamp': entry.get('timestamp', ''),
                    'elemdata': entry.get('elemdata', ''),
                })
    except Exception:
        pass


def update_last_id_from_data(url_data: dict, current_last_id: int) -> int:
    candidates = [int(k) for k, v in url_data.items() if v and v.get('exists') is True]
    if candidates:
        new_last = max(candidates)
        if new_last != current_last_id:
            save_last_id(new_last)
        return new_last
    return current_last_id


def http_status(url: str, method: str = 'GET') -> int:
    # Use urllib with minimal deps
    req = Request(url=url, method=method, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urlopen(req, timeout=20) as resp:
            return getattr(resp, 'status', 200)  # Py3 returns .status
    except HTTPError as e:
        return e.code
    except URLError:
        return 0
    except Exception:
        return 0


def check_url(url_data: dict, _id: int) -> bool:
    url = f"{Config.BASE_URL}{_id}"
    status = http_status(url, method='GET')

    # Handle simple rate-limit/captcha cases similarly
    if status == 429:
        print(f"ID {_id}: 429 várakozás 60s")
        time.sleep(61)
        status = http_status(url, method='GET')
    elif status == 302:
        print(f"ID {_id}: 302 captcha/redirect, várakozás 60s")
        time.sleep(60)
        status = http_status(url, method='GET')

    if status == 200:
        
        url_data[_id] = {
            'exists': True,
            'url': url,
            'timestamp': now_iso(),
            'elemdata': '',  # keep simple; can be extended
        }
        return True
    else:
        url_data[_id] = {
            'exists': False,
            'url': url,
            'timestamp': now_iso(),
            'elemdata': '',
        }
        return False


def start_checking():
    url_data = load_url_data()
    last_id = load_last_id()
    print('Kezdés. LastID =', last_id)

    # Simple range window like background.js (e.g., +100)
    upper = last_id + 100
    for _id in range(last_id, upper + 1):
        # Skip if already known
        if _id in url_data and ('exists' in url_data[_id]):
            print(f"ID {_id}: Már ellenőrizve korábban")
            continue

        ok = check_url(url_data, _id)
        # Persist after each check to be robust
        save_url_data(url_data)

        # Update LastID based on known good items
        last_id = update_last_id_from_data(url_data, last_id)
        save_last_id(last_id if ok else last_id)

        time.sleep(Config.CHECK_INTERVAL_SECONDS)

    print('Ellenőrzés befejeződött')


if __name__ == '__main__':
    start_checking()



