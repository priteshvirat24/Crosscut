"""OpenAI / GPT-4.1 provider implementation."""

from __future__ import annotations

import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel

from app.llm.provider import LLMProvider

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider using the Chat Completions API."""

    def __init__(self, api_key: str, model: str = "gpt-4.1", **kwargs: Any) -> None:
        super().__init__(api_key, model, **kwargs)
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def structured_output(
        self,
        messages: list[dict[str, str]],
        output_schema: Type[T],
        temperature: float = 0.0,
    ) -> T:
        schema = output_schema.model_json_schema()
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=temperature,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": output_schema.__name__,
                    "schema": schema,
                    "strict": True,
                },
            },
        )
        content = response.choices[0].message.content or "{}"
        return output_schema.model_validate_json(content)
