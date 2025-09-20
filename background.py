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
import re
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class Config:
    # Adjust as needed
    # START_ID falls back to value in LastID.TXT if present
    START_ID = 1251923
    BASE_URL = 'https://www.automobile.at/boerse/expose/'
    CHECK_INTERVAL_SECONDS = 0.1  # 650 ms

    URL_DATA_CSV = 'URL_data.csv'
    LAST_ID_FILE = 'LastID.TXT'


class ELEMDATA:
    """Objektum JSON változók tárolására az elempar szövegből"""
    
    def __init__(self):
        self.title = ""
        self.isTaxDeductible = False
        self.price = 0
        self.year = 0
        self.mileage = 0
        self.fuel_type = ""
        self.transmission = ""
        self.power = 0
        self.color = ""
        self.brand = ""
        self.model = ""
        self.raw_data = ""
        
    def __str__(self):
        return f"ELEMDATA(title='{self.title}', price={self.price}, year={self.year}, mileage={self.mileage})"
    
    def to_dict(self):
        """Dictionary formátumba konvertálás"""
        return {
            'title': self.title,
            'isTaxDeductible': self.isTaxDeductible,
            'price': self.price,
            'year': self.year,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'power': self.power,
            'color': self.color,
            'brand': self.brand,
            'model': self.model,
            'raw_data': self.raw_data
        }


def parse_elempar_json(elempar_text: str) -> ELEMDATA:
    """
    elempar szöveges stringből JSON változókat kinyeri és ELEMDATA objektumban tárolja
    
    Args:
        elempar_text: A szöveges string ami JSON változókat tartalmaz
        
    Returns:
        ELEMDATA objektum a kinyert adatokkal
    """
    elemdata = ELEMDATA()
    elemdata.raw_data = elempar_text
    
    try:
        # JSON objektum keresése a szövegben
        # Keresünk egy teljes JSON objektumot
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_matches = re.findall(json_pattern, elempar_text)
        
        for json_str in json_matches:
            try:
                # JSON parse-olás
                data = json.loads(json_str)
                
                # Adatok kinyerése és tárolása
                if isinstance(data, dict):
                    elemdata.title = data.get('title', elemdata.title)
                    elemdata.isTaxDeductible = data.get('isTaxDeductible', elemdata.isTaxDeductible)
                    elemdata.price = data.get('price', elemdata.price)
                    elemdata.year = data.get('year', elemdata.year)
                    elemdata.mileage = data.get('mileage', elemdata.mileage)
                    elemdata.fuel_type = data.get('fuelType', elemdata.fuel_type)
                    elemdata.transmission = data.get('transmission', elemdata.transmission)
                    elemdata.power = data.get('power', elemdata.power)
                    elemdata.color = data.get('color', elemdata.color)
                    elemdata.brand = data.get('brand', elemdata.brand)
                    elemdata.model = data.get('model', elemdata.model)
                    
            except json.JSONDecodeError:
                continue
                
    except Exception as e:
        print(f"JSON parse hiba: {e}")
    
    # Ha nem találtunk JSON-t, próbáljuk regex-szel kinyerni az adatokat
    if not elemdata.title and elempar_text:
        # Cím keresése idézőjelek között
        title_match = re.search(r'"([^"]+)"', elempar_text)
        if title_match:
            elemdata.title = title_match.group(1)
        
        # Tax deductible keresése
        if 'isTaxDeductible' in elempar_text:
            elemdata.isTaxDeductible = True
            
        # Ár keresése számként
        price_match = re.search(r'"price":\s*(\d+)', elempar_text)
        if price_match:
            elemdata.price = int(price_match.group(1))
            
        # Év keresése
        year_match = re.search(r'"year":\s*(\d{4})', elempar_text)
        if year_match:
            elemdata.year = int(year_match.group(1))
            
        # Kilométer keresése
        mileage_match = re.search(r'"mileage":\s*(\d+)', elempar_text)
        if mileage_match:
            elemdata.mileage = int(mileage_match.group(1))
    
    return elemdata


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
                elemdata_str = row.get('elemdata', '')
                # Ha elemdata string, próbáljuk parse-olni
                if elemdata_str and elemdata_str != 'NA':
                    try:
                        # Ha JSON string, parse-oljuk
                        if elemdata_str.startswith('{'):
                            elemdata_dict = json.loads(elemdata_str)
                        else:
                            # Ha nem JSON, parse-oljuk az elempar szövegből
                            elemdata_obj = parse_elempar_json(elemdata_str)
                            elemdata_dict = elemdata_obj.to_dict()
                    except:
                        # Ha parse hiba, tároljuk stringként
                        elemdata_dict = {'raw_data': elemdata_str}
                else:
                    elemdata_dict = {'raw_data': 'NA'}
                
                data[_id] = {
                    'exists': (row.get('exists', 'false').lower() == 'true'),
                    'url': row.get('url', ''),
                    'timestamp': row.get('timestamp', ''),
                    'elemdata': elemdata_dict,
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
                elemdata = entry.get('elemdata', {})
                # ELEMDATA objektum JSON stringgé konvertálása
                if isinstance(elemdata, dict):
                    elemdata_str = json.dumps(elemdata, ensure_ascii=False)
                else:
                    elemdata_str = str(elemdata)
                
                writer.writerow({
                    'id': _id,
                    'exists': 'true' if entry.get('exists') else 'false',
                    'url': entry.get('url', ''),
                    'timestamp': entry.get('timestamp', ''),
                    'elemdata': elemdata_str,
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


def http_status(url: str, method: str = 'HEAD') -> int:
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


def get_api_data(api_url: str) -> ELEMDATA:
    # Get API response text és parse-olás ELEMDATA objektumba
    req = Request(url=api_url, method='GET', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urlopen(req, timeout=20) as resp:
            if resp.status == 200:
                elempar = resp.read().decode('utf-8')
                print(f"Raw elempar: {elempar[:100]}...")
                
                # JSON parse-olás ELEMDATA objektumba
                elemdata = parse_elempar_json(elempar)
                print(f"Parsed elemdata: {elemdata}")
                
                return elemdata
            else:
                # Hiba esetén üres ELEMDATA objektum
                error_elemdata = ELEMDATA()
                error_elemdata.raw_data = f"API_ERROR_{resp.status}"
                return error_elemdata
    except HTTPError as e:
        error_elemdata = ELEMDATA()
        error_elemdata.raw_data = f"API_ERROR_{e.code}"
        return error_elemdata
    except URLError:
        error_elemdata = ELEMDATA()
        error_elemdata.raw_data = "API_ERROR_CONNECTION"
        return error_elemdata
    except Exception:
        error_elemdata = ELEMDATA()
        error_elemdata.raw_data = "API_ERROR_UNKNOWN"
        return error_elemdata


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
        urlapi = f"https://api.automobile.at/api/v1/public/listing/{_id}"
        elemdata = get_api_data(urlapi)
    
        url_data[_id] = {
            'exists': True,
            'url': url,
            'timestamp': now_iso(),
            'elemdata': elemdata.to_dict(),  # ELEMDATA objektum dictionary formátumba
        }
        print(f"ID {_id}: {elemdata}")
        return True
    else:
        url_data[_id] = {
            'exists': False,
            'url': url,
            'timestamp': now_iso(),
            'elemdata': 'NA',
        }
        return False



def start_checking():
    url_data = load_url_data()
    last_id = load_last_id()
    print('Kezdés. LastID =', last_id)

    # Simple range window like background.js (e.g., +100)
    upper = last_id + 30
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


def test_parser():
    """Tesztelő függvény a parser működésének demonstrálására"""
    print("=== ELEMDATA Parser Teszt ===")
    
    # Teszt adatok a CSV-ből
    test_cases = [
        '" T-Cross Friends TSI DSG"",""isTaxDeductib"',
        'rcedes GLE Coupé AMG GLE 53 HYBRID 4MATI',
        '"ugeot 5008 1,5 BHDI 130 S&S EAT8 *Leder*"',
        '"W 320 d xDrive Touring"",""isTaxDeductible"',
        '"rsche Macan Turbo 3,6 DSG Allrad"",""isTax"'
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Teszt {i} ---")
        print(f"Input: {test_data}")
        
        elemdata = parse_elempar_json(test_data)
        print(f"Parsed: {elemdata}")
        print(f"Dictionary: {elemdata.to_dict()}")
    
    # Komplex JSON teszt
    print(f"\n--- Komplex JSON Teszt ---")
    complex_json = '{"title": "BMW X5 xDrive30d", "price": 45000, "year": 2020, "mileage": 25000, "fuelType": "Diesel", "transmission": "Automatic", "power": 265, "color": "Black", "brand": "BMW", "model": "X5", "isTaxDeductible": true}'
    print(f"Input: {complex_json}")
    
    elemdata = parse_elempar_json(complex_json)
    print(f"Parsed: {elemdata}")
    print(f"Dictionary: {elemdata.to_dict()}")
    
    print("\n=== Teszt befejezve ===")


def demo_usage():
    """Demonstráció a parser használatáról"""
    print("\n=== Parser Használati Példa ===")
    
    # Példa elempar szöveg
    sample_elempar = '{"title": "Audi A4 2.0 TDI", "price": 32000, "year": 2019, "mileage": 45000, "fuelType": "Diesel", "isTaxDeductible": false}'
    
    print(f"Eredeti elempar: {sample_elempar}")
    
    # Parse-olás
    elemdata = parse_elempar_json(sample_elempar)
    
    # Adatok elérése
    print(f"\nKinyert adatok:")
    print(f"- Cím: {elemdata.title}")
    print(f"- Ár: {elemdata.price:,} EUR")
    print(f"- Év: {elemdata.year}")
    print(f"- Kilométer: {elemdata.mileage:,} km")
    print(f"- Üzemanyag: {elemdata.fuel_type}")
    print(f"- Adólevonható: {'Igen' if elemdata.isTaxDeductible else 'Nem'}")
    
    # Dictionary formátum
    print(f"\nDictionary formátum:")
    data_dict = elemdata.to_dict()
    for key, value in data_dict.items():
        if key != 'raw_data':  # raw_data kihagyása a tisztaságért
            print(f"  {key}: {value}")
    
    print("\n=== Példa befejezve ===")


if __name__ == '__main__':
    # Teszt futtatása
    #test_parser()
    # demo_usage()
    
    # Normál működés
    start_checking()



