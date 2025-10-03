# Catalunya Dashboard

Dashboard elegant i minimalista per visualitzar dades de Catalunya amb múltiples mòduls: indicadors bursàtils d'empreses catalanes, demografia, habitatge i medi ambient. Inspirat en el disseny de The New York Times.

## Característiques

- **Disseny elegant**: Inspirat en The New York Times amb tipografia seriosa, molt espai en blanc i jerarquia clara
- **Dades reals**: Integració amb Yahoo Finance (yfinance) amb fallback automàtic a dades mock
- **Sistema de cache intel·ligent**: Cache de 1 hora per dades de preus per optimitzar rendiment
- **Gràfics interactius**: Visualitzacions amb Plotly.js per preus i volums
- **Responsive**: Disseny adaptat a dispositius mòbils i desktop
- **Ràpid**: Server-Side Rendering amb FastAPI i Jinja2

## Stack tecnològic

- **Backend**: FastAPI + Jinja2 (SSR)
- **Frontend**: Tailwind CSS + JavaScript vanilla
- **Gràfics**: Plotly.js
- **Dades**: Yahoo Finance API (yfinance) + Fixtures JSON com a fallback
- **Cache**: Sistema de cache en disc amb TTL configurable
- **Servidor**: Uvicorn

## Instal·lació i ús

### 1. Configuració de l'entorn

```bash
# Crear entorn virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

# Instal·lar dependències
pip install -r requirements.txt
```

### 2. Generar dades mock (opcional)

**Nota**: Amb yfinance instal·lat, el sistema usa dades reals automàticament. Les dades mock només són necessàries com a fallback.

```bash
python scripts/gen_mock_data.py
```

### 3. Provar integració amb dades reals (recomanat)

```bash
python scripts/test_real_data.py
```

Això verificarà que yfinance funciona i mostrarà dades reals de les empreses.

### 4. Executar el servidor

```bash
uvicorn app.main:app --reload
```

L'aplicació estarà disponible a: http://localhost:8000

## Estructura del projecte

```
catalunya-dashboard/
├── app/
│   ├── main.py                 # Aplicació FastAPI principal
│   ├── db.py                   # Gestor de dades (fixtures)
│   ├── models.py               # Models Pydantic
│   ├── api/
│   │   └── companies.py        # Endpoints API REST
│   ├── templates/
│   │   ├── layout.html         # Template base
│   │   ├── home.html          # Pàgina d'inici
│   │   ├── companies.html     # Llistat d'empreses
│   │   ├── company_detail.html # Detall d'empresa
│   │   ├── demographics.html  # Demografia
│   │   ├── housing.html       # Habitatge
│   │   └── environment.html   # Medi ambient
│   └── static/
│       └── css/
│           └── main.css       # Estils personalitzats
├── data/
│   ├── companies.json         # Metadades d'empreses
│   ├── demographics.json      # Dades demogràfiques
│   ├── housing.json           # Dades d'habitatge
│   ├── environment.json       # Dades de medi ambient
│   └── prices/               # Sèries de preus per empresa
│       ├── CABK.MC.json
│       ├── GRF.MC.json
│       └── ...
├── scripts/
│   └── gen_mock_data.py      # Generador de dades mock
├── requirements.txt
└── README.md
```

## Pàgines disponibles

### Mòdul d'empreses

#### 1. Inici (`/`)
- Hero amb títol principal
- 3 empreses destacades amb sparklines
- Resum del mercat

#### 2. Llistat d'empreses (`/companies`)
- Taula amb totes les empreses
- Cercador per nom/ticker
- Filtres per borsa i sector
- Ordenació i paginació

#### 3. Detall d'empresa (`/company/{ticker}`)
- Informació completa de l'empresa
- Gràfic interactiu de preus (1M/3M/1Y)
- Gràfic de volum
- KPIs: preu actual, màxim/mínim 52s, capitalització

### Mòdul de demografia (`/demographics`)
- Població total i evolució
- Taxes de natalitat i mortalitat
- Esperança de vida
- Dades per regions
- Distribució per grups d'edat

### Mòdul d'habitatge (`/housing`)
- Preus mitjans de compra i lloguer (€/m²)
- Evolució històrica de preus
- Dades de construcció i permisos
- Informació d'hipoteques
- Índex d'accessibilitat

### Mòdul de medi ambient (`/environment`)
- Qualitat de l'aire (PM2.5, PM10, NO₂, O₃, AQI)
- Consum i producció energètica
- Percentatge d'energies renovables
- Evolució d'emissions de CO₂
- Reciclatge i gestió de residus

## API Endpoints

### Empreses
- `GET /api/companies` - Llista d'empreses amb KPIs
- `GET /api/companies/{ticker}` - Detalls d'una empresa
- `GET /api/companies/{ticker}/series?range=1M|3M|1Y` - Sèries de preus

### Gestió de dades
- `GET /api/data-source` - Informació sobre la font de dades actual (real vs mock)
- `POST /api/refresh` - Refrescar totes les dades (netejar cache)
- `POST /api/refresh/{ticker}` - Refrescar dades d'una empresa específica

### Utilitats
- `GET /health` - Estat de l'API

## Empreses incloses (mock)

- **CaixaBank** (CABK.MC) - Banks
- **Grifols** (GRF.MC) - Healthcare  
- **Cellnex** (CLNX.MC) - Telecom
- **Fluidra** (FDR.MC) - Industrials
- **Inmobiliaria Colonial** (COL.MC) - Real Estate
- **Almirall** (ALM.MC) - Pharma

## Disseny NYT-inspired

### Tipografia
- **Serif** (Georgia): Títols i text llarg per elegància i llegibilitat
- **Sans-serif** (Inter): UI, botons i elements interactius
- **Monospace**: Xifres, tickers i dades numèriques

### Colors
- **Negre** (#111): Text principal
- **Grisos** (#444, #777, #e5e5e5): Text secundari i línies
- **Fons** (#fafafa): Fons principal
- **Accent** (#0b57d0): Enllaços i elements interactius

### Principis de disseny
- Màxim 1040px d'amplada per llegibilitat
- Marges generosos i interlineal alt
- Jerarquia clara amb tipografia
- Hover effects subtils
- Focus states accessibles

## Desenvolupament

### Afegir noves empreses

1. Editar `data/companies.json`
2. Executar `python scripts/gen_mock_data.py`
3. Reiniciar el servidor

### Actualitzar dades d'altres mòduls

Les dades de demografia, habitatge i medi ambient estan a:
- `data/demographics.json`
- `data/housing.json`
- `data/environment.json`

Editar aquests fitxers directament i reiniciar el servidor.

### Personalitzar estils

Editar `app/static/css/main.css` per ajustar l'aparença mantenint l'estil NYT.

### Afegir nous endpoints

Crear nous routers a `app/api/` i incloure'ls a `app/main.py`.

### Afegir nous mòduls

1. Crear models a `app/models.py`
2. Afegir dades mock a `data/`
3. Crear template HTML a `app/templates/`
4. Afegir ruta a `app/main.py`

## 🔌 Integració amb dades reals

El projecte inclou integració completa amb **Yahoo Finance** per obtenir dades bursàtils reals.

### Activar dades reals

Les dades reals s'activen automàticament si yfinance està instal·lat:

```bash
pip install yfinance
python scripts/test_real_data.py  # Verificar funcionament
```

### Característiques

- ✅ **Automàtic**: Dades reals per defecte, fallback a mock si falla
- ✅ **Cache intel·ligent**: 1 hora per preus, evita sobrecàrrega de l'API
- ✅ **Transparent**: El codi no canvia, funciona amb ambdues fonts
- ✅ **API de gestió**: Endpoints per refrescar i comprovar estat

### Comprovar estat

```bash
curl http://localhost:8000/api/data-source
```

Resposta:
```json
{
  "yfinance_available": true,
  "using_real_data": true,
  "source": "Yahoo Finance (real-time)",
  "cache_enabled": true
}
```

### Refrescar dades

```bash
# Refrescar totes les empreses
curl -X POST http://localhost:8000/api/refresh

# Refrescar només CaixaBank
curl -X POST http://localhost:8000/api/refresh/CABK.MC
```

### Documentació completa

Consulta [`docs/REAL_DATA_INTEGRATION.md`](docs/REAL_DATA_INTEGRATION.md) per:
- Guia d'instal·lació detallada
- Arquitectura del sistema
- Configuració avançada
- Solució de problemes
- Millors pràctiques

## Extensibilitat futura

### Millores dels mòduls actuals
- **Stocks**: ✅ Dades reals implementades amb Yahoo Finance. Futures: alertes de preu, indicadors tècnics (SMA, RSI)
- **Demografia**: Afegir projeccions, piràmides poblacionals interactives, flux migratori detallat
- **Habitatge**: Mapes de calor per zones, prediccions de preus, comparatives per barris
- **Medi ambient**: Alertes de qualitat de l'aire, seguiment en temps real, històrics més extensos

### Nous mòduls
- **Economia**: PIB, atur, salaris per sectors i regions
- **Turisme**: Visitants, ocupació hotelera, esdeveniments
- **Educació**: Centres, resultats acadèmics, inversió
- **Sanitat**: Hospitals, llistes d'espera, indicadors de salut
- **Transport**: Tràfic, transport públic, mobilitat sostenible
- **Cultura**: Museus, teatres, esdeveniments culturals

### Funcionalitats generals
- **Base de dades**: Migrar de fixtures JSON a PostgreSQL/SQLite per millor rendiment
- **API REST completa**: Endpoints per tots els mòduls amb autenticació
- **Internacionalització**: Suport per català/espanyol/anglès
- **Autenticació**: Usuaris i dashboards personalitzats
- **Mobile app**: PWA o React Native
- **Exportació de dades**: Descarregar dades en CSV, Excel, PDF

## Llicència

Projecte de demostració. Dades mock generades aleatòriament.
