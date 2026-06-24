"""Anthropic / Claude provider implementation."""

from __future__ import annotations

import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel

from app.llm.provider import LLMProvider

T = TypeVar("T", bound=BaseModel)


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider using the Messages API."""

    def __init__(
        self, api_key: str, model: str = "claude-sonnet-4-20250514", **kwargs: Any
    ) -> None:
        super().__init__(api_key, model, **kwargs)
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(api_key=api_key)

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        # Separate system message
        system = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)

        response = await self.client.messages.create(
            model=self.model,
            system=system,
            messages=user_messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content[0].text

    async def structured_output(
        self,
        messages: list[dict[str, str]],
        output_schema: Type[T],
        temperature: float = 0.0,
    ) -> T:
        schema = output_schema.model_json_schema()
        prompt_suffix = (
            f"\n\nRespond ONLY with valid JSON conforming to this schema:\n"
            f"{json.dumps(schema, indent=2)}"
        )

        # Append schema instructions to the last user message
        modified_messages = messages.copy()
        if modified_messages and modified_messages[-1]["role"] == "user":
            modified_messages[-1] = {
                "role": "user",
                "content": modified_messages[-1]["content"] + prompt_suffix,
            }

        response = await self.chat(modified_messages, temperature=temperature)

        # Extract JSON from response
        try:
            # Try direct parse
            return output_schema.model_validate_json(response)
        except Exception:
            # Try to find JSON block
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return output_schema.model_validate_json(json_match.group())
            raise
