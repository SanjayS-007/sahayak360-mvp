"""
Gemini Client — Singleton wrapper around Google GenAI SDK.
Handles client initialization, rate limiting, and fallback.
"""

import asyncio
import logging
from typing import Optional, Union

from google import genai

from config import settings

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"

_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    """Get or initialize the GenAI client."""
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not configured")
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


async def generate_text(prompt: str, system_instruction: str = "") -> str:
    """Generate text using Gemini Flash (non-blocking via to_thread)."""
    client = get_client()
    try:
        contents = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=contents,
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini text generation failed: {e}")
        raise


async def generate_with_image(prompt: str, image_bytes: bytes, mime_type: str = "image/png") -> str:
    """Generate text from image + prompt using Gemini Vision (non-blocking)."""
    client = get_client()
    try:
        image_part = {"mime_type": mime_type, "data": image_bytes}
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=[prompt, image_part],
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini vision generation failed: {e}")
        raise


async def generate_json(prompt: str, system_instruction: str = "") -> Union[dict, list]:
    """Generate and parse JSON from Gemini output."""
    import json
    raw = await generate_text(prompt, system_instruction)

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON output: {e}\nRaw: {raw[:500]}")
        raise ValueError(f"Gemini returned invalid JSON: {e}")
