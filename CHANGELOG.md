# Changelog

## [Unreleased] - 2025-10-03

### ✨ Added - Integració amb dades reals (Yahoo Finance)

#### Noves funcionalitats
- **Servei de dades reals** (`app/services/stock_data.py`)
  - Integració completa amb Yahoo Finance via yfinance
  - Sistema de cache en disc amb TTL configurable (1h preus, 24h info empresa, 5min temps real)
  - Suport per múltiples períodes (1d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
  - Suport per múltiples intervals (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)

- **DataManager millorat** (`app/db.py`)
  - Detecció automàtica de yfinance disponible
  - Fallback automàtic a dades mock si l'API falla
  - Mètodes `clear_cache()` i `refresh_data()` per gestió manual
  - Flag `use_real_data` per activar/desactivar dades reals

- **Nous endpoints API** (`app/api/companies.py`)
  - `GET /api/data-source` - Comprovar font de dades actual
  - `POST /api/refresh` - Refrescar totes les dades
  - `POST /api/refresh/{ticker}` - Refrescar empresa específica

- **Script de testing** (`scripts/test_real_data.py`)
  - Verificar disponibilitat de yfinance
  - Provar obtenció de dades reals
  - Benchmark del sistema de cache
  - Mostrar exemples de dades obtingudes

#### Documentació
- **Guia completa** (`docs/REAL_DATA_INTEGRATION.md`)
  - Instal·lació pas a pas
  - Arquitectura del sistema
  - Configuració avançada
  - Solució de problemes
  - Millors pràctiques
  - Límits i restriccions

- **README actualitzat**
  - Secció nova sobre integració amb dades reals
  - Actualització de característiques
  - Actualització de stack tecnològic
  - Nous endpoints API documentats

#### Dependències
- Afegit `yfinance>=0.2.0` a `requirements.txt`

### 🔧 Changed
- Cache de dades ara persisteix a `data/cache/` en format JSON
- Empreses ara poden usar dades reals o mock transparentment
- Stack tecnològic actualitzat per reflectir dades reals

### 📝 Technical Details

#### Arquitectura

```
Dashboard (FastAPI)
    ↓
DataManager (db.py)
    ↓
    ├── [TRY] Yahoo Finance (yfinance)
    │         ↓
    │    Cache (1h TTL)
    │         ↓
    │    ✅ Dades reals
    │
    └── [FALLBACK] JSON fixtures
              ↓
         📊 Dades mock
```

#### Cache Strategy
- **Disc**: `data/cache/*.json` amb timestamps
- **Memòria**: Dict en `DataManager._prices_cache`
- **TTL**: Automàtic per tipus de dada

#### Performance
- Primera càrrega: ~2-3s per empresa
- Amb cache: ~0.01s per empresa (200x més ràpid)
- Cache hit rate esperat: >95% en producció

---

## [1.0.0] - 2025-10-02

### Added
- Mòdul d'empreses amb 6 empreses catalanes
- Mòdul de demografia
- Mòdul d'habitatge
- Mòdul de medi ambient
- Disseny inspirat en The New York Times
- Gràfics interactius amb Plotly.js
- API REST amb FastAPI
- Sistema de templates amb Jinja2

### Initial Features
- Pàgina d'inici amb empreses destacades
- Llistat complet d'empreses amb cerca i filtres
- Detall d'empresa amb gràfics de preus i volum
- Pàgines de demografia, habitatge i medi ambient
- Dades mock generades amb random walk

