from .base import AIProvider


class TestProvider(AIProvider):

    def generate_response(self, messages):
        return "Test Provider is working."

    def generate_json(self, prompt):
        return "{}"