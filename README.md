# Catalunya Dashboard

Dashboard elegant i minimalista per visualitzar dades de Catalunya, començant per indicadors bursàtils d'empreses catalanes. Inspirat en el disseny de The New York Times.

## Característiques

- **Disseny elegant**: Inspirat en The New York Times amb tipografia seriosa, molt espai en blanc i jerarquia clara
- **Dades mock**: Utilitza fixtures generades amb random walk per validar estructura i UI
- **Gràfics interactius**: Visualitzacions amb Plotly.js per preus i volums
- **Responsive**: Disseny adaptat a dispositius mòbils i desktop
- **Ràpid**: Server-Side Rendering amb FastAPI i Jinja2

## Stack tecnològic

- **Backend**: FastAPI + Jinja2 (SSR)
- **Frontend**: Tailwind CSS + JavaScript vanilla
- **Gràfics**: Plotly.js
- **Dades**: Fixtures JSON (sense base de dades)
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

### 2. Generar dades mock

```bash
python scripts/gen_mock_data.py
```

### 3. Executar el servidor

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
│   │   └── company_detail.html # Detall d'empresa
│   └── static/
│       └── css/
│           └── main.css       # Estils personalitzats
├── data/
│   ├── companies.json         # Metadades d'empreses
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

### 1. Inici (`/`)
- Hero amb títol principal
- 3 empreses destacades amb sparklines
- Resum del mercat

### 2. Llistat d'empreses (`/companies`)
- Taula amb totes les empreses
- Cercador per nom/ticker
- Filtres per borsa i sector
- Ordenació i paginació

### 3. Detall d'empresa (`/company/{ticker}`)
- Informació completa de l'empresa
- Gràfic interactiu de preus (1M/3M/1Y)
- Gràfic de volum
- KPIs: preu actual, màxim/mínim 52s, capitalització

## API Endpoints

### Empreses
- `GET /api/companies` - Llista d'empreses amb KPIs
- `GET /api/companies/{ticker}` - Detalls d'una empresa
- `GET /api/companies/{ticker}/series?range=1M|3M|1Y` - Sèries de preus

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

### Personalitzar estils

Editar `app/static/css/main.css` per ajustar l'aparença mantenint l'estil NYT.

### Afegir nous endpoints

Crear nous routers a `app/api/` i incloure'ls a `app/main.py`.

## Extensibilitat futura

### Mòdul Stocks (actual)
- **Dades reals**: Connectar a APIs financeres (Alpha Vantage, Yahoo Finance)
- **Base de dades**: Migrar de fixtures a PostgreSQL/SQLite
- **Alertes**: Notificacions de preu i volum

### Nous mòduls
- **Demografia**: Població, natalitat, immigració per comarques
- **Economia**: PIB, atur, salaris per sectors i regions
- **Medi ambient**: Qualitat de l'aire, consum energètic, reciclatge
- **Turisme**: Visitants, ocupació hotelera, esdeveniments
- **Educació**: Centres, resultats acadèmics, inversió
- **Sanitat**: Hospitals, llistes d'espera, indicadors de salut

### Funcionalitats generals
- **Internacionalització**: Suport per català/espanyol/anglès
- **Autenticació**: Usuaris i dashboards personalitzats
- **Mobile app**: PWA o React Native

## Llicència

Projecte de demostració. Dades mock generades aleatòriament.
