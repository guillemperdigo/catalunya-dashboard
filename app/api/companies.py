from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models import CompanyKPI, SeriesResponse, CompanyDetail, PriceData
from app.db import db

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
