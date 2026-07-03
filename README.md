# EduGenie

EduGenie is an AI-powered educational assistant designed to help learners with
question answering, concept explanation, quiz generation, text summarization,
and personalized learning recommendations.

The project is planned around a FastAPI backend, HTML/CSS frontend, Google
Gemini integration, and an optional local LaMini-Flan-T5 explanation model.

## Project Structure

```text
EduGenie/
├── backend/
│   └── app/
│       ├── ai_modules/
│       │   └── features/
│       ├── api/
│       ├── core/
│       ├── database/
│       ├── schemas/
│       └── services/
├── frontend/
│   ├── templates/
│   └── static/
│       ├── assets/
│       ├── css/
│       └── js/
├── database/
│   └── migrations/
├── deployment/
├── docs/
│   └── project/
├── scripts/
├── tests/
│   └── ai_features/
├── .env.example
├── .gitignore
└── README.md
```

## Implemented AI Features

The implemented AI modules are available in:

```text
backend/app/ai_modules/features/
```

Included modules:

- Question answering
- Concept explanation
- Quiz generation
- Text summarization
- Learning path recommendations

The modules can use Gemini or LaMini-Flan-T5 when configured. They also include
local fallback behavior so development and tests can run without API keys.

## Environment Variables

Copy `.env.example` to `.env` and add local values:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-pro
GOOGLE_API_KEY=
LAMINI_MODEL=MBZUAI/LaMini-Flan-T5-783M
EDUGENIE_USE_LOCAL_MODEL=1
```

Do not commit real API keys.

## Run Tests

```bash
python -B -m unittest discover -s tests
```

## Notes

Some project folders are intentionally empty so other contributors can add their
assigned backend, frontend, database, deployment, and integration code.
