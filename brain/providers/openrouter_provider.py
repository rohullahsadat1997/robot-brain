import os

from openai import OpenAI

from .base import AIProvider


class OpenRouterProvider(AIProvider):

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def generate_response(self, messages):
        response = self.client.chat.completions.create(
     model="openrouter/free",
            messages=messages,
        )

        return response.choices[0].message.content

    def generate_json(self, prompt):
        response = self.client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content.strip()