import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.models import Company, PriceData, CompanyKPI

# Intentar importar serveis de dades reals
try:
    from app.services.stock_data import stock_service
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    stock_service = None

try:
    from app.services.alphavantage_data import get_alphavantage_service
    ALPHAVANTAGE_AVAILABLE = True
except ImportError:
    ALPHAVANTAGE_AVAILABLE = False
    get_alphavantage_service = None

# Determinar si tenim alguna font de dades reals
REAL_DATA_AVAILABLE = YFINANCE_AVAILABLE or ALPHAVANTAGE_AVAILABLE

if not REAL_DATA_AVAILABLE:
    print("⚠️  Cap servei de dades reals disponible. Usant dades mock.")


class DataManager:
    def __init__(self, data_dir: str = "data", use_real_data: bool = True):
        self.data_dir = data_dir
        self._companies_cache = None
        self._prices_cache = {}
        
        # Activar dades reals si està disponible i activat
        self.use_real_data = use_real_data and REAL_DATA_AVAILABLE
        
        # Obtenir servei d'Alpha Vantage si està disponible
        self.alphavantage_service = None
        if ALPHAVANTAGE_AVAILABLE and get_alphavantage_service:
            self.alphavantage_service = get_alphavantage_service()
        
        # Mostrar estat
        if self.use_real_data:
            sources = []
            if YFINANCE_AVAILABLE:
                sources.append("Yahoo Finance")
            if self.alphavantage_service:
                sources.append("Alpha Vantage")
            print(f"✅ Serveis de dades reals activats: {', '.join(sources)}")
        else:
            print("📊 Usant dades mock des de fitxers JSON")
    
    def get_companies(self) -> List[Company]:
        """Carrega llista d'empreses des del JSON"""
        if self._companies_cache is None:
            companies_path = os.path.join(self.data_dir, "companies.json")
            with open(companies_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._companies_cache = [Company(**company) for company in data]
        return self._companies_cache
    
    def get_price_data(self, ticker: str, force_mock: bool = False) -> List[PriceData]:
        """
        Carrega dades de preus per un ticker
        Intenta múltiples fonts: Yahoo Finance -> Alpha Vantage -> Mock
        """
        # Si ja està en cache, retornar-lo
        cache_key = f"{ticker}_{'real' if self.use_real_data and not force_mock else 'mock'}"
        if cache_key in self._prices_cache:
            return self._prices_cache[cache_key]
        
        prices = []
        
        # Intentar obtenir dades reals
        if self.use_real_data and not force_mock:
            # 1. Intentar amb Yahoo Finance (yfinance)
            if YFINANCE_AVAILABLE and stock_service:
                try:
                    real_data = stock_service.get_historical_data(ticker, period="1y")
                    if real_data:
                        prices = [PriceData(**price) for price in real_data]
                        print(f"✅ Dades obtingudes de Yahoo Finance per {ticker}")
                except Exception as e:
                    print(f"⚠️  Yahoo Finance error per {ticker}: {str(e)[:50]}")
            
            # 2. Si Yahoo Finance ha fallat, intentar amb Alpha Vantage
            if not prices and self.alphavantage_service:
                try:
                    real_data = self.alphavantage_service.get_historical_data(ticker, period="1y")
                    if real_data:
                        prices = [PriceData(**price) for price in real_data]
                        print(f"✅ Dades obtingudes d'Alpha Vantage per {ticker}")
                except Exception as e:
                    print(f"⚠️  Alpha Vantage error per {ticker}: {str(e)[:50]}")
        
        # 3. Fallback a dades mock si no s'han obtingut dades reals
        if not prices:
            prices_path = os.path.join(self.data_dir, "prices", f"{ticker}.json")
            if os.path.exists(prices_path):
                with open(prices_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    prices = [PriceData(**price) for price in data]
                    print(f"📊 Usant dades mock per {ticker}")
        
        # Guardar al cache
        if prices:
            self._prices_cache[cache_key] = prices
        
        return prices
    
    def get_company_kpis(self) -> List[CompanyKPI]:
        """Calcula KPIs per totes les empreses"""
        companies = self.get_companies()
        kpis = []
        
        for company in companies:
            prices = self.get_price_data(company.ticker)
            if not prices:
                continue
                
            # Ordenar per data (més recent primer)
            prices.sort(key=lambda x: x.date, reverse=True)
            
            latest = prices[0]
            previous = prices[1] if len(prices) > 1 else latest
            
            # Calcular màxim/mínim 52 setmanes
            high_52w = max(p.high for p in prices[:252] if p.high)  # ~252 dies bursàtils/any
            low_52w = min(p.low for p in prices[:252] if p.low)
            
            # Mock market cap (preu * shares fictícies)
            mkt_cap = latest.close * 1000000  # Mock: 1M shares
            
            # Variació percentual
            chng_1d_pct = ((latest.close - previous.close) / previous.close) * 100 if previous.close > 0 else 0
            
            kpi = CompanyKPI(
                name=company.name,
                ticker=company.ticker,
                exchange=company.exchange,
                sector=company.sector,
                hq_province=company.hq_province,
                last_price=latest.close,
                chng_1d_pct=chng_1d_pct,
                high_52w=high_52w,
                low_52w=low_52w,
                mkt_cap=mkt_cap
            )
            kpis.append(kpi)
        
        return kpis
    
    def get_company_by_ticker(self, ticker: str) -> Optional[Company]:
        """Troba empresa per ticker"""
        companies = self.get_companies()
        return next((c for c in companies if c.ticker == ticker), None)
    
    def get_series_data(self, ticker: str, range_param: str = "1Y") -> List[PriceData]:
        """Obté sèries de preus per un rang específic"""
        # Mapejar range_param al format de yfinance/alphavantage
        period_map = {
            "1M": "1mo",
            "3M": "3mo",
            "1Y": "1y"
        }
        
        # Si usem dades reals, obtenir directament el període correcte
        if self.use_real_data:
            period = period_map.get(range_param, "1y")
            
            # Intentar amb Yahoo Finance
            if YFINANCE_AVAILABLE and stock_service:
                try:
                    real_data = stock_service.get_historical_data(ticker, period=period)
                    if real_data:
                        return [PriceData(**price) for price in real_data]
                except Exception as e:
                    print(f"⚠️  Yahoo Finance error sèrie {ticker}: {str(e)[:50]}")
            
            # Intentar amb Alpha Vantage
            if self.alphavantage_service:
                try:
                    real_data = self.alphavantage_service.get_historical_data(ticker, period=period)
                    if real_data:
                        return [PriceData(**price) for price in real_data]
                except Exception as e:
                    print(f"⚠️  Alpha Vantage error sèrie {ticker}: {str(e)[:50]}")
        
        # Fallback: obtenir totes les dades i filtrar
        prices = self.get_price_data(ticker)
        if not prices:
            return []
        
        # Ordenar per data
        prices.sort(key=lambda x: x.date)
        
        # Filtrar per rang
        if range_param == "1M":
            cutoff_days = 30
        elif range_param == "3M":
            cutoff_days = 90
        else:  # 1Y
            cutoff_days = 365
        
        cutoff_date = (datetime.now() - timedelta(days=cutoff_days)).strftime('%Y-%m-%d')
        filtered_prices = [p for p in prices if p.date >= cutoff_date]
        
        return filtered_prices
    
    def clear_cache(self):
        """Neteja cache en memòria"""
        self._prices_cache = {}
        self._companies_cache = None
        print("🗑️  Cache netejat")
    
    def refresh_data(self, ticker: Optional[str] = None):
        """
        Refresca dades (neteja cache i força re-descàrrega)
        """
        if self.use_real_data:
            # Netejar cache de Yahoo Finance
            if YFINANCE_AVAILABLE and stock_service:
                stock_service.clear_cache(ticker)
            
            # Netejar cache d'Alpha Vantage
            if self.alphavantage_service:
                self.alphavantage_service.clear_cache(ticker)
        
        if ticker:
            # Netejar cache d'un ticker específic
            keys_to_remove = [k for k in self._prices_cache.keys() if k.startswith(ticker)]
            for key in keys_to_remove:
                del self._prices_cache[key]
            print(f"🔄 Dades de {ticker} refrescades")
        else:
            # Netejar tot el cache
            self.clear_cache()
            print("🔄 Totes les dades refrescades")


# Instància global
db = DataManager()
