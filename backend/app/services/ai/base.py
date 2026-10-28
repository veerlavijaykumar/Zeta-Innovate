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

    def _get_client(self):
        """Lazy-init the Gemini client."""
        if self._client is None:
            if not settings.GEMINI_API_KEY:
                raise RuntimeError(
                    "GEMINI_API_KEY not configured. Set it in your .env file. "
                    "Get a key at https://aistudio.google.com/app/apikey"
                )
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._client = genai.GenerativeModel(settings.GEMINI_MODEL)
        return self._client

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
                await asyncio.sleep(wait_time)
                self._request_count = 1
                self._last_request_time = time.time()

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.3,
        max_retries: int = None,
    ) -> str:
        """Generate text with retry and timeout."""
        max_retries = max_retries or settings.AI_MAX_RETRIES
        await self._rate_limit_check()

        client = self._get_client()

        for attempt in range(max_retries):
            try:
                full_prompt = prompt
                if system_instruction:
                    full_prompt = f"{system_instruction}\n\n{prompt}"

                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.generate_content,
                        full_prompt,
                        generation_config={
                            "temperature": temperature,
                            "max_output_tokens": 8192,
                        },
                    ),
                    timeout=settings.AI_REQUEST_TIMEOUT,
                )

                if response.text:
                    return response.text
                else:
                    logger.warning("Empty AI response", attempt=attempt)
                    continue

            except asyncio.TimeoutError:
                logger.error("AI request timeout", attempt=attempt)
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.error("AI request failed", error=str(e), attempt=attempt)
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError("AI service unavailable after retries")

    async def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Generate and parse JSON response."""
        json_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code blocks, no extra text."

        response = await self.generate(
            json_prompt,
            system_instruction=system_instruction,
            temperature=temperature,
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
