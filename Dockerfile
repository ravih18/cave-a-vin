FROM python:3.12-slim

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copier les fichiers de dépendances
COPY pyproject.toml .
COPY uv.lock* .

# Installer les dépendances avec uv (sans venv, directement dans le système)
RUN uv sync --frozen --no-dev

# Copier le code
COPY app/ ./app/

# Dossier data persistant
RUN mkdir -p data

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
