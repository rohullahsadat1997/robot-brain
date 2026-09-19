import os
import time

from google import genai

from .base import AIProvider


class GeminiProvider(AIProvider):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=api_key)

    def generate_response(self, messages):
        prompt_start = time.perf_counter()

        prompt = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        print(
            "PROMPT BUILD TIME:",
            time.perf_counter() - prompt_start
        )

        ai_start = time.perf_counter()

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        print(
            "GEMINI REQUEST TIME:",
            time.perf_counter() - ai_start
        )

        return response.text

    def generate_json(self, prompt):
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        return response.text.strip()