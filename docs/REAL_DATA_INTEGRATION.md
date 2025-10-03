# Integració amb Dades Reals (Yahoo Finance)

Aquest document explica com funciona la integració amb dades reals via **yfinance** i com usar-la.

## 🚀 Instal·lació

### 1. Instal·lar yfinance

Des del teu entorn virtual:

```bash
# Activar entorn virtual
source .venv/bin/activate  # Mac/Linux
# o
.venv\Scripts\activate     # Windows

# Instal·lar yfinance
pip install yfinance
```

**Nota**: Si tens problemes amb la instal·lació de `curl_cffi`, pots provar:

```bash
# Actualitzar pip primer
pip install --upgrade pip

# Instal·lar amb wheel precompilat
pip install --upgrade yfinance

# O especificar una versió més antiga
pip install yfinance==0.2.38
```

### 2. Verificar instal·lació

Executa el script de prova:

```bash
python scripts/test_real_data.py
```

Si tot funciona correctament, hauràs de veure:
- ✅ yfinance disponible: Sí
- ✅ Dades reals obtingudes per cada empresa
- ✅ KPIs calculats amb dades reals
- ⚡ Sistema de cache funcionant

## 📊 Com funciona

### Arquitectura

```
┌─────────────────┐
│   Dashboard     │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  db.py   │ ◄─── DataManager amb fallback automàtic
    └────┬─────┘
         │
    ┌────▼──────────────────┐
    │ Intentar dades reals  │
    │ (stock_data.py)       │
    └────┬──────────────────┘
         │
    ┌────▼────────┐    ┌──────────────┐
    │ Yahoo       │ ❌ │ Fallback a   │
    │ Finance     │───►│ dades mock   │
    │ (yfinance)  │    │ (JSON)       │
    └─────────────┘    └──────────────┘
         │ ✅
    ┌────▼────────┐
    │   Cache     │ (1 hora)
    │ (disk+mem)  │
    └─────────────┘
```

### Flux de dades

1. **Primera request**: 
   - Intenta obtenir dades de Yahoo Finance
   - Si funciona → guarda a cache (1 hora)
   - Si falla → usa dades mock dels JSON

2. **Requests següents** (< 1 hora):
   - Retorna dades des del cache (molt més ràpid)
   
3. **Després d'1 hora**:
   - Cache expira automàticament
   - Torna a obtenir dades fresques de Yahoo Finance

## 🎯 Ús

### Dades reals activades per defecte

Quan yfinance està instal·lat, el sistema usa dades reals automàticament:

```python
from app.db import db

# Usa dades reals si yfinance està disponible
prices = db.get_price_data("CABK.MC")
```

### Forçar dades mock

Si vols usar dades mock encara que yfinance estigui disponible:

```python
# A db.py
db = DataManager(use_real_data=False)

# O per una request específica
prices = db.get_price_data("CABK.MC", force_mock=True)
```

### Refrescar dades manualment

```python
from app.db import db

# Refrescar totes les empreses
db.refresh_data()

# Refrescar només una empresa
db.refresh_data("CABK.MC")
```

## 🌐 API Endpoints

### Comprovar font de dades

```bash
GET /api/data-source
```

Resposta:
```json
{
  "yfinance_available": true,
  "using_real_data": true,
  "source": "Yahoo Finance (real-time)",
  "cache_enabled": true,
  "cache_ttl_minutes": {
    "company_info": 1440,
    "price_data": 60,
    "realtime": 5
  }
}
```

### Refrescar totes les dades

```bash
POST /api/refresh
```

### Refrescar una empresa

```bash
POST /api/refresh/CABK.MC
```

## 🗂️ Sistema de Cache

### Cache de disc

Les dades es guarden a `data/cache/`:

```
data/cache/
├── CABK.MC_info.json          # Info empresa (24h TTL)
├── CABK.MC_1y_1d_prices.json  # Preus històrics (1h TTL)
└── CABK.MC_realtime.json      # Dades en temps real (5min TTL)
```

### TTL (Time To Live)

| Tipus de dada      | TTL      | Raó                          |
|--------------------|----------|------------------------------|
| Info empresa       | 24 hores | Canvia poc (sector, etc.)    |
| Preus històrics    | 1 hora   | S'actualitzen cada dia       |
| Preu actual        | 5 minuts | Dades quasi en temps real    |

### Netejar cache

```bash
# Des de Python
from app.db import db
db.refresh_data()  # Neteja tot

# O des de l'API
curl -X POST http://localhost:8000/api/refresh
```

## 🔧 Configuració avançada

### Canviar TTL del cache

Edita `app/services/stock_data.py`:

```python
self.cache_ttl = {
    "company_info": 1440,  # 24 hores → canviar aquí
    "price_data": 60,      # 1 hora → canviar aquí
    "realtime": 5          # 5 minuts → canviar aquí
}
```

### Afegir més empreses

1. Afegir a `data/companies.json`:
```json
{
  "name": "Banco Santander",
  "ticker": "SAN.MC",
  "exchange": "BME",
  "sector": "Banks",
  "hq_province": "Madrid"
}
```

2. Reiniciar servidor → les dades es descarreguen automàticament

### Períodes disponibles

Per `get_historical_data()`:

- **Períodes**: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`
- **Intervals**: `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1wk`, `1mo`

Exemple:
```python
from app.services.stock_data import stock_service

# Últims 3 mesos amb dades diàries
data = stock_service.get_historical_data("CABK.MC", period="3mo", interval="1d")

# Últim dia amb dades de cada minut
data = stock_service.get_historical_data("CABK.MC", period="1d", interval="1m")
```

## 🚨 Solució de problemes

### Error: "yfinance no disponible"

**Causa**: yfinance no està instal·lat o hi ha un error d'importació

**Solució**:
```bash
pip install yfinance
python scripts/test_real_data.py
```

### Error: "No s'han trobat dades per {ticker}"

**Causa**: El ticker pot ser incorrecte o no existir a Yahoo Finance

**Solució**:
- Comprovar ticker a https://finance.yahoo.com/
- Per empreses espanyoles, usa format `.MC` (ex: `CABK.MC`)
- Provar amb un altre ticker conegut (ex: `AAPL`, `MSFT`)

### Cache no s'actualitza

**Solució**:
```bash
# Via API
curl -X POST http://localhost:8000/api/refresh

# Via Python
python -c "from app.db import db; db.refresh_data()"
```

### Dades massa antigues

**Causa**: Mercat tancat (cap de setmana, festius)

**Comportament normal**: yfinance retorna les últimes dades disponibles (últim dia de mercat obert)

## 📈 Rendiment

### Primera càrrega (sense cache)

- Per empresa: ~2-3 segons
- Per 6 empreses: ~15-20 segons

### Amb cache

- Per empresa: ~0.01 segons (200x més ràpid!)
- Per 6 empreses: ~0.06 segons

### Millors pràctiques

1. **Pre-càrrega**: Executar script d'actualització cada hora (cron job)
2. **Lazy loading**: Carregar dades sota demanda per cada empresa
3. **Batch requests**: Per actualitzacions massives, usar `get_multiple_tickers()`

Exemple de cron job:
```bash
# Actualitzar dades cada hora
0 * * * * cd /path/to/project && python scripts/update_data.py
```

## 🔐 Límits i restriccions

### Yahoo Finance (yfinance)

- ✅ **Gratuït** sense límits publicats
- ✅ **No requereix API key**
- ⚠️ Ús just i raonable (evitar milers de requests per segon)
- ⚠️ No garantit per producció crítica (pot canviar)

### Recomanacions

- **Desenvolupament**: yfinance és perfecte
- **Producció petita**: yfinance amb cache adequat
- **Producció gran**: Considerar APIs professionals (Alpha Vantage, IEX Cloud, etc.)

## 🎯 Properes millores

- [ ] Tasca programada per actualitzar dades automàticament
- [ ] Webhooks per notificar canvis de preu
- [ ] Suport per múltiples fonts de dades (Alpha Vantage, IEX)
- [ ] Base de dades (PostgreSQL) en lloc de cache de fitxers
- [ ] Indicadors tècnics (SMA, RSI, MACD)
- [ ] Dades fonamentals (EPS, P/E ratio, dividends)

## 📚 Referències

- [yfinance GitHub](https://github.com/ranaroussi/yfinance)
- [Yahoo Finance](https://finance.yahoo.com/)
- [pandas documentation](https://pandas.pydata.org/)

