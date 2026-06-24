"""Google / Gemini provider implementation."""

from __future__ import annotations

import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel

from app.llm.provider import LLMProvider

T = TypeVar("T", bound=BaseModel)


class GoogleProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(
        self, api_key: str, model: str = "gemini-2.5-pro", **kwargs: Any
    ) -> None:
        super().__init__(api_key, model, **kwargs)
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self.genai = genai
        self._model = genai.GenerativeModel(model)

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        # Combine messages into a single prompt for Gemini
        parts = []
        for msg in messages:
            prefix = "System: " if msg["role"] == "system" else "User: "
            parts.append(f"{prefix}{msg['content']}")

        prompt = "\n\n".join(parts)

        response = await self._model.generate_content_async(
            prompt,
            generation_config=self.genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text or ""

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

        modified_messages = messages.copy()
        if modified_messages and modified_messages[-1]["role"] == "user":
            modified_messages[-1] = {
                "role": "user",
                "content": modified_messages[-1]["content"] + prompt_suffix,
            }

        response = await self.chat(modified_messages, temperature=temperature)

        try:
            return output_schema.model_validate_json(response)
        except Exception:
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return output_schema.model_validate_json(json_match.group())
            raise
