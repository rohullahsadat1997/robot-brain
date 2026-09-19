import os

from openai import OpenAI

from .base import AIProvider


class OpenAIProvider(AIProvider):

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_response(self, messages):
        print("AI REQUEST: generate_response")
        response = self.client.chat.completions.create(
            model="gpt-5.6-luna",
            messages=messages,
        )

        return response.choices[0].message.content

    def generate_json(self, prompt):
        print("AI REQUEST: generate_json")
        response = self.client.responses.create(
            model="gpt-5.6-luna",
            input=prompt,
        )

        return response.output_text.strip()