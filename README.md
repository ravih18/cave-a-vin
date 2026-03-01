# 🍷 Cave à Vin

Application de gestion de cave à vin — FastAPI + SQLite + Docker.

## Structure

```
cave-a-vin/
├── app/
│   ├── main.py          ← FastAPI (routes + logique)
│   ├── models.py        ← SQLAlchemy ORM
│   ├── database.py      ← Connexion SQLite
│   └── templates/
│       └── index.html   ← Frontend (Jinja2 + JS vanilla)
├── nginx/
│   └── cave.rhassana.net.conf
├── data/                ← SQLite (gitignored, volume Docker)
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── docker-compose.dev.yml
├── pyproject.toml       ← dépendances uv
├── Makefile
└── .env.example
```

## Démarrage rapide

```bash
# 1. Cloner et configurer
git clone <repo> cave-a-vin && cd cave-a-vin
make setup                    # crée data/
cp .env.example .env && nano .env   # définir PIN_CODE

# 2. Dev local (sans Docker)
make dev

# 3. Dev local avec Docker
make docker-dev

# 4. Production (VPS)
make up                       # démarre tout
make ssl-init                 # certificat SSL (1ère fois)
docker compose restart nginx  # applique le SSL
```

## Premier déploiement sur le VPS

```bash
# Sur le VPS, après git clone :
make setup
cp .env.example .env && nano .env

# Démarrer en HTTP d'abord (pour la validation certbot)
make up

# Obtenir le certificat SSL
make ssl-init

# Redémarrer nginx avec SSL
docker compose restart nginx
```

## Mises à jour

```bash
make deploy   # git pull + rebuild + restart
```

## Backup

```bash
make backup   # crée cave-backup-YYYYMMDD-HHMM.tar.gz
```
