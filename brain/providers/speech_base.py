from abc import ABC, abstractmethod


class SpeechToTextProvider(ABC):

    @abstractmethod
    def transcribe(self, audio_file):
        pass