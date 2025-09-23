from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class Company(BaseModel):
    name: str
    ticker: str
    exchange: str
    sector: str
    hq_province: str


class PriceData(BaseModel):
    date: str
    close: float
    open: float
    high: float
    low: float
    volume: int


class CompanyKPI(BaseModel):
    name: str
    ticker: str
    exchange: str
    sector: str
    hq_province: str
    last_price: float
    chng_1d_pct: float
    high_52w: float
    low_52w: float
    mkt_cap: float


class SeriesResponse(BaseModel):
    ticker: str
    range: str
    prices: List[PriceData]


class CompanyDetail(BaseModel):
    company: CompanyKPI
    latest_data: PriceData
