from .speech_base import SpeechToTextProvider


class TestSpeechProvider(SpeechToTextProvider):

    def transcribe(self, audio_file):
        return "این یک متن آزمایشی از TestSpeechProvider است."