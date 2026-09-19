from django.contrib import admin
from .models import UserUsage


@admin.register(UserUsage)
class UserUsageAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "daily_messages",
        "last_reset",
    )

    list_filter = (
        "plan",
        "last_reset",
    )

    search_fields = (
        "user__username",
        "user__email",
    )