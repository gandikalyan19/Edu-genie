# EduGenie

EduGenie is an AI-powered educational assistant that helps learners with question
answering, concept explanation, quiz generation, text summarization, and
personalized learning recommendations.

It is built with a FastAPI backend, an HTML/CSS/JavaScript frontend served through
Jinja2, SQLAlchemy persistence, Google Gemini integration, and an optional local
LaMini-Flan-T5 explanation model. Every feature has a deterministic local fallback,
so the whole application runs without any API key.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env          # optional: add your Gemini key
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 for the web interface and http://127.0.0.1:8000/docs
for the interactive API documentation. Tables are created automatically on startup.

## API Endpoints

| Method     | Path                     | Purpose                              |
| ---------- | ------------------------ | ------------------------------------ |
| POST / GET | `/qa`                    | Educational question answering       |
| POST       | `/explain`               | Simplified concept explanation       |
| POST       | `/quiz`                  | MCQ quiz generation (1-5 questions)  |
| POST       | `/summarize`             | Educational text summarization       |
| POST / GET | `/learn/recommendations` | Personalized learning path           |
| GET        | `/history`               | Recent queries and their AI responses |
| GET        | `/health`                | Service, database, and model status  |

Example:

```bash
curl -X POST http://127.0.0.1:8000/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "Which is the largest ocean?"}'
```

Every request is stored as a `USER_QUERY` with its `AI_RESPONSE`, plus a
feature-specific record in `QUIZ`, `SUMMARY`, or `LEARNING_PATH`. The
`model_used` field records whether Gemini, LaMini-Flan-T5, or the local fallback
produced the response.

## Model Selection

Question answering, quiz generation, summarization, and learning paths use
Gemini. Concept explanation prefers the local LaMini-Flan-T5 model, falls back to
Gemini when `transformers` is not installed, and finally to deterministic local
text. Watch the `model_used` field to see which path served a response.

`gemini-1.5-pro` has been retired by Google and now returns HTTP 404. Set
`GEMINI_MODEL=gemini-flash-latest` instead. Some accounts also see HTTP 429 on
`gemini-2.5-pro` and `gemini-2.0-flash`; when a provider call fails for any
reason the application degrades to fallback text rather than returning an error.

## Screenshots

Functional walkthrough of each feature in the running application:

| Feature | Screenshot |
| --- | --- |
| Question answering | [ask_question.png](docs/screenshots/ask_question.png) |
| Concept explanation | [explain_concept.png](docs/screenshots/explain_concept.png) |
| Quiz generation | [generate_quiz.png](docs/screenshots/generate_quiz.png) |
| Text summarization | [summarize.png](docs/screenshots/summarize.png) |
| Learning recommendations | [learning_path.png](docs/screenshots/learning_path.png) |
| Stored activity and model used | [history.png](docs/screenshots/history.png) |

## Project Structure

```text
EduGenie/
├── main.py                     # uvicorn main:app entrypoint
├── backend/app/
│   ├── main.py                 # FastAPI app, static mount, templates
│   ├── ai_modules/features/    # QnA, explanation, quiz, summary, learning path
│   ├── api/routes.py           # REST endpoints
│   ├── core/config.py          # Settings loaded from .env
│   ├── database/               # ORM models and session management
│   ├── schemas/                # Pydantic request/response models
│   └── services/               # Feature orchestration and persistence
├── frontend/
│   ├── templates/index.html
│   └── static/{css,js}/
├── database/migrations/        # Reference SQL DDL
├── deployment/                 # Dockerfile, compose, deployment notes
├── scripts/                    # init_db, run_dev helpers
└── tests/                      # AI module and API tests
```

## Database

The ER design has six entities: `USER`, `USER_QUERY`, `AI_RESPONSE`, `QUIZ`,
`SUMMARY`, and `LEARNING_PATH`. One user has many queries, each query has one AI
response, and a query may produce many quizzes, summaries, or learning paths.

SQLite is the default. Point `DATABASE_URL` at PostgreSQL for a shared deployment
and apply `database/migrations/001_initial_schema.sql` if tables are managed
outside the application.

```bash
python -m scripts.init_db      # create tables explicitly
```

## Environment Variables

Copy `.env.example` to `.env` and add local values. Without `GEMINI_API_KEY` the
application serves local fallback content instead of failing. Set
`EDUGENIE_USE_LOCAL_MODEL=0` to skip loading LaMini-Flan-T5.

Do not commit real API keys.

## Run Tests

```bash
python -B -m unittest discover -s tests
```

## Deployment

See [deployment/README.md](deployment/README.md) for local Uvicorn and Docker
instructions.
