"""
EduGenie AI Client

This module provides a single reusable interface for communicating
with Google's Gemini API.

Other EduGenie modules such as:
    - Q&A
    - Quiz
    - Summarization
    - Learning Path

can call the functions in this file instead of creating their own
Gemini clients.
"""

from __future__ import annotations

from typing import Optional

from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS,
)


class GeminiClientError(Exception):
    """Custom exception for Gemini-related errors."""

    pass


class GeminiAIClient:
    """
    Reusable Gemini AI client for the EduGenie application.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:

        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL

        if not self.api_key:
            self.client = None
            return

        try:
            self.client = genai.Client(
                api_key=self.api_key
            )
        except Exception as exc:
            self.client = None

            raise GeminiClientError(
                f"Unable to initialize Gemini client: {exc}"
            ) from exc

    # ---------------------------------------------------------
    # Check whether Gemini is configured
    # ---------------------------------------------------------

    def is_configured(self) -> bool:
        """
        Returns True if a Gemini API key is available.
        """

        return self.client is not None

    # ---------------------------------------------------------
    # Generate text
    # ---------------------------------------------------------

    def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a prompt to Gemini and return generated text.
        """

        if not prompt or not prompt.strip():
            raise GeminiClientError(
                "Prompt cannot be empty."
            )

        if not self.client:
            raise GeminiClientError(
                "Gemini API is not configured. "
                "Please add GEMINI_API_KEY to the .env file."
            )

        temperature = (
            DEFAULT_TEMPERATURE
            if temperature is None
            else temperature
        )

        max_output_tokens = (
            DEFAULT_MAX_OUTPUT_TOKENS
            if max_output_tokens is None
            else max_output_tokens
        )

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )

        except Exception as exc:

            raise GeminiClientError(
                f"Gemini generation failed: {exc}"
            ) from exc

        text = getattr(response, "text", None)

        if not text:
            raise GeminiClientError(
                "Gemini returned an empty response."
            )

        return text.strip()

    # ---------------------------------------------------------
    # Generate structured JSON
    # ---------------------------------------------------------

    def generate_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ) -> str:
        """
        Ask Gemini to return JSON.

        The actual JSON validation will be performed by the
        individual application modules using Pydantic.
        """

        if not prompt or not prompt.strip():
            raise GeminiClientError(
                "Prompt cannot be empty."
            )

        if not self.client:
            raise GeminiClientError(
                "Gemini API is not configured. "
                "Please add GEMINI_API_KEY to the .env file."
            )

        temperature = (
            DEFAULT_TEMPERATURE
            if temperature is None
            else temperature
        )

        max_output_tokens = (
            DEFAULT_MAX_OUTPUT_TOKENS
            if max_output_tokens is None
            else max_output_tokens
        )

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                ),
            )

        except Exception as exc:

            raise GeminiClientError(
                f"Gemini JSON generation failed: {exc}"
            ) from exc

        text = getattr(response, "text", None)

        if not text:
            raise GeminiClientError(
                "Gemini returned an empty JSON response."
            )

        return text.strip()


# -------------------------------------------------------------
# Shared application-level Gemini client
# -------------------------------------------------------------

gemini_client = GeminiAIClient()


# -------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------

def generate_ai_response(
    prompt: str,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Convenience function used by EduGenie modules.
    """

    return gemini_client.generate_text(
        prompt=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )


def generate_ai_json(
    prompt: str,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Convenience function for JSON-based AI responses.
    """

    return gemini_client.generate_json(
        prompt=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )