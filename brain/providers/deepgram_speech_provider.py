import os
import requests

from .speech_base import SpeechToTextProvider


class DeepgramSpeechProvider(SpeechToTextProvider):

    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")

        if not self.api_key:
            raise ValueError(
                "DEEPGRAM_API_KEY is not configured."
            )

    def transcribe(self, audio_file):
        with open(audio_file, "rb") as file:
            audio_data = file.read()

        response = requests.post(
            "https://api.deepgram.com/v1/listen",
            params={
                "model": "nova-3",
                "language": "fa",
                "smart_format": "true",
            },
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "audio/wav",
            },
            data=audio_data,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        return (
            data["results"]
            ["channels"][0]
            ["alternatives"][0]
            ["transcript"]
        )