"""AI Service base - Gemini API client with retry, timeout, rate limiting."""
import json
import asyncio
import time
from typing import Optional, Any
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class AIService:
    """Base AI service with Gemini API integration."""

    def __init__(self):
        self._client = None
        self._last_request_time = 0
        self._request_count = 0
        self._rate_limit_window = 60  # seconds
        self._rate_limit_max = settings.RATE_LIMIT_AI

    def _get_client(self, model_name: Optional[str] = None):
        """Lazy-init the Gemini client."""
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY not configured. Set it in your .env file. "
                "Get a key at https://aistudio.google.com/app/apikey"
            )
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        chosen_model = model_name or settings.GEMINI_MODEL
        return genai.GenerativeModel(chosen_model)

    async def _rate_limit_check(self):
        """Simple rate limiting."""
        now = time.time()
        if now - self._last_request_time > self._rate_limit_window:
            self._request_count = 0
            self._last_request_time = now

        self._request_count += 1
        if self._request_count > self._rate_limit_max:
            wait_time = self._rate_limit_window - (now - self._last_request_time)
            if wait_time > 0:
                logger.warning("Rate limit reached, waiting", wait_seconds=wait_time)
                await asyncio.sleep(min(wait_time, 2.0))
                self._request_count = 1
                self._last_request_time = time.time()

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        max_retries: int = 2,
    ) -> str:
        """Generate text with fast fallback across available models and token limits."""
        await self._rate_limit_check()

        # Build prioritized list of models to try
        candidates = [settings.GEMINI_MODEL, "gemini-3.1-flash-lite", "gemini-flash-latest", "gemini-2.5-flash"]
        seen = set()
        models_to_try = [m for m in candidates if m and not (m in seen or seen.add(m))]

        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"

        last_error = None
        for model_name in models_to_try:
            try:
                client = self._get_client(model_name)
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.generate_content,
                        full_prompt,
                        generation_config={
                            "temperature": temperature,
                            "max_output_tokens": max_tokens,
                        },
                    ),
                    timeout=25,
                )

                if response.text and response.text.strip():
                    return response.text
                else:
                    logger.warning("Empty AI response", model=model_name)
            except Exception as e:
                err_str = str(e)
                last_error = e
                logger.warning("AI model failed, attempting next available model", model=model_name, error=err_str[:120])
                # If quota exhausted (429) or model deprecated (404), immediately try next model without sleep
                continue

        raise RuntimeError(f"All AI models exhausted: {str(last_error)}")

    async def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        """Generate and parse JSON response."""
        json_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown explanation, no conversational filler."

        response = await self.generate(
            json_prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Clean potential markdown code blocks
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI JSON response", error=str(e), response=text[:500])
            raise ValueError(f"AI returned invalid JSON: {str(e)}")

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate text embedding."""
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not configured")

        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)

        result = await asyncio.to_thread(
            genai.embed_content,
            model=settings.GEMINI_EMBEDDING_MODEL,
            content=text,
        )
        return result["embedding"]
