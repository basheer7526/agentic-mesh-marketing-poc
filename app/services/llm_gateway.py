from typing import Any, Type

from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.config.settings import settings


class LLMGateway:

    def __init__(self) -> None:

        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0,
        )

    def invoke(self, prompt: str) -> Any:
        return self.llm.invoke(prompt)

    def structured(self, schema: Type[BaseModel]):
        return self.llm.with_structured_output(
            schema,
            method="json_mode",
        )


llm_gateway = LLMGateway()