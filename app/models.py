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


# Models per Habitatge
class HousingPriceData(BaseModel):
    region: str
    year: int
    avg_price_sale: float  # €/m²
    avg_price_rent: float  # €/mes
    price_change_1y_pct: float
    rent_change_1y_pct: float
    affordability_index: float  # % ingressos per habitatge


class ConstructionData(BaseModel):
    region: str
    year: int
    new_housing_units: int
    building_permits: int
    construction_starts: int
    construction_completions: int


class MortgageData(BaseModel):
    region: str
    year: int
    avg_mortgage_amount: float
    avg_interest_rate: float
    mortgage_approvals: int
    default_rate: float


class HousingOverview(BaseModel):
    avg_price_m2: float
    price_change_1y: float
    avg_rent: float
    rent_change_1y: float
    new_units_built: int
    mortgage_volume: float


# Models per Medi Ambient
class AirQualityData(BaseModel):
    city: str
    date: str
    pm25: float  # µg/m³
    pm10: float  # µg/m³
    no2: float   # µg/m³
    o3: float    # µg/m³
    aqi: int     # Air Quality Index (0-500)
    quality_level: str  # "Bo", "Moderat", "Dolent", "Molt dolent"


class EnergyData(BaseModel):
    region: str
    year: int
    total_consumption_gwh: float
    renewable_percentage: float
    solar_capacity_mw: float
    wind_capacity_mw: float
    hydro_capacity_mw: float
    co2_emissions_tons: float


class WasteData(BaseModel):
    region: str
    year: int
    total_waste_tons: int
    recycling_rate: float  # %
    organic_waste_tons: int
    plastic_waste_tons: int
    paper_waste_tons: int
    glass_waste_tons: int
    waste_per_capita_kg: float


class EnvironmentOverview(BaseModel):
    avg_aqi: float
    renewable_percentage: float
    recycling_rate: float
    co2_reduction_1y: float
    green_energy_capacity_mw: float
    waste_per_capita: float
