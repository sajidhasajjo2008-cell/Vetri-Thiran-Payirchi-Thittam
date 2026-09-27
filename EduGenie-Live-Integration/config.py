import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# Application settings
# ---------------------------------------------------------

APP_NAME = os.getenv(
    "APP_NAME",
    "EduGenie - AI Powered Learning Assistant"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

DEBUG = os.getenv(
    "DEBUG",
    "true"
).lower() == "true"


# ---------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# ---------------------------------------------------------
# Local explanation model configuration
# ---------------------------------------------------------

EXPLANATION_MODEL = os.getenv(
    "EXPLANATION_MODEL",
    "MBZUAI/LaMini-Flan-T5-248M"
)


# ---------------------------------------------------------
# Server configuration
# ---------------------------------------------------------

HOST = os.getenv(
    "HOST",
    "127.0.0.1"
)

PORT = int(
    os.getenv(
        "PORT",
        "8000"
    )
)


# ---------------------------------------------------------
# AI generation settings
# ---------------------------------------------------------

DEFAULT_TEMPERATURE = float(
    os.getenv(
        "DEFAULT_TEMPERATURE",
        "0.4"
    )
)

DEFAULT_MAX_OUTPUT_TOKENS = int(
    os.getenv(
        "DEFAULT_MAX_OUTPUT_TOKENS",
        "2048"
    )
)


# ---------------------------------------------------------
# Validation helper
# ---------------------------------------------------------

def validate_settings() -> None:
    """
    Validate important project configuration.

    The Gemini API key is required only when an endpoint
    needs Gemini. This allows the application to start
    before the key is configured.
    """

    if not GEMINI_API_KEY:
        print(
            "WARNING: GEMINI_API_KEY is not configured. "
            "Gemini-powered modules will not work until "
            "the API key is added to the .env file."
        )


# ---------------------------------------------------------
# Display configuration
# ---------------------------------------------------------

def get_settings_summary() -> dict:
    """
    Return safe application settings.

    The actual Gemini API key is intentionally never returned.
    """

    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "debug": DEBUG,
        "gemini_configured": bool(GEMINI_API_KEY),
        "gemini_model": GEMINI_MODEL,
        "explanation_model": EXPLANATION_MODEL,
        "host": HOST,
        "port": PORT,
        "temperature": DEFAULT_TEMPERATURE,
        "max_output_tokens": DEFAULT_MAX_OUTPUT_TOKENS,
    }


validate_settings()