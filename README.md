# mvola-service

Microservice FastAPI autonome pour gérer les transactions Mvola.

## Démarrage rapide
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # puis remplir les variables
uvicorn app.main:app --reload
```

## Endpoints (prefixe `/api/v1/mvola`)
- `POST /create` : initier une transaction
- `POST /update/{id}` : mettre à jour `transactionReference`
- `GET /status/{serverCorrelationId}?id_mv_transaction=<id>` : statut
- `GET /details/{transactionReference}` : détails
- `GET /user/{user_id}` : transactions d'un utilisateur

## Conteneur
```bash
docker build -t mvola-service .
docker run -p 8000:8000 --env-file .env mvola-service
```

## Docker Compose (PostgreSQL + API)
```bash
cp .env.example .env   # vérifier DATABASE_URL/creds
docker compose up --build
# API sur http://localhost:8000, Postgres sur port local 5433
```
