import os

from .test_provider import TestProvider
from .openrouter_provider import OpenRouterProvider

from .test_speech_provider import TestSpeechProvider
from .openrouter_speech_provider import OpenRouterSpeechProvider
from .one_xai_speech_provider import OneXaiSpeechProvider
from .deepgram_speech_provider import DeepgramSpeechProvider


def get_ai_provider():
    provider_name = os.getenv("AI_PROVIDER", "test")

    if provider_name == "test":
        return TestProvider()

    if provider_name == "openrouter":
        return OpenRouterProvider()

    raise ValueError(
        f"Unknown AI provider: {provider_name}"
    )


def get_speech_provider():
    provider_name = os.getenv("SPEECH_PROVIDER", "test")

    if provider_name == "test":
        return TestSpeechProvider()

    if provider_name == "openrouter":
        return OpenRouterSpeechProvider()

    if provider_name == "1xai":
        return OneXaiSpeechProvider()

    if provider_name == "deepgram":
        return DeepgramSpeechProvider()

    raise ValueError(
        f"Unknown speech provider: {provider_name}"
    )