"""
Gemini Client — Singleton wrapper around Google Generative AI.
Handles model initialization, rate limiting, and fallback.
"""

import asyncio
import logging
from typing import Optional, Union

import google.generativeai as genai

from config import settings

logger = logging.getLogger(__name__)

_model: Optional[genai.GenerativeModel] = None
_vision_model: Optional[genai.GenerativeModel] = None


def get_gemini_model() -> genai.GenerativeModel:
    """Get or initialize the text generation model."""
    global _model
    if _model is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not configured")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel(
            "gemini-1.5-flash-latest",
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                max_output_tokens=4096,
            ),
        )
    return _model


def get_vision_model() -> genai.GenerativeModel:
    """Get or initialize the vision model."""
    global _vision_model
    if _vision_model is None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not configured")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _vision_model = genai.GenerativeModel(
            "gemini-1.5-flash-latest",
            generation_config=genai.GenerationConfig(
                temperature=0.0,
                max_output_tokens=4096,
            ),
        )
    return _vision_model


async def generate_text(prompt: str, system_instruction: str = "") -> str:
    """Generate text using Gemini Flash (non-blocking via to_thread)."""
    model = get_gemini_model()
    try:
        if system_instruction:
            response = await asyncio.to_thread(
                model.generate_content, [system_instruction, prompt]
            )
        else:
            response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini text generation failed: {e}")
        raise


async def generate_with_image(prompt: str, image_bytes: bytes, mime_type: str = "image/png") -> str:
    """Generate text from image + prompt using Gemini Vision (non-blocking)."""
    model = get_vision_model()
    try:
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes,
        }
        response = await asyncio.to_thread(
            model.generate_content, [prompt, image_part]
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
