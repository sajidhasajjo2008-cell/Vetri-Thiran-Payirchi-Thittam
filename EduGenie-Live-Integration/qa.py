"""
EduGenie - Question & Answer Module

This module receives a learner's question and uses Gemini
to generate a clear, educational answer.
"""

from ai_client import GeminiClientError, generate_ai_response


def answer_question(question: str) -> str:
    """
    Generate an educational answer for a learner's question.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = f"""
You are EduGenie, an AI-powered educational assistant.

Answer the learner's question clearly and educationally.

Question:
{question.strip()}

Instructions:
- Use simple and clear language.
- Explain the concept properly.
- Give an example when useful.
- Do not use unnecessary technical language.
"""

    try:
        answer = generate_ai_response(
            prompt=prompt,
            temperature=0.4,
            max_output_tokens=1000,
        )

        return answer.strip()

    except GeminiClientError:
        raise
    except Exception as exc:
        raise GeminiClientError(
            f"Failed to generate answer: {exc}"
        ) from exc