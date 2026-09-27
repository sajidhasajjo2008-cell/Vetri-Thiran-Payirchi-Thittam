"""
EduGenie - Quiz Generation Module

This module generates multiple-choice questions from a
learning passage using Gemini.

Expected quiz structure:
- 3 questions by default
- 4 options per question
- One correct answer
- Explanation for each answer
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from ai_client import GeminiClientError, generate_ai_json


# =========================================================
# Constants
# =========================================================

DEFAULT_QUESTION_COUNT = 3
MIN_QUESTION_COUNT = 1
MAX_QUESTION_COUNT = 10


# =========================================================
# Prompt builder
# =========================================================

def build_quiz_prompt(
    passage: str,
    number_of_questions: int = DEFAULT_QUESTION_COUNT,
) -> str:
    """
    Build a structured prompt for Gemini quiz generation.
    """

    return f"""
You are EduGenie, an AI-powered educational assistant.

Create a multiple-choice quiz from the learning passage below.

Learning passage:
----------------
{passage}
----------------

Number of questions:
{number_of_questions}

Rules:

1. Generate exactly {number_of_questions} questions.
2. Each question must have exactly 4 options.
3. Every question must have exactly one correct answer.
4. Questions must be based only on the supplied passage.
5. Avoid questions that require information not present in the passage.
6. Use clear language appropriate for students.
7. Avoid duplicate questions.
8. Include a short explanation for the correct answer.
9. The answer must exactly match one of the four options.
10. Return ONLY valid JSON.
11. Do not use Markdown.
12. Do not put the JSON inside ```json or ``` blocks.

Required JSON structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A",
      "explanation": "Why this answer is correct."
    }}
  ]
}}
""".strip()


# =========================================================
# JSON cleaning
# =========================================================

def clean_json_response(response_text: str) -> str:
    """
    Remove common Markdown formatting from an AI response.
    """

    if not response_text:
        raise ValueError(
            "Gemini returned an empty quiz response."
        )

    cleaned = response_text.strip()

    # Remove ```json ... ```
    cleaned = re.sub(
        r"^```json\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"^```\s*",
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    return cleaned.strip()


# =========================================================
# JSON parsing
# =========================================================

def parse_quiz_json(response_text: str) -> Dict[str, Any]:
    """
    Convert Gemini's JSON response into a Python dictionary.
    """

    cleaned = clean_json_response(response_text)

    try:

        data = json.loads(cleaned)

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Quiz response must be a JSON object."
        )

    if "questions" not in data:
        raise ValueError(
            "Quiz response does not contain 'questions'."
        )

    if not isinstance(data["questions"], list):
        raise ValueError(
            "'questions' must be a list."
        )

    return data


# =========================================================
# Validate individual question
# =========================================================

def validate_question(
    question: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate and normalize one quiz question.
    """

    if not isinstance(question, dict):
        raise ValueError(
            "Each quiz question must be an object."
        )

    required_fields = [
        "question",
        "options",
        "answer",
        "explanation",
    ]

    for field in required_fields:

        if field not in question:
            raise ValueError(
                f"Quiz question is missing '{field}'."
            )

    question_text = str(
        question["question"]
    ).strip()

    options = question["options"]

    answer = str(
        question["answer"]
    ).strip()

    explanation = str(
        question["explanation"]
    ).strip()

    if not question_text:
        raise ValueError(
            "Quiz question text cannot be empty."
        )

    if not isinstance(options, list):
        raise ValueError(
            "Quiz options must be a list."
        )

    if len(options) != 4:
        raise ValueError(
            "Each quiz question must contain exactly 4 options."
        )

    cleaned_options = [
        str(option).strip()
        for option in options
    ]

    if any(
        not option
        for option in cleaned_options
    ):
        raise ValueError(
            "Quiz options cannot be empty."
        )

    # Remove duplicate options while preserving order.
    if len(set(cleaned_options)) != 4:
        raise ValueError(
            "Quiz options must be unique."
        )

    if answer not in cleaned_options:
        raise ValueError(
            "The correct answer must exactly match "
            "one of the options."
        )

    return {
        "question": question_text,
        "options": cleaned_options,
        "answer": answer,
        "explanation": explanation,
    }


# =========================================================
# Validate complete quiz
# =========================================================

def validate_quiz(
    data: Dict[str, Any],
    expected_count: int,
) -> List[Dict[str, Any]]:
    """
    Validate the complete quiz.
    """

    questions = data["questions"]

    if len(questions) != expected_count:
        raise ValueError(
            f"Expected {expected_count} questions, "
            f"but received {len(questions)}."
        )

    validated_questions = []

    for question in questions:

        validated_question = validate_question(
            question
        )

        validated_questions.append(
            validated_question
        )

    return validated_questions


# =========================================================
# Generate quiz
# =========================================================

def generate_quiz(
    passage: str,
    number_of_questions: int = DEFAULT_QUESTION_COUNT,
) -> List[Dict[str, Any]]:
    """
    Generate and validate a multiple-choice quiz.
    """

    if not passage or not passage.strip():
        raise ValueError(
            "Passage cannot be empty."
        )

    if (
        number_of_questions < MIN_QUESTION_COUNT
        or number_of_questions > MAX_QUESTION_COUNT
    ):
        raise ValueError(
            f"Number of questions must be between "
            f"{MIN_QUESTION_COUNT} and "
            f"{MAX_QUESTION_COUNT}."
        )

    cleaned_passage = passage.strip()

    prompt = build_quiz_prompt(
        passage=cleaned_passage,
        number_of_questions=number_of_questions,
    )

    response = generate_ai_json(
        prompt=prompt,
        temperature=0.3,
        max_output_tokens=2500,
    )

    data = parse_quiz_json(
        response
    )

    questions = validate_quiz(
        data=data,
        expected_count=number_of_questions,
    )

    return questions


# =========================================================
# Safe API helper
# =========================================================

def generate_quiz_safe(
    passage: str,
    number_of_questions: int = DEFAULT_QUESTION_COUNT,
) -> dict:
    """
    Safe wrapper for the FastAPI layer.
    """

    try:

        questions = generate_quiz(
            passage=passage,
            number_of_questions=number_of_questions,
        )

        return {
            "success": True,
            "questions": questions,
            "error": None,
        }

    except ValueError as exc:

        return {
            "success": False,
            "questions": [],
            "error": str(exc),
        }

    except GeminiClientError as exc:

        return {
            "success": False,
            "questions": [],
            "error": str(exc),
        }

    except Exception as exc:

        return {
            "success": False,
            "questions": [],
            "error": f"Unexpected error: {exc}",
        }