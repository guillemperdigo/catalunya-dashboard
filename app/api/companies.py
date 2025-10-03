from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models import CompanyKPI, SeriesResponse, CompanyDetail, PriceData
from app.db import db, REAL_DATA_AVAILABLE

router = APIRouter(prefix="/api", tags=["companies"])


@router.get("/companies", response_model=List[CompanyKPI])
async def get_companies():
    """Retorna llista d'empreses amb KPIs calculats"""
    try:
        companies = db.get_company_kpis()
        return companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error carregant empreses: {str(e)}")


@router.get("/companies/{ticker}", response_model=CompanyDetail)
async def get_company_detail(ticker: str):
    """Retorna detalls d'una empresa específica"""
    try:
        # Buscar empresa
        company = db.get_company_by_ticker(ticker)
        if not company:
            raise HTTPException(status_code=404, detail=f"Empresa {ticker} no trobada")
        
        # Calcular KPIs
        kpis = db.get_company_kpis()
        company_kpi = next((kpi for kpi in kpis if kpi.ticker == ticker), None)
        
        if not company_kpi:
            raise HTTPException(status_code=404, detail=f"Dades KPI per {ticker} no trobades")
        
        # Obtenir últimes dades de preus
        prices = db.get_price_data(ticker)
        if not prices:
            raise HTTPException(status_code=404, detail=f"Dades de preus per {ticker} no trobades")
        
        # Ordenar per data (més recent primer)
        prices.sort(key=lambda x: x.date, reverse=True)
        latest_data = prices[0]
        
        return CompanyDetail(
            company=company_kpi,
            latest_data=latest_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error carregant detalls de {ticker}: {str(e)}")


@router.get("/companies/{ticker}/series", response_model=SeriesResponse)
async def get_company_series(ticker: str, range: str = "1Y"):
    """Retorna sèries de preus per un ticker i rang específics"""
    try:
        # Validar rang
        valid_ranges = ["1M", "3M", "1Y"]
        if range not in valid_ranges:
            raise HTTPException(
                status_code=400, 
                detail=f"Rang '{range}' no vàlid. Usa: {', '.join(valid_ranges)}"
            )
        
        # Obtenir dades
        prices = db.get_series_data(ticker, range)
        if not prices:
            raise HTTPException(status_code=404, detail=f"Dades de sèries per {ticker} no trobades")
        
        return SeriesResponse(
            ticker=ticker,
            range=range,
            prices=prices
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error carregant sèries de {ticker}: {str(e)}")


@router.post("/refresh")
async def refresh_all_data():
    """Refresca totes les dades (neteja cache)"""
    try:
        db.refresh_data()
        return {
            "status": "success",
            "message": "Totes les dades han estat refrescades",
            "real_data_enabled": db.use_real_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refrescant dades: {str(e)}")


@router.post("/refresh/{ticker}")
async def refresh_ticker_data(ticker: str):
    """Refresca dades d'un ticker específic"""
    try:
        # Comprovar que l'empresa existeix
        company = db.get_company_by_ticker(ticker)
        if not company:
            raise HTTPException(status_code=404, detail=f"Empresa {ticker} no trobada")
        
        db.refresh_data(ticker)
        
        return {
            "status": "success",
            "message": f"Dades de {ticker} refrescades",
            "ticker": ticker,
            "real_data_enabled": db.use_real_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refrescant {ticker}: {str(e)}")


@router.get("/data-source")
async def get_data_source():
    """Retorna informació sobre la font de dades actual"""
    return {
        "yfinance_available": REAL_DATA_AVAILABLE,
        "using_real_data": db.use_real_data,
        "source": "Yahoo Finance (real-time)" if db.use_real_data else "Mock data (fixtures)",
        "cache_enabled": True,
        "cache_ttl_minutes": {
            "company_info": 1440,
            "price_data": 60,
            "realtime": 5
        }
    }
