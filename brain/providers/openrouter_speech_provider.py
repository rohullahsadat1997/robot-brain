import base64
import os
import requests

from .speech_base import SpeechToTextProvider


class OpenRouterSpeechProvider(SpeechToTextProvider):

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

    def transcribe(self, audio_file):
        with open(audio_file, "rb") as file:
            audio_data = base64.b64encode(
                file.read()
            ).decode("utf-8")

        response = requests.post(
            "https://openrouter.ai/api/v1/audio/transcriptions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/whisper-1",
                "input_audio": {
                    "data": audio_data,
                    "format": "wav",
                },
                "language": "fa",
            },
            timeout=60,
        )

        response.raise_for_status()

        return response.json()["text"]
    