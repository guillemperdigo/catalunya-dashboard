import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.models import Company, PriceData, CompanyKPI

# Placeholder per futures BD connections
# De moment treballa amb fixtures JSON

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._companies_cache = None
        self._prices_cache = {}
    
    def get_companies(self) -> List[Company]:
        """Carrega llista d'empreses des del JSON"""
        if self._companies_cache is None:
            companies_path = os.path.join(self.data_dir, "companies.json")
            with open(companies_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._companies_cache = [Company(**company) for company in data]
        return self._companies_cache
    
    def get_price_data(self, ticker: str) -> List[PriceData]:
        """Carrega dades de preus per un ticker"""
        if ticker not in self._prices_cache:
            prices_path = os.path.join(self.data_dir, "prices", f"{ticker}.json")
            if not os.path.exists(prices_path):
                return []
            
            with open(prices_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._prices_cache[ticker] = [PriceData(**price) for price in data]
        
        return self._prices_cache[ticker]
    
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


# Instància global
db = DataManager()
