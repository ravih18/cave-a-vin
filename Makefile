.PHONY: dev docker-dev docker-dev-down build up down logs logs-app pull deploy ssl-renew ssl-init install-docker setup help

# ─── Local sans Docker ────────────────────────────────────────────────────────

dev:
	uv run uvicorn app.main:app --reload

# ─── Docker dev (test local avec Docker) ──────────────────────────────────────

docker-dev:
	docker compose -f docker-compose.dev.yml up --build

docker-dev-down:
	docker compose -f docker-compose.dev.yml down

# ─── Docker local ─────────────────────────────────────────────────────────────

build:
	docker compose up -d --build app

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

logs-app:
	docker compose logs -f app

# ─── Production (VPS) ─────────────────────────────────────────────────────────

pull:
	git pull origin main

deploy:
	git pull origin main
	docker compose up -d --build

ssl-renew:
	docker compose run --rm certbot renew
	docker compose restart nginx

# Obtenir le certificat SSL pour la première fois
# À lancer UNE SEULE FOIS après le premier `make up`
ssl-init:
	@echo "⚠️  Assurez-vous que cave.rhassana.net pointe bien vers ce serveur"
	@echo "📋 Lancement de la validation HTTP-01 via certbot..."
	docker compose run --rm certbot certonly \
		--webroot \
		--webroot-path=/var/www/certbot \
		--email admin@rhassana.net \
		--agree-tos \
		--no-eff-email \
		-d cave.rhassana.net
	@echo "✅ Certificat obtenu ! Relancez nginx :"
	@echo "   docker compose restart nginx"

# ─── Installation initiale sur le VPS ────────────────────────────────────────

install-docker:
	apt install -y ca-certificates curl gnupg git ufw make
	install -m 0755 -d /etc/apt/keyrings
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
	chmod a+r /etc/apt/keyrings/docker.asc
	echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $$(. /etc/os-release && echo "$$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
	apt update
	apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
	systemctl enable docker
	systemctl start docker
	@echo "✅ Docker installé avec succès"

setup:
	@echo "📁 Création du dossier data/"
	mkdir -p data
	@echo "⚠️  N'oublie pas de créer ton fichier .env !"
	@echo "   cp .env.example .env && nano .env"
	@echo "✅ Setup terminé"

# ─── Backup ───────────────────────────────────────────────────────────────────

backup:
	docker run --rm \
		-v cave-a-vin_cave-data:/data \
		-v $(shell pwd):/backup \
		alpine tar czf /backup/cave-backup-$$(date +%Y%m%d-%H%M).tar.gz /data
	@echo "✅ Backup créé"

# ─── Aide ─────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "Commandes disponibles :"
	@echo ""
	@echo "  Local :"
	@echo "    make dev              → lancer en local sans Docker (uv)"
	@echo "    make docker-dev       → Docker local avec hot reload"
	@echo "    make docker-dev-down  → arrêter le Docker dev"
	@echo "    make down             → arrêter Docker"
	@echo "    make logs             → voir tous les logs"
	@echo "    make logs-app         → logs de l'app seulement"
	@echo ""
	@echo "  Production :"
	@echo "    make deploy           → git pull + rebuild + restart"
	@echo "    make ssl-init         → obtenir le certificat SSL (1ère fois)"
	@echo "    make ssl-renew        → renouveler le certificat SSL"
	@echo "    make backup           → sauvegarder la base SQLite"
	@echo ""
	@echo "  Installation VPS :"
	@echo "    make install-docker   → installer Docker sur Ubuntu"
	@echo "    make setup            → initialisation après git clone"
	@echo ""
