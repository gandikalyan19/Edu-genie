# Deployment

## Local (Uvicorn)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The app is served at http://127.0.0.1:8000 with interactive API docs at `/docs`.

## Docker

```bash
docker compose -f deployment/docker-compose.yml up --build
```

SQLite data persists in the `edugenie-data` volume. Set `DATABASE_URL` to a
PostgreSQL DSN (for example `postgresql+psycopg://user:pass@host/edugenie`) to
use a managed database instead; apply `database/migrations/001_initial_schema.sql`
when the database is not created by the application on startup.
