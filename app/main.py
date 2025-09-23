from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.companies import router as companies_router
from app.db import db
import random
import json
import os

# Crear aplicació FastAPI
app = FastAPI(
    title="Catalunya Stocks Dashboard",
    description="Dashboard d'empreses catalanes en borsa",
    version="1.0.0"
)

# Muntar fitxers estàtics
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Incluir rutes API
app.include_router(companies_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Pàgina d'inici amb 3 empreses destacades"""
    try:
        # Obtenir totes les empreses amb KPIs
        companies = db.get_company_kpis()
        
        if len(companies) < 3:
            raise HTTPException(status_code=500, detail="No hi ha prou empreses per mostrar")
        
        # Seleccionar 3 empreses destacades (les primeres 3 per simplicitat)
        featured_companies = companies[:3]
        
        # Per cada empresa destacada, obtenir dades per sparkline
        sparkline_data = {}
        for company in featured_companies:
            # Obtenir últimes 30 dades per sparkline
            prices = db.get_series_data(company.ticker, "1M")
            if prices:
                sparkline_data[company.ticker] = [p.close for p in prices[-30:]]  # Últims 30 punts
            else:
                sparkline_data[company.ticker] = []
        
        return templates.TemplateResponse("home.html", {
            "request": request,
            "featured_companies": [c.dict() for c in featured_companies],
            "sparkline_data": sparkline_data,
            "title": "Empreses catalanes en borsa"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error carregant pàgina d'inici: {str(e)}")


@app.get("/companies", response_class=HTMLResponse)
async def companies_page(request: Request):
    """Pàgina amb llistat complet d'empreses"""
    try:
        companies = db.get_company_kpis()
        
        # Obtenir llistes úniques per filtres
        exchanges = list(set(c.exchange for c in companies))
        sectors = list(set(c.sector for c in companies))
        
        return templates.TemplateResponse("companies.html", {
            "request": request,
            "companies": [c.dict() for c in companies],
            "exchanges": exchanges,
            "sectors": sectors,
            "title": "Totes les empreses"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error carregant llista d'empreses: {str(e)}")


@app.get("/company/{ticker}", response_class=HTMLResponse)
async def company_detail(request: Request, ticker: str):
    """Pàgina de detall d'una empresa"""
    try:
        # Obtenir empresa
        company = db.get_company_by_ticker(ticker)
        if not company:
            raise HTTPException(status_code=404, detail=f"Empresa {ticker} no trobada")
        
        # Obtenir KPIs
        kpis = db.get_company_kpis()
        company_kpi = next((kpi for kpi in kpis if kpi.ticker == ticker), None)
        
        if not company_kpi:
            raise HTTPException(status_code=404, detail=f"Dades KPI per {ticker} no trobades")
        
        # Obtenir dades de preus per defecte (1Y)
        prices = db.get_series_data(ticker, "1Y")
        if not prices:
            raise HTTPException(status_code=404, detail=f"Dades de preus per {ticker} no trobades")
        
        return templates.TemplateResponse("company_detail.html", {
            "request": request,
            "company": company_kpi.dict(),
            "prices": [p.dict() for p in prices],
            "title": f"{company.name} ({ticker})"
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error carregant detalls de {ticker}: {str(e)}")


@app.get("/demographics", response_class=HTMLResponse)
async def demographics_page(request: Request):
    """Pàgina de demografia"""
    try:
        # Carregar dades demogràfiques
        demographics_path = os.path.join("data", "demographics.json")
        with open(demographics_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return templates.TemplateResponse("demographics.html", {
            "request": request,
            "overview": data["overview"],
            "regions": data["regions"],
            "age_groups": data["age_groups"],
            "title": "Demografia de Catalunya"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error carregant demografia: {str(e)}")


# Endpoint de salut
@app.get("/health")
async def health_check():
    """Endpoint per verificar que l'API funciona"""
    return {"status": "ok", "message": "Catalunya Stocks API funcionant correctament"}
