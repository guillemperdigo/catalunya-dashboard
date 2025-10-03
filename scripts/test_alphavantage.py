#!/usr/bin/env python3
"""
Script de prova per verificar la integració amb Alpha Vantage
"""

import sys
import os

# Afegir directori arrel al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carregar variables d'entorn
from dotenv import load_dotenv
load_dotenv()

from app.services.alphavantage_data import AlphaVantageService


def test_alphavantage():
    """Prova la connexió amb Alpha Vantage"""
    
    print("=" * 60)
    print("🧪 TEST: Integració amb Alpha Vantage")
    print("=" * 60)
    print()
    
    # Comprovar API key
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ API key d'Alpha Vantage no configurada")
        print()
        print("Per configurar:")
        print("1. Obté una clau gratuïta a: https://www.alphavantage.co/support/#api-key")
        print("2. Crea un fitxer .env amb:")
        print("   ALPHAVANTAGE_API_KEY=la_teva_clau")
        print()
        return
    
    print(f"✅ API key configurada: {api_key[:8]}...")
    print()
    
    # Crear servei
    service = AlphaVantageService(api_key)
    
    # Provar amb diferents tickers
    test_tickers = [
        ("AAPL", "Apple (US)"),
        ("SAN.MAD", "Banco Santander (Espanya)"),
        ("CABK.MAD", "CaixaBank (Espanya)"),
        ("MSFT", "Microsoft (US)")
    ]
    
    print("🔍 Provant cotitzacions actuals...\n")
    
    for ticker, name in test_tickers:
        print(f"📊 {name} ({ticker}):")
        
        # Obtenir cotització
        quote = service.get_quote(ticker)
        
        if quote:
            print(f"   ✅ Preu actual: ${quote['current_price']:.2f}")
            print(f"      Canvi: {quote['change']:+.2f} ({quote['change_percent']}%)")
            print(f"      Volum: {quote['volume']:,}")
            print()
            
            # Obtenir dades històriques (només per el primer que funcioni)
            if ticker == "AAPL":
                print(f"   Obtenint històric (1 mes)...")
                history = service.get_historical_data(ticker, period="1mo")
                if history:
                    print(f"   ✅ {len(history)} dies de dades")
                    print(f"      Primer: {history[0]['date']}")
                    print(f"      Últim: {history[-1]['date']}")
                    print()
                else:
                    print(f"   ❌ No s'han pogut obtenir dades històriques")
                    print()
        else:
            print(f"   ❌ No s'ha pogut obtenir cotització")
            print()
    
    print("=" * 60)
    print("✅ TEST COMPLETAT!")
    print("=" * 60)
    print()
    print("💡 Si alguna empresa espanyola no funciona, pot ser que")
    print("   Alpha Vantage no tingui cobertura d'aquest mercat.")
    print("   Les empreses US (AAPL, MSFT, etc.) funcionen sempre.")
    print()


if __name__ == "__main__":
    test_alphavantage()

