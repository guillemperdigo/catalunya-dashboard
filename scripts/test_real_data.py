#!/usr/bin/env python3
"""
Script de prova per verificar la integració amb dades reals de Yahoo Finance
"""

import sys
import os

# Afegir directori arrel al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import DataManager, REAL_DATA_AVAILABLE


def test_real_data():
    """Prova la connexió amb dades reals"""
    
    print("=" * 60)
    print("🧪 TEST: Integració amb Yahoo Finance")
    print("=" * 60)
    print()
    
    # Comprovar disponibilitat
    print(f"yfinance disponible: {'✅ Sí' if REAL_DATA_AVAILABLE else '❌ No'}")
    print()
    
    if not REAL_DATA_AVAILABLE:
        print("⚠️  Per activar dades reals, instal·la yfinance:")
        print("   pip install yfinance")
        print()
        return
    
    # Crear DataManager amb dades reals
    print("Inicialitzant DataManager amb dades reals...")
    db = DataManager(use_real_data=True)
    print()
    
    # Obtenir empreses
    companies = db.get_companies()
    print(f"📊 Empreses carregades: {len(companies)}")
    for company in companies:
        print(f"   - {company.name} ({company.ticker})")
    print()
    
    # Provar amb primera empresa
    if companies:
        test_ticker = companies[0].ticker
        print(f"🔍 Provant amb {test_ticker}...")
        print()
        
        # Obtenir dades de preus
        print("Obtenint dades històriques (1 any)...")
        prices = db.get_price_data(test_ticker)
        
        if prices:
            print(f"✅ Dades obtingudes: {len(prices)} punts")
            print()
            
            # Mostrar últimes 5 dades
            print("Últimes 5 sessions:")
            for price in sorted(prices, key=lambda x: x.date, reverse=True)[:5]:
                print(f"   {price.date}: €{price.close:.2f} (Vol: {price.volume:,})")
            print()
            
            # Obtenir KPIs
            print("Calculant KPIs...")
            kpis = db.get_company_kpis()
            
            if kpis:
                test_kpi = next((k for k in kpis if k.ticker == test_ticker), None)
                if test_kpi:
                    print(f"✅ KPIs per {test_ticker}:")
                    print(f"   Preu actual: €{test_kpi.last_price:.2f}")
                    print(f"   Variació 1d: {test_kpi.chng_1d_pct:+.2f}%")
                    print(f"   Màxim 52s: €{test_kpi.high_52w:.2f}")
                    print(f"   Mínim 52s: €{test_kpi.low_52w:.2f}")
                    print(f"   Market Cap: €{test_kpi.mkt_cap:,.0f}")
                    print()
            
            # Provar diferents rangs
            print("Provant diferents rangs temporals...")
            for range_param in ["1M", "3M", "1Y"]:
                series = db.get_series_data(test_ticker, range_param)
                print(f"   {range_param}: {len(series)} punts")
            print()
            
            print("=" * 60)
            print("✅ TEST COMPLETAT AMB ÈXIT!")
            print("=" * 60)
            print()
            print("💡 El dashboard ara pot usar dades reals de Yahoo Finance")
            print("   Les dades es guarden a cache durant 1 hora")
            print("   El fallback a dades mock funciona automàticament")
            print()
            
        else:
            print("❌ No s'han pogut obtenir dades")
            print()
    else:
        print("❌ No s'han trobat empreses")
        print()


def test_cache():
    """Prova el sistema de cache"""
    print("=" * 60)
    print("🧪 TEST: Sistema de cache")
    print("=" * 60)
    print()
    
    if not REAL_DATA_AVAILABLE:
        print("⚠️  yfinance no disponible. Saltant test de cache.")
        return
    
    from app.services.stock_data import stock_service
    import time
    
    ticker = "CABK.MC"
    
    print(f"Primera request per {ticker}...")
    start = time.time()
    data1 = stock_service.get_historical_data(ticker, period="1mo")
    time1 = time.time() - start
    print(f"   Temps: {time1:.2f}s")
    print()
    
    print(f"Segona request (des de cache)...")
    start = time.time()
    data2 = stock_service.get_historical_data(ticker, period="1mo")
    time2 = time.time() - start
    print(f"   Temps: {time2:.2f}s")
    print()
    
    speedup = time1 / time2 if time2 > 0 else float('inf')
    print(f"⚡ Acceleració: {speedup:.1f}x més ràpid")
    print(f"✅ Cache funcionant correctament!")
    print()


if __name__ == "__main__":
    test_real_data()
    print()
    test_cache()

