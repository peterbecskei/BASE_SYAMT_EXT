# ELEMDATA Parser Dokumentáció

## Áttekintés

Ez a parser az `elempar` szöveges stringekből JSON változókat nyer ki és egy `ELEMDATA` objektumban tárolja őket. A parser képes feldolgozni mind teljes JSON objektumokat, mind részleges szövegeket.

## Főbb Komponensek

### 1. ELEMDATA Osztály

```python
class ELEMDATA:
    def __init__(self):
        self.title = ""           # Jármű címe
        self.isTaxDeductible = False  # Adólevonható-e
        self.price = 0            # Ár
        self.year = 0             # Évjárat
        self.mileage = 0          # Kilométeróra állása
        self.fuel_type = ""       # Üzemanyag típusa
        self.transmission = ""    # Váltó típusa
        self.power = 0            # Teljesítmény (LE)
        self.color = ""           # Szín
        self.brand = ""           # Márka
        self.model = ""           # Modell
        self.raw_data = ""        # Eredeti szöveg
```

### 2. parse_elempar_json() Függvény

Ez a fő parser függvény, amely:
- JSON objektumokat keres a szövegben
- Regex-szel kinyeri az adatokat, ha nincs teljes JSON
- ELEMDATA objektumot ad vissza

## Használat

### Alapvető használat:

```python
from background import parse_elempar_json

# Szöveg feldolgozása
elempar_text = '"BMW X5 xDrive30d"",""isTaxDeductible"'
elemdata = parse_elempar_json(elempar_text)

# Adatok elérése
print(f"Cím: {elemdata.title}")
print(f"Adólevonható: {elemdata.isTaxDeductible}")
```

### Teljes JSON objektum:

```python
json_text = '{"title": "Audi A4", "price": 25000, "year": 2020}'
elemdata = parse_elempar_json(json_text)
print(f"Ár: {elemdata.price:,} EUR")
```

### Dictionary formátum:

```python
data_dict = elemdata.to_dict()
for key, value in data_dict.items():
    print(f"{key}: {value}")
```

## Integráció a meglévő kódba

A parser integrálva van a `background.py` fájlba:

1. **get_api_data()** függvény most ELEMDATA objektumot ad vissza
2. **check_url()** függvény a parse-olt adatokat tárolja
3. **CSV mentés/beolvasás** támogatja az új formátumot

## Tesztelés

A parser tesztelhető a következő módokon:

```bash
# Teljes teszt futtatása
python background.py

# Csak a parser példa
python parser_example.py
```

## Példa Kimenetek

### Egyszerű szöveg:
```
Input: "Volkswagen Golf 2.0 TDI"",""isTaxDeductible"
Output: ELEMDATA(title='Volkswagen Golf 2.0 TDI', isTaxDeductible=True)
```

### Teljes JSON:
```
Input: {"title": "BMW X5", "price": 45000, "year": 2020}
Output: ELEMDATA(title='BMW X5', price=45000, year=2020, ...)
```

## Hibakezelés

A parser robusztus hibakezeléssel rendelkezik:
- JSON parse hibák esetén regex-szel próbálja kinyerni az adatokat
- Érvénytelen bemenet esetén üres ELEMDATA objektumot ad vissza
- Minden eredeti szöveg megmarad a `raw_data` mezőben

## Fájlok

- `background.py` - Fő parser implementáció
- `parser_example.py` - Használati példák
- `PARSER_README.md` - Ez a dokumentáció
