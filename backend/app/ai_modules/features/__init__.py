"""EduGenie AI feature modules."""

from .explanation_module import explain_concept
from .learning_path import get_learning_recommendations
from .qna import answer_question
from .quiz_module import generate_quiz
from .summary_module import summarize_text

__all__ = [
    "answer_question",
    "explain_concept",
    "generate_quiz",
    "get_learning_recommendations",
    "summarize_text",
]
