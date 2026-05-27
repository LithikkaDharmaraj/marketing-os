import json
import logging
from typing import Any, Type, TypeVar
from groq import AsyncGroq, APIError, RateLimitError, APIConnectionError as GroqConnectionError
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from shared.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar("T", bound=BaseModel)

_groq_client: AsyncGroq | None = None
_openai_client = None


def get_groq_client() -> AsyncGroq:
    global _groq_client
    if _groq_client is None:
        _groq_client = AsyncGroq(api_key=settings.groq_api_key)
    return _groq_client


def get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import AsyncOpenAI
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


async def _call_openai_structured(
    system_prompt: str,
    user_prompt: str,
    output_schema: Type[T],
    max_tokens: int,
) -> T:
    """OpenAI fallback for structured JSON extraction."""
    client = get_openai_client()
    schema_str = json.dumps(output_schema.model_json_schema(), indent=2)
    full_system = (
        f"{system_prompt}\n\n"
        f"CRITICAL: Return ONLY valid JSON matching this exact schema. No explanation, no markdown, no code blocks.\n"
        f"Schema:\n{schema_str}"
    )
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)
    if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
        data = data[0]
    return output_schema.model_validate(data)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(APIError),
)
async def call_groq_structured(
    system_prompt: str,
    user_prompt: str,
    output_schema: Type[T],
    model: str | None = None,
    max_tokens: int | None = None,
) -> T:
    """Call Groq with structured JSON output. Falls back to OpenAI on rate limit."""
    chosen_model = model or settings.groq_model_large
    max_tok = max_tokens or settings.groq_max_tokens

    schema_str = json.dumps(output_schema.model_json_schema(), indent=2)
    full_system = (
        f"{system_prompt}\n\n"
        f"CRITICAL: Return ONLY valid JSON matching this exact schema. No explanation, no markdown, no code blocks.\n"
        f"Schema:\n{schema_str}"
    )

    try:
        client = get_groq_client()
        response = await client.chat.completions.create(
            model=chosen_model,
            messages=[
                {"role": "system", "content": full_system},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tok,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw_text = response.choices[0].message.content or "{}"

        try:
            data = json.loads(raw_text)
            if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
                data = data[0]
            return output_schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Groq parse failed ({e}), retrying with fast model")
            retry_response = await client.chat.completions.create(
                model=settings.groq_model_fast,
                messages=[
                    {"role": "system", "content": full_system},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": raw_text},
                    {"role": "user", "content": f"The previous response was invalid. Return ONLY valid JSON matching: {schema_str}"},
                ],
                max_tokens=max_tok,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            data = json.loads(retry_response.choices[0].message.content or "{}")
            return output_schema.model_validate(data)

    except (RateLimitError, GroqConnectionError) as e:
        if not settings.openai_api_key:
            logger.error("Groq unavailable and no OpenAI API key configured — failing")
            raise
        logger.warning(f"Groq unavailable ({type(e).__name__}), falling back to OpenAI {settings.openai_model}")
        return await _call_openai_structured(system_prompt, user_prompt, output_schema, max_tok)


async def call_groq_raw(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int = 2048,
) -> tuple[str, dict[str, Any]]:
    """Call Groq and return raw text + usage stats. Falls back to OpenAI on rate limit."""
    chosen_model = model or settings.groq_model_large

    try:
        client = get_groq_client()
        response = await client.chat.completions.create(
            model=chosen_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        }
        return response.choices[0].message.content or "", usage

    except (RateLimitError, GroqConnectionError) as e:
        if not settings.openai_api_key:
            raise
        logger.warning(f"Groq unavailable ({type(e).__name__}), falling back to OpenAI for raw call")
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        }
        return response.choices[0].message.content or "", usage
