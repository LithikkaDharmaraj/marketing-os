import json
import logging
from typing import Any, Type, TypeVar
from groq import AsyncGroq, APIError, RateLimitError
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from shared.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar("T", bound=BaseModel)

_client: AsyncGroq | None = None


def get_groq_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.groq_api_key)
    return _client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((APIError, RateLimitError)),
)
async def call_groq_structured(
    system_prompt: str,
    user_prompt: str,
    output_schema: Type[T],
    model: str | None = None,
    max_tokens: int | None = None,
) -> T:
    """Call Groq API with structured JSON output, validated against a Pydantic schema."""
    client = get_groq_client()
    chosen_model = model or settings.groq_model_large
    max_tok = max_tokens or settings.groq_max_tokens

    schema_str = json.dumps(output_schema.model_json_schema(), indent=2)
    full_system = (
        f"{system_prompt}\n\n"
        f"CRITICAL: Return ONLY valid JSON matching this exact schema. No explanation, no markdown, no code blocks.\n"
        f"Schema:\n{schema_str}"
    )

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
        return output_schema.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f"First parse failed ({e}), retrying with explicit schema prompt")
        # Second attempt with stricter prompt
        retry_response = await client.chat.completions.create(
            model=settings.groq_model_fast,  # fallback to fast model
            messages=[
                {"role": "system", "content": full_system},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": raw_text},
                {
                    "role": "user",
                    "content": f"The previous response was invalid. Return ONLY valid JSON matching: {schema_str}",
                },
            ],
            max_tokens=max_tok,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        retry_text = retry_response.choices[0].message.content or "{}"
        data = json.loads(retry_text)
        return output_schema.model_validate(data)


async def call_groq_raw(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int = 2048,
) -> tuple[str, dict[str, Any]]:
    """Call Groq and return raw text + usage stats."""
    client = get_groq_client()
    chosen_model = model or settings.groq_model_large

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
