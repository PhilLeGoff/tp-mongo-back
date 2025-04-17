# Movie Explorer – Backend Flask

Ce dépôt correspond à l’API backend de l’application **Movie Explorer**, construite avec **Flask** et connectée à une base de données **MongoDB**. L’API expose des routes permettant de récupérer et manipuler des données sur les films, les genres, les acteurs et les favoris des utilisateurs.

---

## Objectif de l'application

Fournir une API RESTful permettant au frontend de :

- Récupérer des listes de films (populaires, récents, par genre...)
- Visualiser des données analytiques sur les genres et films appréciés
- Gérer des favoris liés à l’adresse IP de l’utilisateur
- Explorer les informations liées aux acteurs

---

## Structure du projet

```
tp-mongo-back/
├── app/
│   ├── routes/              # Routes Flask (films, genres, favoris...)
│   ├── services/            # Logique métier
│   ├── models/              # Modèles MongoDB (si utilisés)
│   ├── extensions.py        # Initialisation Mongo
│   ├── errors/              # Gestion centralisée des erreurs
│   └── __init__.py          # Création de l'application Flask
├── Dockerfile
├── run.py
├── requirements.txt
└── .env.example
```

---

## Lancer l'application en développement

```bash
pip install -r requirements.txt
python run.py
```

> Le backend s’exécutera par défaut sur http://localhost:5000

---

## Lancer avec Docker

```bash
docker build -t tp-mongo-backend .
docker run -p 5000:5000 --env-file .env tp-mongo-backend
```

---

## Routes principales disponibles

### Films (`/films`)
- `GET /` – Liste complète des films
- `GET /<id>` – Détail d’un film
- `GET /cursor` – Pagination par curseur
- `GET /popular`, `/latest`, `/top-rated`, `/hottest`
- `GET /analytics/overview` – Données analytiques (genres appréciés, etc.)
- `GET /recommended` – Recommandations personnalisées
- `GET /new-releases`, `/critically-acclaimed`, `/underrated`, `/nostalgia-90s`, etc.

### Genres (`/genres`)
- `GET /` – Liste des genres
- `GET /popular` – Genres les plus fréquents
- `GET /<genre_name>` – Films populaires par genre

### Favoris (`/favorites`)
- `GET /` – Liste des favoris pour l’utilisateur (via IP)
- `POST /toggle` – Ajoute ou retire un film des favoris

### Acteurs (`/actors`)
- `GET /<id>` – Détails sur un acteur

---

## Variables d’environnement (exemple dans `.env.example`)

```env
DB_URI=mongodb+srv://.../movie-app
SECRET_KEY=xxxxxxxxxx
```

---

## Licence

Projet pédagogique développé dans le cadre d’un exercice universitaire. Utilisation libre à des fins éducatives.
