
from django.db import models


class Memory(models.Model):
    MEMORY_TYPES = [
        ("fact", "Fact"),
        ("preference", "Preference"),
        ("project", "Project"),
        ("conversation", "Conversation"),
        ("goal", "Goal"),
    ]

    memory_type = models.CharField(
        max_length=20,
        choices=MEMORY_TYPES,
        default="fact",
    )

    title = models.CharField(max_length=255)

    content = models.TextField()

    importance = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Conversation(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
        default="New Conversation",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.title


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
    
    
    
class UserUsage(models.Model):
    PLAN_CHOICES = [
        ("guest", "Guest"),
        ("registered", "Registered"),
        ("premium", "Premium"),
        ("admin", "Admin"),
    ]

    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="usage",
        null=True,
        blank=True,
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="registered",
    )

    daily_messages = models.PositiveIntegerField(default=0)

    last_reset = models.DateField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.plan}"

        return f"Guest - {self.plan}"   
    
    