# Backend – Movie Explorer API

Ce dépôt contient l'API REST du projet **Movie Explorer**, développée avec Flask et MongoDB. Elle alimente l'interface utilisateur en données sur les films, genres, acteurs et favoris, en s'appuyant notamment sur l'API The Movie Database (TMDB).

---

## Démarrage rapide

### 1. Créer un fichier `.env`

À la racine du dossier `tp-mongo-back`, créez un fichier `.env` contenant :

```env
DB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/movie-app?retryWrites=true&w=majority
TMDB_API_KEY=your_tmdb_api_key
TMDB_BASE=https://api.themoviedb.org/3
```

> Un fichier `.env.example` est fourni à titre de modèle.

### 2. Lancer l'API en local sans Docker

Assurez-vous d'avoir Python 3.11 installé, ainsi que `pip` :

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
python run.py
```

L'API sera disponible sur : `http://localhost:5000`

### 3. Lancer l'API avec Docker

```bash
docker build -t tp-mongo-backend .
docker run -p 5000:5000 --env-file .env tp-mongo-backend
```

Ou via `docker-compose` depuis le dossier parent :

```bash
docker-compose up --build
```

---

## Endpoints disponibles

Les routes suivantes sont exposées :

### Films

- `GET /films/` — Liste de tous les films
- `GET /films/<movie_id>` — Détail d’un film
- `GET /films/search` — Recherche (par titre, genre, etc.)
- `GET /films/latest` — Dernières sorties
- `GET /films/hottest` — Films les plus tendances
- `GET /films/top-rated` — Films les mieux notés
- `GET /films/analytics/overview` — Statistiques globales
- `GET /films/title_frequency` — Répartition des titres
- `GET /films/details/<movie_id>` — Infos enrichies via TMDB
- `GET /films/update-latest` — Synchronisation avec TMDB
- Suggestions :
  - `/films/recommended/`
  - `/films/most-popular`
  - `/films/critically-acclaimed`
  - `/films/underrated`
  - `/films/best-french`
  - `/films/best-action`
  - `/films/nostalgia-90s`
  - `/films/sci-fi`
  - `/films/true-stories`
  - `/films/best-by-decade`

### Acteurs

- `GET /actors/<actor_id>` — Détail d’un acteur (depuis TMDB)

### Genres

- `GET /genres/` — Liste complète des genres
- `GET /genres/popular?limit=N` — Genres les plus populaires
- `GET /genres/<genre_name>` — Films populaires d’un genre

### Favoris

Les favoris sont gérés par adresse IP :

- `GET /favorites/` — Récupérer ses favoris
- `POST /favorites/toggle` — Ajouter/retirer un film

---

## Stack technique

- **Python 3.11** avec **Flask**
- **MongoDB Atlas** comme base de données NoSQL
- **Flask-CORS** pour permettre les appels frontend
- **Dotenv** pour la configuration par environnement
- **Requests** pour communiquer avec l’API TMDB

---

## Organisation du code

```txt
app/
├── routes/         # Routes Flask (films, genres, acteurs, favoris)
├── services/       # Logique métier et communication TMDB
├── models/         # Représentation des entités (Movie, Genre, etc.)
├── errors/         # Gestion des erreurs
├── extensions.py   # Initialisation des extensions (Mongo)
├── config.py       # (optionnel) Configuration supplémentaire
└── __init__.py     # Création de l'application Flask
```

---

## Remarque

Le backend peut être utilisé indépendamment ou via le projet global `tp-mongo`, qui intègre aussi le frontend React et la configuration Docker.
