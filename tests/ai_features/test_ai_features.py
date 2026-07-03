import json
import unittest
from unittest.mock import patch

from backend.app.ai_modules.features import (
    answer_question,
    explain_concept,
    generate_quiz,
    get_learning_recommendations,
    summarize_text,
)
from backend.app.ai_modules.features.quiz_module import _parse_quiz
from backend.app.ai_modules.features.text_utils import clean_json_block


class AiFeatureTests(unittest.TestCase):
    def test_qna_returns_local_answer_without_provider(self):
        with patch("backend.app.ai_modules.features.qna.generate_with_gemini", return_value=None):
            answer = answer_question("Which is the largest ocean?")

        self.assertIn("ocean", answer.lower())
        self.assertGreater(len(answer), 40)

    def test_explanation_returns_beginner_friendly_text(self):
        with patch("backend.app.ai_modules.features.explanation_module._generate_with_lamini", return_value=None):
            explanation = explain_concept("Pythagoras theorem")

        self.assertIn("Pythagoras theorem", explanation)
        self.assertIn("beginner", explanation)

    def test_summary_keeps_first_and_last_ideas(self):
        text = (
            "Python is a high-level programming language. "
            "It is popular for web development and data science. "
            "Its readable syntax helps beginners learn programming. "
            "Practice is important for building confidence."
        )

        summary = summarize_text(text, max_sentences=2)

        self.assertIn("Python is a high-level programming language.", summary)
        self.assertIn("Practice is important", summary)

    def test_quiz_generates_three_questions_with_four_options(self):
        passage = (
            "Photosynthesis is the process by which plants make food using "
            "sunlight, carbon dioxide, and water. Chlorophyll helps capture "
            "light energy. Oxygen is released as a byproduct."
        )

        with patch("backend.app.ai_modules.features.quiz_module.generate_with_gemini", return_value=None):
            quiz = generate_quiz(passage)

        self.assertEqual(len(quiz), 3)
        for question in quiz:
            self.assertIn("question", question)
            self.assertEqual(len(question["options"]), 4)
            self.assertIn("correct_answer", question)

    def test_quiz_parser_accepts_markdown_json_block(self):
        payload = [
            {
                "question": "What does SQL manage?",
                "options": ["Databases", "Weather", "Music", "Images"],
                "correct_answer": "Databases",
            }
        ]
        response = "```json\n" + json.dumps(payload) + "\n```"

        parsed = _parse_quiz(response)

        self.assertEqual(parsed, payload)
        self.assertEqual(clean_json_block(response), json.dumps(payload))

    def test_learning_path_includes_all_levels(self):
        with patch("backend.app.ai_modules.features.learning_path.generate_with_gemini", return_value=None):
            path = get_learning_recommendations("SQL")

        self.assertIn("Beginner", path)
        self.assertIn("Intermediate", path)
        self.assertIn("Advanced", path)

    def test_empty_input_validation(self):
        with self.assertRaises(ValueError):
            summarize_text("")


if __name__ == "__main__":
    unittest.main()
