# Deployment a Render

Aquest document explica com fer el deployment del Catalunya Dashboard a Render.

## Preparació

Els fitxers de configuració ja estan preparats:
- ✅ `render.yaml` - Configuració del servei
- ✅ `start.sh` - Script d'inici
- ✅ `requirements.txt` - Dependencies actualitzades

## Passos per fer el deployment

### 1. Pujar els canvis a GitHub
```bash
git add .
git commit -m "🚀 Add Render deployment config"
git push origin main
```

### 2. Crear compte a Render
- Anar a https://render.com
- Sign up amb GitHub (recomanat)

### 3. Crear nou servei web
1. Clicar "New +" → "Web Service"
2. Connectar el repositori GitHub `guillemperdigo/catalunya-dashboard`
3. Configuració automàtica (Render detectarà `render.yaml`)
4. Clicar "Create Web Service"

### 4. Esperar el deployment
- Render farà build automàticament (~2-5 minuts)
- Generarà les dades mock automàticament
- Assignarà una URL pública

## URL final
Un cop completat, tindràs una URL com:
`https://catalunya-dashboard.onrender.com`

## Funcionalitats disponibles
- ✅ Pàgina d'inici amb empreses destacades
- ✅ Llistat complet d'empreses amb filtres
- ✅ Pàgines de detall amb gràfics interactius
- ✅ API REST per a dades JSON
- ✅ SSL automàtic (HTTPS)
- ✅ Responsive design

## Actualitzacions automàtiques
Cada cop que facis `git push` al repositori, Render farà redeploy automàticament.

## Limitacions del pla gratuït
- L'aplicació s'adorma després de 15 minuts d'inactivitat
- Temps de "despertar": ~30 segons
- 750 hores/mes gratuïtes (suficient per ús personal)

## Upgrade a pla de pagament
Per tenir l'aplicació sempre activa: $7/mes
