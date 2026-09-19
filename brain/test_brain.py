from django.test import TestCase

from .models import Memory
from .services import BrainEngine


class BrainEngineTest(TestCase):

    def setUp(self):
        self.brain = BrainEngine()

    def test_remember(self):
        memory = self.brain.remember(
            title="Robot Goal",
            content="Build a general-purpose intelligent robot.",
            memory_type="goal",
            importance=10,
        )

        self.assertEqual(Memory.objects.count(), 1)
        self.assertEqual(memory.title, "Robot Goal")

    def test_recall(self):
        self.brain.remember(
            title="Low Priority",
            content="Test memory",
            importance=2,
        )

        self.brain.remember(
            title="High Priority",
            content="Important memory",
            importance=10,
        )

        memories = self.brain.recall()

        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0].title, "High Priority")

    def test_create_conversation(self):
        conversation = self.brain.create_conversation(
            title="Robot Project"
        )

        self.assertEqual(
            conversation.title,
            "Robot Project",
        )

    def test_add_message(self):
        conversation = self.brain.create_conversation(
            title="Robot Project"
        )

        self.brain.add_message(
            conversation=conversation,
            role="user",
            content="Hello Brain",
        )

        self.brain.add_message(
            conversation=conversation,
            role="assistant",
            content="Hello! I am your robot brain.",
        )

        messages = self.brain.get_conversation_messages(
            conversation
        )

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[1].role, "assistant")

    def test_get_conversation_history(self):
        conversation = self.brain.create_conversation(
            title="Robot Project"
        )

        self.brain.add_message(
            conversation=conversation,
            role="user",
            content="سلام Brain",
        )

        self.brain.add_message(
            conversation=conversation,
            role="assistant",
            content="سلام! من Brain هستم.",
        )

        history = self.brain.get_conversation_history(
            conversation
        )

        self.assertEqual(len(history), 2)

        self.assertEqual(
            history[0]["role"],
            "user",
        )

        self.assertEqual(
            history[0]["content"],
            "سلام Brain",
        )

        self.assertEqual(
            history[1]["role"],
            "assistant",
        )
        
        
    def test_generate_response_from_memory(self):
        self.brain.remember(
            title="All-Purpose Robot",
            content=(
                "We are building a long-term "
                "all-purpose robot project. "
                "The project starts with a software "
                "brain and will gradually evolve "
                "into a physical robotic system."
            ),
            memory_type="project",
            importance=10,
        )

        conversation = self.brain.create_conversation(
            title="Robot Project"
        )

        response = self.brain.generate_response(
            message="پروژه ما چیست؟",
            conversation=conversation,
        )

        self.assertTrue(response)
        self.assertIn(
            "پروژه",
            response,
        )