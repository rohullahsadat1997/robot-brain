import os

from openai import OpenAI

from .speech_base import SpeechToTextProvider


class OneXaiSpeechProvider(SpeechToTextProvider):

    def __init__(self):
        api_key = os.getenv("ONEXAI_API_KEY")

        if not api_key:
            raise ValueError(
                "ONEXAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://1xai.ir/v1",
        )

    def transcribe(self, audio_file):
        with open(audio_file, "rb") as file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=file,
                language="fa",
            )

        return transcript.text