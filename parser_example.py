#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ELEMDATA Parser Használati Példa

Ez a fájl demonstrálja, hogyan használható a parse_elempar_json függvény
és az ELEMDATA osztály az elempar szövegek feldolgozására.
"""

from background import ELEMDATA, parse_elempar_json


def main():
    print("=== ELEMDATA Parser Használati Példa ===\n")
    
    # Példa 1: Egyszerű szöveg idézőjelekkel
    print("1. Egyszerű szöveg feldolgozása:")
    text1 = '"Volkswagen Golf 2.0 TDI"",""isTaxDeductible"'
    elemdata1 = parse_elempar_json(text1)
    print(f"   Input: {text1}")
    print(f"   Cím: {elemdata1.title}")
    print(f"   Adólevonható: {elemdata1.isTaxDeductible}")
    print()
    
    # Példa 2: Teljes JSON objektum
    print("2. Teljes JSON objektum feldolgozása:")
    json_text = '''{"title": "BMW 320d xDrive", "price": 35000, "year": 2021, 
                   "mileage": 30000, "fuelType": "Diesel", "transmission": "Automatic", 
                   "power": 190, "color": "White", "brand": "BMW", "model": "320d", 
                   "isTaxDeductible": true}'''
    elemdata2 = parse_elempar_json(json_text)
    print(f"   Input: {json_text[:50]}...")
    print(f"   Cím: {elemdata2.title}")
    print(f"   Ár: {elemdata2.price:,} EUR")
    print(f"   Év: {elemdata2.year}")
    print(f"   Kilométer: {elemdata2.mileage:,} km")
    print(f"   Üzemanyag: {elemdata2.fuel_type}")
    print(f"   Váltó: {elemdata2.transmission}")
    print(f"   Teljesítmény: {elemdata2.power} LE")
    print(f"   Szín: {elemdata2.color}")
    print(f"   Márka: {elemdata2.brand}")
    print(f"   Modell: {elemdata2.model}")
    print(f"   Adólevonható: {'Igen' if elemdata2.isTaxDeductible else 'Nem'}")
    print()
    
    # Példa 3: Dictionary formátum
    print("3. Dictionary formátumba konvertálás:")
    data_dict = elemdata2.to_dict()
    print("   Dictionary tartalom:")
    for key, value in data_dict.items():
        if key != 'raw_data':  # raw_data kihagyása
            print(f"     {key}: {value}")
    print()
    
    # Példa 4: Hiba kezelés
    print("4. Hiba kezelés:")
    invalid_text = "Ez nem egy érvényes JSON vagy elempar szöveg"
    elemdata3 = parse_elempar_json(invalid_text)
    print(f"   Input: {invalid_text}")
    print(f"   Eredmény: {elemdata3}")
    print(f"   Raw data: {elemdata3.raw_data}")
    print()
    
    print("=== Példa befejezve ===")


if __name__ == '__main__':
    main()
