"""
Servei per obtenir dades reals de mercats bursàtils via Alpha Vantage
API més fiable que Yahoo Finance amb 500 requests/dia gratuïts
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from pathlib import Path
import time


class AlphaVantageService:
    """Gestor de dades bursàtils d'Alpha Vantage amb cache"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "data/cache/alphavantage"):
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache en memòria
        self._memory_cache = {}
        
        # Temps de vida del cache (en minuts)
        self.cache_ttl = {
            "company_info": 1440,  # 24 hores
            "price_data": 60,      # 1 hora
            "intraday": 5          # 5 minuts
        }
        
        # Rate limiting (5 requests per minut per API gratuïta)
        self.last_request_time = 0
        self.min_request_interval = 12  # segons (5 req/min = 12s entre requests)
    
    def _wait_for_rate_limit(self):
        """Espera si cal per no excedir el rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            print(f"⏳ Esperant {wait_time:.1f}s per rate limit...")
            time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Genera path per fitxer de cache"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_path: Path, ttl_minutes: int) -> bool:
        """Comprova si el cache és vàlid segons TTL"""
        if not cache_path.exists():
            return False
        
        modified_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - modified_time
        
        return age < timedelta(minutes=ttl_minutes)
    
    def _read_cache(self, cache_path: Path) -> Optional[Dict]:
        """Llegeix dades del cache"""
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error llegint cache {cache_path}: {e}")
            return None
    
    def _write_cache(self, cache_path: Path, data: Dict):
        """Escriu dades al cache"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error escrivint cache {cache_path}: {e}")
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Fa una petició a l'API d'Alpha Vantage"""
        if not self.api_key:
            print("❌ API key d'Alpha Vantage no configurada")
            return None
        
        # Afegir API key
        params['apikey'] = self.api_key
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Comprovar errors de l'API
            if "Error Message" in data:
                print(f"❌ Alpha Vantage error: {data['Error Message']}")
                return None
            
            if "Note" in data:
                print(f"⚠️  Alpha Vantage note: {data['Note']}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de connexió amb Alpha Vantage: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsejar resposta d'Alpha Vantage: {e}")
            return None
    
    def _convert_ticker_format(self, ticker: str) -> str:
        """
        Converteix ticker del format Yahoo (.MC) al format Alpha Vantage
        Alpha Vantage usa format diferent per mercats internacionals
        """
        # Empreses espanyoles: eliminar .MC i provar directament
        if ticker.endswith('.MC'):
            base_ticker = ticker.replace('.MC', '')
            # Alguns tickers poden necessitar el sufix del mercat
            return f"{base_ticker}.MAD"  # MAD = Madrid Stock Exchange
        return ticker
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Obté informació de l'empresa (OVERVIEW)
        Cache: 24 hores
        """
        av_ticker = self._convert_ticker_format(ticker)
        cache_key = f"info_{av_ticker.replace('.', '_')}"
        cache_path = self._get_cache_path(cache_key)
        
        # Comprovar cache
        if self._is_cache_valid(cache_path, self.cache_ttl["company_info"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Obtenir dades d'Alpha Vantage
        params = {
            'function': 'OVERVIEW',
            'symbol': av_ticker
        }
        
        data = self._make_request(params)
        if not data or 'Symbol' not in data:
            return None
        
        # Extreure camps rellevants
        company_data = {
            "ticker": ticker,
            "av_ticker": av_ticker,
            "name": data.get("Name", ticker),
            "sector": data.get("Sector", "Unknown"),
            "industry": data.get("Industry", "Unknown"),
            "market_cap": float(data.get("MarketCapitalization", 0)) if data.get("MarketCapitalization") else None,
            "currency": data.get("Currency", "USD"),
            "exchange": data.get("Exchange", "Unknown"),
            "description": data.get("Description"),
            "pe_ratio": float(data.get("PERatio", 0)) if data.get("PERatio") else None,
            "dividend_yield": float(data.get("DividendYield", 0)) if data.get("DividendYield") else None,
            "updated_at": datetime.now().isoformat()
        }
        
        # Guardar al cache
        self._write_cache(cache_path, company_data)
        
        return company_data
    
    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1y",
        outputsize: str = "compact"  # compact=100 punts, full=20+ anys
    ) -> Optional[List[Dict]]:
        """
        Obté dades històriques diàries (TIME_SERIES_DAILY)
        
        Args:
            ticker: Símbol de l'empresa
            period: Període (1mo, 3mo, 6mo, 1y) - filtrat localment
            outputsize: 'compact' (100 punts) o 'full' (tot l'històric)
        
        Returns:
            Llista de diccionaris amb dades OHLCV
        """
        av_ticker = self._convert_ticker_format(ticker)
        cache_key = f"daily_{av_ticker.replace('.', '_')}_{outputsize}"
        cache_path = self._get_cache_path(cache_key)
        
        # Comprovar cache
        if self._is_cache_valid(cache_path, self.cache_ttl["price_data"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return self._filter_by_period(cached_data, period)
        
        # Obtenir dades d'Alpha Vantage
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': av_ticker,
            'outputsize': outputsize
        }
        
        data = self._make_request(params)
        if not data or 'Time Series (Daily)' not in data:
            print(f"❌ No s'han trobat dades diàries per {av_ticker}")
            return None
        
        # Convertir a format consistent
        time_series = data['Time Series (Daily)']
        price_data = []
        
        for date_str, values in sorted(time_series.items()):
            price_data.append({
                "date": date_str,
                "open": float(values['1. open']),
                "high": float(values['2. high']),
                "low": float(values['3. low']),
                "close": float(values['4. close']),
                "volume": int(values['5. volume'])
            })
        
        # Guardar al cache
        self._write_cache(cache_path, price_data)
        
        # Filtrar per període
        return self._filter_by_period(price_data, period)
    
    def _filter_by_period(self, price_data: List[Dict], period: str) -> List[Dict]:
        """Filtra dades de preus per període"""
        if not price_data:
            return []
        
        # Calcular data de tall
        period_map = {
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365,
            "2y": 730,
            "5y": 1825
        }
        
        days = period_map.get(period, 365)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        return [p for p in price_data if p['date'] >= cutoff_date]
    
    def get_quote(self, ticker: str) -> Optional[Dict]:
        """
        Obté cotització actual (GLOBAL_QUOTE)
        Cache: 5 minuts
        """
        av_ticker = self._convert_ticker_format(ticker)
        cache_key = f"quote_{av_ticker.replace('.', '_')}"
        cache_path = self._get_cache_path(cache_key)
        
        # Comprovar cache
        if self._is_cache_valid(cache_path, self.cache_ttl["intraday"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Obtenir cotització
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': av_ticker
        }
        
        data = self._make_request(params)
        if not data or 'Global Quote' not in data:
            return None
        
        quote = data['Global Quote']
        if not quote:
            return None
        
        current_data = {
            "ticker": ticker,
            "av_ticker": av_ticker,
            "current_price": float(quote.get('05. price', 0)),
            "open": float(quote.get('02. open', 0)),
            "high": float(quote.get('03. high', 0)),
            "low": float(quote.get('04. low', 0)),
            "volume": int(quote.get('06. volume', 0)),
            "previous_close": float(quote.get('08. previous close', 0)),
            "change": float(quote.get('09. change', 0)),
            "change_percent": quote.get('10. change percent', '0%').rstrip('%'),
            "timestamp": datetime.now().isoformat()
        }
        
        # Guardar al cache
        self._write_cache(cache_path, current_data)
        
        return current_data
    
    def clear_cache(self, ticker: Optional[str] = None):
        """Neteja el cache"""
        if ticker:
            av_ticker = self._convert_ticker_format(ticker)
            safe_ticker = av_ticker.replace('.', '_')
            for cache_file in self.cache_dir.glob(f"*{safe_ticker}*.json"):
                cache_file.unlink()
                print(f"🗑️  Cache eliminat: {cache_file.name}")
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            print("🗑️  Tot el cache d'Alpha Vantage eliminat")


# Instància global (es crearà quan sigui necessari)
_alphavantage_service = None


def get_alphavantage_service() -> Optional[AlphaVantageService]:
    """Obté la instància global del servei d'Alpha Vantage"""
    global _alphavantage_service
    
    if _alphavantage_service is None:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if api_key:
            _alphavantage_service = AlphaVantageService(api_key)
        else:
            return None
    
    return _alphavantage_service

