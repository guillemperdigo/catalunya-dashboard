#!/usr/bin/env python3
"""
Script per generar dades mock de preus bursàtils
Usa random walk suau per simular moviments realistes de preus
"""

import json
import os
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict


def generate_random_walk(days: int, start_price: float = 100.0, volatility: float = 0.02) -> List[float]:
    """Genera una sèrie de preus amb random walk"""
    prices = [start_price]
    
    for _ in range(days - 1):
        # Random walk amb drift lleu cap amunt (mercat alcista suau)
        drift = 0.0002  # ~0.02% diari
        shock = random.gauss(0, volatility)
        
        # Nou preu basat en l'anterior
        new_price = prices[-1] * (1 + drift + shock)
        
        # Evitar preus negatius
        new_price = max(new_price, 1.0)
        prices.append(new_price)
    
    return prices


def generate_volume_series(days: int, base_volume: int = 100000) -> List[int]:
    """Genera volums amb estacionalitat lleu"""
    volumes = []
    
    for i in range(days):
        # Estacionalitat setmanal (menys volum caps de setmana)
        day_of_week = i % 7
        if day_of_week in [5, 6]:  # Dissabte, diumenge (menys volum)
            seasonal_factor = 0.3
        else:
            seasonal_factor = 1.0
        
        # Variació aleatòria
        random_factor = random.uniform(0.5, 1.8)
        
        volume = int(base_volume * seasonal_factor * random_factor)
        volumes.append(volume)
    
    return volumes


def generate_ohlc_from_close(close_prices: List[float]) -> List[Dict]:
    """Genera Open, High, Low des dels preus de tancament"""
    ohlc_data = []
    
    for i, close in enumerate(close_prices):
        # Open: preu anterior + soroll petit
        if i == 0:
            open_price = close * random.uniform(0.995, 1.005)
        else:
            open_price = close_prices[i-1] * random.uniform(0.998, 1.002)
        
        # High i Low basats en volatilitat intradiària
        intraday_volatility = 0.015  # 1.5% volatilitat intradiària
        high = max(open_price, close) * random.uniform(1.001, 1 + intraday_volatility)
        low = min(open_price, close) * random.uniform(1 - intraday_volatility, 0.999)
        
        # Assegurar coherència: Low <= Open,Close <= High
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        ohlc_data.append({
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2)
        })
    
    return ohlc_data


def generate_dates(days: int, start_date: str = None) -> List[str]:
    """Genera llista de dates (només dies laborables)"""
    if start_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=int(days * 1.4))  # Buffer per caps de setmana
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=int(days * 1.4))
    
    dates = []
    current_date = start_date
    
    while len(dates) < days and current_date <= end_date:
        # Només dies laborables (dilluns=0, diumenge=6)
        if current_date.weekday() < 5:  # 0-4 són dilluns-divendres
            dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return dates[:days]


def generate_company_data(ticker: str, days: int = 260) -> List[Dict]:
    """Genera dades completes per una empresa"""
    
    # Preus inicials diferents per empresa (simulant diferents nivells de preu)
    start_prices = {
        'CABK.MC': 4.2,
        'GRF.MC': 15.8,
        'CLNX.MC': 45.3,
        'FDR.MC': 18.9,
        'COL.MC': 7.6,
        'ALM.MC': 12.4
    }
    
    start_price = start_prices.get(ticker, 25.0)
    
    # Volatilitats diferents per sector
    volatilities = {
        'CABK.MC': 0.025,  # Banks: volatilitat mitjana
        'GRF.MC': 0.035,   # Healthcare: més volàtil
        'CLNX.MC': 0.030,  # Telecom: volatilitat mitjana-alta
        'FDR.MC': 0.028,   # Industrials: volatilitat mitjana
        'COL.MC': 0.032,   # Real Estate: volàtil
        'ALM.MC': 0.033    # Pharma: volàtil
    }
    
    volatility = volatilities.get(ticker, 0.025)
    
    # Generar sèries
    dates = generate_dates(days)
    close_prices = generate_random_walk(days, start_price, volatility)
    ohlc_data = generate_ohlc_from_close(close_prices)
    volumes = generate_volume_series(days, base_volume=random.randint(50000, 500000))
    
    # Combinar tot
    price_data = []
    for i, date in enumerate(dates):
        price_data.append({
            'date': date,
            'open': ohlc_data[i]['open'],
            'high': ohlc_data[i]['high'],
            'low': ohlc_data[i]['low'],
            'close': ohlc_data[i]['close'],
            'volume': volumes[i]
        })
    
    return price_data


def main():
    """Genera fixtures per totes les empreses"""
    
    # Llegir llista d'empreses
    companies_path = os.path.join('data', 'companies.json')
    if not os.path.exists(companies_path):
        print(f"Error: {companies_path} no existeix")
        return
    
    with open(companies_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)
    
    # Crear directori de preus si no existeix
    prices_dir = os.path.join('data', 'prices')
    os.makedirs(prices_dir, exist_ok=True)
    
    print(f"Generant dades mock per {len(companies)} empreses...")
    
    for company in companies:
        ticker = company['ticker']
        print(f"  Generant {ticker}...")
        
        # Generar dades
        price_data = generate_company_data(ticker)
        
        # Guardar a fitxer
        output_path = os.path.join(prices_dir, f"{ticker}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(price_data, f, indent=2, ensure_ascii=False)
        
        print(f"    ✓ {len(price_data)} punts de dades guardats a {output_path}")
    
    print("\n🎉 Generació de dades mock completada!")


if __name__ == '__main__':
    main()
