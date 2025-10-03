"""
Servei per obtenir dades reals de mercats bursàtils via yfinance (Yahoo Finance)
Inclou sistema de cache per minimitzar requests a l'API
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from pathlib import Path


class StockDataService:
    """Gestor de dades bursàtils reals amb cache"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache en memòria per rendiment
        self._memory_cache = {}
        
        # Temps de vida del cache (en minuts)
        self.cache_ttl = {
            "company_info": 1440,  # 24 hores
            "price_data": 60,      # 1 hora per dades històriques
            "realtime": 5          # 5 minuts per dades en temps real
        }
    
    def _get_cache_path(self, ticker: str, data_type: str) -> Path:
        """Genera path per fitxer de cache"""
        return self.cache_dir / f"{ticker}_{data_type}.json"
    
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
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Obté informació bàsica de l'empresa
        Cache: 24 hores
        """
        cache_path = self._get_cache_path(ticker, "info")
        
        # Comprovar cache
        if self._is_cache_valid(cache_path, self.cache_ttl["company_info"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Obtenir dades de Yahoo Finance
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extreure camps rellevants
            company_data = {
                "ticker": ticker,
                "name": info.get("longName", info.get("shortName", ticker)),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap"),
                "currency": info.get("currency", "EUR"),
                "exchange": info.get("exchange", "Unknown"),
                "website": info.get("website"),
                "description": info.get("longBusinessSummary"),
                "updated_at": datetime.now().isoformat()
            }
            
            # Guardar al cache
            self._write_cache(cache_path, company_data)
            
            return company_data
            
        except Exception as e:
            print(f"Error obtenint info de {ticker}: {e}")
            return None
    
    def get_historical_data(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Obté dades històriques de preus
        
        Args:
            ticker: Símbol de l'empresa (ex: "CABK.MC")
            period: Període de temps (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Interval de dades (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            Llista de diccionaris amb dades OHLCV
        """
        cache_key = f"{ticker}_{period}_{interval}"
        cache_path = self._get_cache_path(cache_key, "prices")
        
        # Comprovar cache
        if self._is_cache_valid(cache_path, self.cache_ttl["price_data"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Obtenir dades de Yahoo Finance
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                print(f"No s'han trobat dades per {ticker}")
                return None
            
            # Convertir a format dict
            price_data = []
            for date, row in hist.iterrows():
                price_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            # Guardar al cache
            self._write_cache(cache_path, price_data)
            
            return price_data
            
        except Exception as e:
            print(f"Error obtenint dades de {ticker}: {e}")
            return None
    
    def get_current_price(self, ticker: str) -> Optional[Dict]:
        """
        Obté preu actual i dades del dia
        Cache: 5 minuts
        """
        cache_path = self._get_cache_path(ticker, "realtime")
        
        # Comprovar cache
        if self._is_cache_valid(cache_path, self.cache_ttl["realtime"]):
            cached_data = self._read_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Obtenir dades del dia (més ràpid que info completa)
        try:
            stock = yf.Ticker(ticker)
            
            # Obtenir últim dia de dades
            hist = stock.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            previous_close = stock.info.get("previousClose", latest["Close"])
            
            current_data = {
                "ticker": ticker,
                "current_price": float(latest["Close"]),
                "open": float(latest["Open"]),
                "high": float(hist["High"].max()),
                "low": float(hist["Low"].min()),
                "volume": int(hist["Volume"].sum()),
                "previous_close": float(previous_close),
                "change": float(latest["Close"] - previous_close),
                "change_percent": float((latest["Close"] - previous_close) / previous_close * 100),
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar al cache
            self._write_cache(cache_path, current_data)
            
            return current_data
            
        except Exception as e:
            print(f"Error obtenint preu actual de {ticker}: {e}")
            return None
    
    def clear_cache(self, ticker: Optional[str] = None):
        """Neteja el cache (tot o només un ticker)"""
        if ticker:
            # Netejar cache d'un ticker específic
            for cache_file in self.cache_dir.glob(f"{ticker}_*.json"):
                cache_file.unlink()
                print(f"Cache eliminat: {cache_file}")
        else:
            # Netejar tot el cache
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            print("Tot el cache ha estat eliminat")
    
    def get_multiple_tickers(self, tickers: List[str], period: str = "1y") -> Dict[str, List[Dict]]:
        """
        Obté dades per múltiples tickers de cop
        Més eficient per actualitzacions massives
        """
        results = {}
        
        for ticker in tickers:
            data = self.get_historical_data(ticker, period=period)
            if data:
                results[ticker] = data
            else:
                print(f"No s'han pogut obtenir dades per {ticker}")
        
        return results


# Instància global del servei
stock_service = StockDataService()

