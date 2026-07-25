import os
import tempfile
import unittest
from pathlib import Path

_TEMP_DIR = tempfile.mkdtemp(prefix="edugenie-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEMP_DIR).as_posix()}/test.db"
os.environ["EDUGENIE_USE_LOCAL_MODEL"] = "0"
# Set explicitly rather than popping: real environment variables take precedence
# over a local .env file, so the suite stays hermetic on a developer machine that
# has a working Gemini key configured.
os.environ["GEMINI_API_KEY"] = ""
os.environ["GOOGLE_API_KEY"] = ""

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.database.models import AiResponse, LearningPath, Quiz, Summary, UserQuery  # noqa: E402
from backend.app.database.session import init_db, session_scope  # noqa: E402
from backend.app.main import app  # noqa: E402


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health_reports_database_and_provider_state(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertTrue(body["database_ready"])
        self.assertFalse(body["gemini_configured"])
        self.assertFalse(body["local_model_enabled"])

    def test_index_page_renders(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("EduGenie", response.text)
        self.assertIn("/static/js/app.js", response.text)

    def test_qa_endpoint_persists_query_and_response(self):
        response = self.client.post("/qa", json={"question": "Which is the largest ocean?"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["answer"])
        self.assertEqual(body["model_used"], "local-fallback")

        with session_scope() as db:
            query = db.get(UserQuery, body["query_id"])
            stored = db.query(AiResponse).filter_by(query_id=body["query_id"]).one()
            self.assertEqual(query.query_type, "qna")
            self.assertEqual(stored.response_text, body["answer"])

    def test_qa_get_variant(self):
        response = self.client.get("/qa", params={"question": "What is a river?"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["answer"])

    def test_explain_endpoint(self):
        response = self.client.post(
            "/explain", json={"topic": "Pythagoras theorem", "audience": "beginner"}
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("Pythagoras theorem", body["explanation"])
        self.assertEqual(body["audience"], "beginner")

    def test_quiz_endpoint_stores_four_options_per_question(self):
        passage = (
            "Photosynthesis is the process by which plants make food using sunlight, "
            "carbon dioxide, and water. Chlorophyll captures light energy. Oxygen is "
            "released as a byproduct."
        )

        response = self.client.post("/quiz", json={"passage": passage, "num_questions": 3})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["questions"]), 3)
        for question in body["questions"]:
            self.assertEqual(len(question["options"]), 4)
            self.assertIn(question["correct_answer"], question["options"])

        with session_scope() as db:
            rows = db.query(Quiz).filter_by(query_id=body["query_id"]).all()
            self.assertEqual(len(rows), 3)
            self.assertTrue(all(row.option_d for row in rows))

    def test_summarize_endpoint_stores_summary_row(self):
        text = (
            "Python is a high-level programming language. It is popular for web "
            "development and data science. Its readable syntax helps beginners. "
            "Practice builds confidence."
        )

        response = self.client.post("/summarize", json={"text": text, "max_sentences": 2})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["summary"])

        with session_scope() as db:
            row = db.query(Summary).filter_by(query_id=body["query_id"]).one()
            self.assertEqual(row.summary_text, body["summary"])
            self.assertEqual(row.original_text, text)

    def test_learning_recommendations_endpoint_stores_path(self):
        response = self.client.post(
            "/learn/recommendations", json={"topic": "SQL", "level": "beginner"}
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        for level in ("Beginner", "Intermediate", "Advanced"):
            self.assertIn(level, body["learning_path"])

        with session_scope() as db:
            row = db.query(LearningPath).filter_by(query_id=body["query_id"]).one()
            self.assertEqual(row.topic, "SQL")
            self.assertEqual(row.difficulty_level, "beginner")

    def test_history_returns_recent_entries(self):
        self.client.post("/qa", json={"question": "What is gravity?"})

        response = self.client.get("/history", params={"limit": 5, "query_type": "qna"})

        self.assertEqual(response.status_code, 200)
        records = response.json()
        self.assertTrue(records)
        self.assertTrue(all(record["query_type"] == "qna" for record in records))
        self.assertTrue(records[0]["response_text"])

    def test_blank_input_is_rejected(self):
        response = self.client.post("/summarize", json={"text": ""})

        self.assertEqual(response.status_code, 422)

    def test_invalid_learning_level_is_rejected(self):
        response = self.client.post(
            "/learn/recommendations", json={"topic": "SQL", "level": "expert"}
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
