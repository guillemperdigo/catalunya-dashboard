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


# Models per Demografia
class PopulationData(BaseModel):
    region: str  # Comarca/Província
    year: int
    population: int
    population_change_pct: float
    birth_rate: float
    death_rate: float
    migration_balance: int


class AgeGroupData(BaseModel):
    region: str
    year: int
    age_0_14: int
    age_15_64: int
    age_65_plus: int
    aging_index: float  # Ratio 65+/0-14


class DemographicsOverview(BaseModel):
    total_population: int
    population_change_1y: float
    birth_rate: float
    death_rate: float
    life_expectancy: float
    regions: List[PopulationData]
