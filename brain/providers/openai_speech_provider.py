import os

from openai import OpenAI

from .speech_base import SpeechToTextProvider


class OpenAISpeechProvider(SpeechToTextProvider):

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def transcribe(self, audio_file):
        with open(audio_file, "rb") as file:
            transcript = self.client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=file,
            )

        return transcript.text